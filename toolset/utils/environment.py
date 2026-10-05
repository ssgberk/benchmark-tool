import hashlib
import json
import os
import platform
import re
import subprocess
import sys

import docker

BASE_IMAGE = 'ubuntu:24.04'
TEST_IMAGE_PREFIX = 'ssgberk/test.'


def _call(fn, *args):
    try:
        result = fn(*args)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _cpu_model(env, cpuinfo_path):
    launcher = (env.get('SSGBERK_HOST_CPU') or '').strip()
    if launcher:
        return launcher, 'launcher'
    try:
        with open(cpuinfo_path) as f:
            for line in f:
                if line.startswith('model name'):
                    value = line.split(':', 1)[1].strip()
                    if value:
                        return value, 'cpuinfo'
    except OSError:
        pass
    return None, None


def _docker_py_version():
    return getattr(docker, '__version__', None)


def capture(docker_client, resources, toolset_commit, env=os.environ,
            cpuinfo_path='/proc/cpuinfo'):
    """The run environment (plan "Results schema additions"). Missing
    Docker fields are None; never raises on a Docker failure."""
    info = _call(docker_client.info)
    version = _call(docker_client.version)
    cpu, source = _cpu_model(env, cpuinfo_path)
    result = {
        'cpuModel': cpu,
        'cpuModelSource': source,
        'host': {'os': env.get('SSGBERK_HOST_OS') or None},
        'docker': {
            'serverVersion': version.get('Version', info.get('ServerVersion')),
            'apiVersion': version.get('ApiVersion'),
            'operatingSystem': info.get('OperatingSystem'),
            'osType': info.get('OSType'),
            'kernelVersion': info.get('KernelVersion'),
            'architecture': info.get('Architecture'),
            'ncpu': info.get('NCPU'),
            'memTotalBytes': info.get('MemTotal'),
            'cgroupVersion': info.get('CgroupVersion'),
            'storageDriver': info.get('Driver'),
        },
        'toolset': {
            'commit': toolset_commit,
            'python': platform.python_version() or sys.version.split()[0],
            'dockerPy': _docker_py_version(),
        },
    }
    result['fingerprint'] = fingerprint(result, resources)
    return result


def fingerprint(env, resources):
    """12 hex chars naming a machine plus a resource configuration."""
    docker_info = env.get('docker') or {}
    resources = resources or {}
    obj = {
        'cpuModel': env.get('cpuModel'),
        'docker.ncpu': docker_info.get('ncpu'),
        'docker.memTotalBytes': docker_info.get('memTotalBytes'),
        'docker.kernelVersion': docker_info.get('kernelVersion'),
        'docker.operatingSystem': docker_info.get('operatingSystem'),
        'docker.architecture': docker_info.get('architecture'),
        'docker.serverVersion': docker_info.get('serverVersion'),
        'resources.cpus': resources.get('cpus'),
        'resources.memoryBytes': resources.get('memoryBytes'),
        'resources.cpuset': resources.get('cpuset'),
    }
    blob = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:12]


def _catalog_versions(fw_root):
    try:
        with open(os.path.join(fw_root, 'frameworks', 'generators.json')) as f:
            entries = json.load(f).get('generators', [])
    except (OSError, ValueError, AttributeError):
        return {}
    return {e['id']: e.get('version') for e in entries
            if isinstance(e, dict) and e.get('id') and e.get('version')}


def _dockerfile_version(fw_root, name):
    base = os.path.join(fw_root, 'frameworks')
    try:
        langs = sorted(os.listdir(base))
    except OSError:
        return None
    arg = re.compile(
        r'^\s*ARG\s+' + re.escape(re.sub(r'\W', '_', name).upper())
        + r'_VERSION=(\S+)', re.M)
    for lang in langs:
        path = os.path.join(base, lang, name, name + '.dockerfile')
        try:
            with open(path) as f:
                m = arg.search(f.read())
        except OSError:
            continue
        if m:
            return m.group(1).strip('"\'')
    return None


def _image_info(docker_client, name):
    image_id = digest = None
    try:
        image_id = docker_client.images.get(TEST_IMAGE_PREFIX + name).id
    except Exception:
        pass
    try:
        digests = docker_client.images.get(BASE_IMAGE).attrs.get('RepoDigests')
        digest = digests[0] if digests else None
    except Exception:
        pass
    return image_id, digest


def generator_versions(fw_root, names, docker_client=None):
    """Per-generator version (generators.json, else the dockerfile ARG,
    else None) plus image id and base image digest when a client is given."""
    catalog = _catalog_versions(fw_root)
    out = {}
    for name in names:
        version, source = catalog.get(name), 'generators.json'
        if version is None:
            version = _dockerfile_version(fw_root, name)
            source = 'dockerfile-arg'
        if version is None:
            source = None
        entry = {'version': version, 'versionSource': source}
        if docker_client is not None:
            image_id, digest = _image_info(docker_client, name)
            entry.update({'imageId': image_id, 'baseImage': BASE_IMAGE,
                          'baseImageDigest': digest})
        out[name] = entry
    return out


def toolset_commit(fw_root):
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'], cwd=fw_root,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None
