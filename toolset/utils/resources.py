import math
import re

_UNITS = {'': 1, 'b': 1, 'k': 1024, 'm': 1024 ** 2, 'g': 1024 ** 3}


def parse_memory(text):
    '''
    Parses "8g", "512m", "64k" or a plain byte count (base 1024) into bytes.
    '''
    m = re.fullmatch(r'(\d+)\s*([kmgb]?)b?', str(text).strip().lower())
    if not m:
        raise ValueError("invalid memory size: %r" % (text,))
    value = int(m.group(1)) * _UNITS[m.group(2)]
    if value <= 0:
        raise ValueError("memory must be positive: %r" % (text,))
    return value


def _validate_cpuset(cpuset, ncpu):
    for part in cpuset.split(','):
        m = re.fullmatch(r'(\d+)(?:-(\d+))?', part.strip())
        if not m:
            raise ValueError("invalid cpuset: %r" % (cpuset,))
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) is not None else lo
        if lo > hi or hi >= ncpu:
            raise ValueError("cpuset %r is out of range for %d CPUs" % (cpuset, ncpu))


def resolve(cpus, memory, cpuset, ncpu):
    '''
    Resolves the run's container limits. cpuset is "auto" (the highest
    numbered CPUs, leaving CPU 0 to the host, when ncpu >= ceil(cpus) + 1),
    "none", or an explicit list such as "2-5".
    '''
    if cpus <= 0:
        raise ValueError("cpus must be positive")
    if cpus > ncpu:
        raise ValueError("--cpus %s exceeds the %d CPUs available to Docker" % (cpus, ncpu))
    c = math.ceil(cpus)
    if cpuset == 'auto':
        resolved = "%d-%d" % (ncpu - c, ncpu - 1) if ncpu >= c + 1 else None
    elif cpuset in (None, '', 'none'):
        resolved = None
    else:
        _validate_cpuset(cpuset, ncpu)
        resolved = cpuset
    return {'cpus': float(cpus), 'memoryBytes': int(memory), 'swap': False,
            'cpuset': resolved}
