import pytest

from toolset.utils import resources


def test_parse_memory():
    assert resources.parse_memory("8g") == 8589934592
    assert resources.parse_memory("512m") == 512 * 1024 ** 2
    assert resources.parse_memory("64K") == 65536
    assert resources.parse_memory("1024") == 1024
    for bad in ("", "g", "8x", "-1g", "0"):
        with pytest.raises(ValueError):
            resources.parse_memory(bad)


def test_resolve_auto_cpuset():
    r = resources.resolve(4, 8589934592, "auto", 8)
    assert r == {"cpus": 4.0, "memoryBytes": 8589934592, "swap": False, "cpuset": "4-7"}
    assert resources.resolve(4, 1, "auto", 4)["cpuset"] is None
    assert resources.resolve(2.5, 1, "auto", 8)["cpuset"] == "5-7"


def test_resolve_none_and_explicit():
    assert resources.resolve(4, 1, "none", 8)["cpuset"] is None
    assert resources.resolve(4, 1, "2-5", 8)["cpuset"] == "2-5"
    assert resources.resolve(2, 1, "0,2-3", 8)["cpuset"] == "0,2-3"


def test_resolve_rejects_too_many_cpus():
    with pytest.raises(ValueError):
        resources.resolve(4, 1, "auto", 2)


@pytest.mark.parametrize("cpuset", ["2-9", "x", "5-2", "8"])
def test_resolve_rejects_bad_cpuset(cpuset):
    with pytest.raises(ValueError):
        resources.resolve(2, 1, cpuset, 8)
