import copy
import json
import os
import re
from types import SimpleNamespace

import docker

from toolset.utils import environment

FIX = os.path.join(os.path.dirname(__file__), 'fixtures')
ROOT = os.path.dirname(os.path.dirname(__file__))


def _load(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


class FakeDocker:
    def __init__(self, info, version, images=None):
        self._info, self._version, self._images = info, version, images or {}
        self.images = SimpleNamespace(get=self._get)

    def info(self):
        return self._info

    def version(self):
        return self._version

    def _get(self, name):
        if name not in self._images:
            raise docker.errors.ImageNotFound(name)
        return self._images[name]


RES = {'cpus': 4.0, 'memoryBytes': 8589934592, 'swap': False, 'cpuset': '4-7'}


def test_capture_from_fixtures():
    env = environment.capture(
        FakeDocker(_load('docker_info.json'), _load('docker_version.json')),
        RES, 'd6ea28c', env={'SSGBERK_HOST_CPU': 'Apple M3 Pro',
                             'SSGBERK_HOST_OS': 'Darwin 27.0.0 arm64'})
    assert env['docker'] == {
        'serverVersion': '29.0.1', 'apiVersion': '1.52',
        'operatingSystem': 'Docker Desktop', 'osType': 'linux',
        'kernelVersion': '6.12.5-linuxkit', 'architecture': 'aarch64',
        'ncpu': 8, 'memTotalBytes': 16764911616, 'cgroupVersion': '2',
        'storageDriver': 'overlayfs'}
    assert env['host'] == {'os': 'Darwin 27.0.0 arm64'}
    assert env['toolset']['commit'] == 'd6ea28c'
    assert env['toolset']['python'] and env['toolset']['dockerPy']
    assert re.fullmatch(r'[0-9a-f]{12}', env['fingerprint'])


def test_capture_missing_keys_are_null():
    env = environment.capture(FakeDocker({}, {}), RES, None, env={},
                              cpuinfo_path='/nonexistent')
    assert all(v is None for v in env['docker'].values())
    assert env['cpuModel'] is None and env['host']['os'] is None


def test_cpu_model_precedence(tmp_path):
    cpuinfo = tmp_path / 'cpuinfo'
    cpuinfo.write_text('processor\t: 0\nmodel name\t: Intel Xeon\n')
    d = FakeDocker({}, {})
    e = environment.capture(d, RES, None, env={'SSGBERK_HOST_CPU': 'M3'},
                            cpuinfo_path=str(cpuinfo))
    assert (e['cpuModel'], e['cpuModelSource']) == ('M3', 'launcher')
    e = environment.capture(d, RES, None, env={}, cpuinfo_path=str(cpuinfo))
    assert (e['cpuModel'], e['cpuModelSource']) == ('Intel Xeon', 'cpuinfo')
    e = environment.capture(d, RES, None, env={},
                            cpuinfo_path=str(tmp_path / 'none'))
    assert (e['cpuModel'], e['cpuModelSource']) == (None, None)


def test_fingerprint_stable_and_sensitive():
    d = FakeDocker(_load('docker_info.json'), _load('docker_version.json'))
    env = environment.capture(d, RES, 'aaa', env={})
    assert environment.fingerprint(env, RES) == env['fingerprint']
    assert environment.fingerprint(env, dict(RES, cpus=2.0)) != env['fingerprint']
    other = copy.deepcopy(env)
    other['toolset']['commit'] = 'bbb'
    assert environment.fingerprint(other, RES) == env['fingerprint']


def test_generator_versions_prefers_generators_json(tmp_path):
    fw = tmp_path / 'frameworks'
    fw.mkdir()
    (fw / 'generators.json').write_text(
        json.dumps(_load('generators.json')))
    g = environment.generator_versions(str(tmp_path), ['astro', 'nope'])
    assert g['astro'] == {'version': '7.3.5', 'versionSource': 'generators.json'}
    assert g['nope'] == {'version': None, 'versionSource': None}


def test_generator_versions_dockerfile_fallback(tmp_path):
    d = tmp_path / 'frameworks' / 'Go' / 'hugo'
    d.mkdir(parents=True)
    (d / 'hugo.dockerfile').write_text(
        'FROM ubuntu:24.04\nARG HUGO_VERSION=0.167.0\nARG HUGO_VERSION=9\n')
    g = environment.generator_versions(str(tmp_path), ['hugo'])
    assert g['hugo'] == {'version': '0.167.0', 'versionSource': 'dockerfile-arg'}


def test_generator_images_tolerate_missing():
    img = SimpleNamespace(id='sha256:abc', attrs={})
    base = SimpleNamespace(id='x', attrs={'RepoDigests': ['ubuntu@sha256:dd']})
    d = FakeDocker({}, {}, {'ssgberk/test.hugo': img, 'ubuntu:24.04': base})
    g = environment.generator_versions('/nonexistent', ['hugo', 'zola'], d)
    assert g['hugo']['imageId'] == 'sha256:abc'
    assert g['hugo']['baseImageDigest'] == 'ubuntu@sha256:dd'
    assert g['zola']['imageId'] is None
    assert g['zola']['baseImage'] == 'ubuntu:24.04'


def test_launcher_exports_host_env():
    with open(os.path.join(ROOT, 'ssgberk')) as f:
        text = f.read()
    assert '-e SSGBERK_HOST_CPU' in text and '-e SSGBERK_HOST_OS' in text
    assert 'export SSGBERK_HOST_CPU' in text
