import json
import os
import re
from dataclasses import dataclass, field

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suites.json")

# Must match the `-cs` choices of toolset/run-tests.py
CONTENT_SIZES = ("0.500", "5", "50", "500", "1000", "5000", "10000", "100000")
_NAME_RE = re.compile(r"^[A-Za-z0-9-]+$")


class SuiteError(ValueError):
    pass


@dataclass(frozen=True)
class Cell:
    number_of_files: int
    content_size: str


@dataclass(frozen=True)
class Suite:
    name: str
    version: int
    runs: int
    cooldown_seconds: int
    timeout_seconds: int
    ranked: bool = True
    description: str = ""
    cells: list = field(default_factory=list)


def _read(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise SuiteError("cannot read suites file %s: %s" % (path, e))
    if not isinstance(data, dict):
        raise SuiteError("suites file must be a JSON object")
    return data


def names(path=DEFAULT):
    '''Suite names defined in the suites file.'''
    return list(_read(path))


def load(name, path=DEFAULT):
    data = _read(path)
    if not _NAME_RE.match(name or "") or name not in data:
        raise SuiteError("unknown suite %r (known: %s)" % (name, ", ".join(data)))
    raw = data[name]
    try:
        cells = [Cell(int(c["numberOfFiles"]), str(c["contentSize"]))
                 for c in raw["cells"]]
        suite = Suite(
            name=name,
            version=int(raw["version"]),
            runs=int(raw["runs"]),
            cooldown_seconds=int(raw["cooldownSeconds"]),
            timeout_seconds=int(raw["timeoutSeconds"]),
            ranked=bool(raw.get("ranked", True)),
            description=str(raw.get("description", "")),
            cells=cells)
    except (KeyError, TypeError, ValueError) as e:
        raise SuiteError("invalid suite %r: %r" % (name, e))
    if suite.runs < 1:
        raise SuiteError("suite %r: runs must be >= 1" % name)
    if not cells:
        raise SuiteError("suite %r: no cells" % name)
    for c in cells:
        if c.number_of_files < 1:
            raise SuiteError("suite %r: numberOfFiles must be >= 1" % name)
        if c.content_size not in CONTENT_SIZES:
            raise SuiteError("suite %r: invalid contentSize %r" % (name, c.content_size))
    return suite


def cell_dir(profile, cell):
    return "%s/nf%d-cs%s" % (profile, cell.number_of_files, cell.content_size)


def rotate(names, cell_index):
    '''Left rotation of the sorted names by (7 * cell_index) mod len(names).'''
    ordered = sorted(names)
    if not ordered:
        return ordered
    k = (7 * cell_index) % len(ordered)
    return ordered[k:] + ordered[:k]
