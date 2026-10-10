'''
The untimed quality pass of one generator (spec 009 R-1..R-3, R-16).
'''
import json
import os

from toolset.quality import reduce, site
from toolset.utils.output_helper import log

# R-1: with --suite, the pass runs only in this (numberOfFiles, contentSize) cell
QUALITY_CELL = (50, 5.0)


def _cell(config):
    return int(config.number_of_files), float(config.content_size)


def eligible(config):
    if not getattr(config, 'quality', False):
        return False
    if getattr(config, 'suite_info', None) is None:
        return True
    return _cell(config) == QUALITY_CELL


def skipped(config):
    return bool(getattr(config, 'quality', False)) and not eligible(config)


def archive_path(results_dir, name):
    return os.path.join(results_dir, 'quality', name, 'site.tar')


def run_pass(docker_helper, test, results_dir):
    '''Runs the pass, writes quality.json and returns it. Never raises.'''
    out_dir = os.path.join(results_dir, 'quality', test.name)
    tar_path = archive_path(results_dir, test.name)
    try:
        output_folder, output_glob = site.generator_config(test.directory)
        if not os.path.exists(tar_path):
            raise RuntimeError('no exported output (%s)' % output_folder)
        site_dir = site.extract(tar_path, os.path.join(out_dir, 'site'))
        pages = site.resolve_pages(site_dir, output_glob)
        site_name = os.path.basename(output_folder.rstrip('/'))
        raw = docker_helper.run_quality(tar_path, site_name, pages)
        with open(os.path.join(out_dir, 'raw.json'), 'w') as f:
            json.dump(raw, f, indent=2)
        quality = reduce.build_quality(raw, site_dir, pages, output_glob)
    except Exception as e:
        quality = {'status': 'error', 'error': '%s: %s' % (type(e).__name__, e)}
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'quality.json'), 'w') as f:
            json.dump(quality, f, indent=2)
    except Exception as e:
        log("quality: could not write quality.json: %s: %s" % (type(e).__name__, e))
    try:
        if os.path.exists(tar_path):
            os.remove(tar_path)
    except Exception as e:
        log("quality: could not remove %s: %s: %s" % (tar_path, type(e).__name__, e))
    return quality
