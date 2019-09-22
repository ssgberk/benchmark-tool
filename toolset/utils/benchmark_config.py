import os
import time

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
        self.verbose_build = args.verbose
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
            self.timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())

        self.run_test_timeout_seconds = 7200
