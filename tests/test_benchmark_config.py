import os
import types

from toolset.utils.benchmark_config import BenchmarkConfig


def _args(**kw):
    base = dict(
        type=['datarate'], duration=15, exclude=None, quiet=True,
        server_host='ssgberk-server', audit=False, new=False, clean=False,
        mode='benchmark', list_tests=False, number_of_files='10',
        content_size='0.5', min_runs='1', verbose=False, parse=None,
        results_environment='x', results_name='n', results_upload_uri=None,
        test=None, test_dir=None, test_lang=None, network_mode=None)
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_run_id_unique_per_config(monkeypatch, tmp_path):
    monkeypatch.setenv('FWROOT', str(tmp_path))
    a, b = BenchmarkConfig(_args()), BenchmarkConfig(_args())
    assert a.run_id and a.run_id != b.run_id


def test_timestamp_dir_unique_when_taken(monkeypatch, tmp_path):
    monkeypatch.setenv('FWROOT', str(tmp_path))
    monkeypatch.setattr('time.strftime', lambda *a, **k: '20261004000000')
    a, b, c = (BenchmarkConfig(_args()) for _ in range(3))
    assert [a.timestamp, b.timestamp, c.timestamp] == [
        '20261004000000', '20261004000000-2', '20261004000000-3']
    for cfg in (a, b, c):
        assert os.path.isdir(os.path.join(cfg.results_root, cfg.timestamp))


def test_parse_keeps_timestamp(monkeypatch, tmp_path):
    monkeypatch.setenv('FWROOT', str(tmp_path))
    (tmp_path / 'results' / '2026').mkdir(parents=True)
    cfg = BenchmarkConfig(_args(parse='2026'))
    assert cfg.timestamp == '2026'
