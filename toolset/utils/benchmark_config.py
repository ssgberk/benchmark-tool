import copy
import os
import time
import uuid

from toolset.benchmark.test_types import *
from toolset.utils.output_helper import QuietOutputStream


class BenchmarkConfig:
    def __init__(self, args):
        '''
        Configures this BenchmarkConfig given the arguments provided.
        '''

        # Map type strings to their objects
        types = dict()
        types['datarate'] = DatarateTestType(self)
        #types['cached_query'] = CachedQueryTestType(self)

        # Turn type into a map instead of a list of strings
        if 'all' in args.type:
            self.types = types
        else:
            self.types = {t: types[t] for t in args.type}

        # Identifies this run (docker labels, results uuid)
        self.run_id = str(uuid.uuid4())

        self.duration = args.duration
        self.exclude = args.exclude
        self.quiet = args.quiet
        self.server_host = args.server_host
        self.audit = args.audit
        self.new = args.new
        self.clean = args.clean
        self.mode = args.mode
        self.list_tests = args.list_tests
        self.number_of_files = args.number_of_files
        self.content_size = args.content_size
        self.min_runs = args.min_runs
        self.profile = getattr(args, 'profile', 'core')
        self.require_conformance = bool(getattr(args, 'require_conformance', False))
        self.verbose_build = args.verbose
        self.no_cache = bool(getattr(args, 'no_cache', False))
        self.quality = bool(getattr(args, 'quality', False))
        self.cpus = getattr(args, 'cpus', 4.0)
        self.memory = getattr(args, 'memory', 8 * 1024 ** 3)
        self.cpuset = getattr(args, 'cpuset', 'auto')
        # Resolved lazily against the Docker host (Benchmarker.resolve_resources)
        self.resources = None
        self.parse = args.parse
        self.results_environment = args.results_environment
        self.results_name = args.results_name
        self.results_upload_uri = args.results_upload_uri
        self.test = args.test
        self.test_dir = args.test_dir
        self.test_lang = args.test_lang
        self.network_mode = args.network_mode
        self.server_docker_host = None
        self.network = None

        if self.network_mode is None:
            self.network = 'ssgberk'
            self.server_docker_host = "unix://var/run/docker.sock"
        else:
            self.network = None
            # The only other supported network_mode is 'host', and that means
            # that we have a tri-machine setup, so we need to use tcp to
            # communicate with docker.
            self.server_docker_host = "tcp://%s:2375" % self.server_host

        self.quiet_out = QuietOutputStream(self.quiet)

        self.start_time = time.time()

        # Remember directories
        self.fw_root = os.getenv('FWROOT')
        self.lang_root = os.path.join(self.fw_root, "frameworks")
        self.results_root = os.path.join(self.fw_root, "results")
        self.scaffold_root = os.path.join(self.fw_root, "toolset", "scaffolding")

        if hasattr(self, 'parse') and self.parse is not None:
            self.timestamp = self.parse
        else:
            self.timestamp = self.__claim_results_dir(
                time.strftime("%Y%m%d%H%M%S", time.localtime()))

        self.run_test_timeout_seconds = 7200
        self.cooldown_seconds = 0
        self.allow_concurrent = bool(getattr(args, 'allow_concurrent', False))

    def __claim_results_dir(self, base):
        '''
        Atomically creates results/<base>, appending -2, -3, ... when it
        already exists (e.g. two runs started in the same second).
        '''
        os.makedirs(self.results_root, exist_ok=True)
        candidate, n = base, 1
        while True:
            try:
                os.mkdir(os.path.join(self.results_root, candidate))
                return candidate
            except FileExistsError:
                n += 1
                candidate = "%s-%d" % (base, n)

    def for_cell(self, suite, cell, cell_index):
        '''
        Returns a copy of this config for one cell of a suite. Results go to
        results/<ts>/<profile>/nf<nf>-cs<cs>/ (the timestamp gains a subdir).
        '''
        from toolset.benchmark import suites
        base = self.suite_timestamp if hasattr(self, 'suite_timestamp') else self.timestamp
        cfg = copy.copy(self)
        cfg.suite_timestamp = base
        cfg.suite = suite.name
        cfg.cell_index = cell_index
        cfg.suite_info = {
            'name': suite.name, 'version': suite.version,
            'cellIndex': cell_index, 'cellCount': len(suite.cells),
            'runs': suite.runs, 'ranked': suite.ranked,
        }
        cfg.number_of_files = str(cell.number_of_files)
        cfg.content_size = cell.content_size
        cfg.min_runs = str(suite.runs)
        cfg.run_test_timeout_seconds = suite.timeout_seconds
        cfg.cooldown_seconds = suite.cooldown_seconds
        cfg.timestamp = "%s/%s" % (base, suites.cell_dir(self.profile, cell))
        # test types keep a reference to their config
        cfg.types = {k: type(v)(cfg) for k, v in self.types.items()}
        return cfg
