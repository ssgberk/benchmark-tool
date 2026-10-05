import os
import subprocess
import traceback
import sys
import time
import shlex
import shutil
import numbers

from colorama import Fore
from toolset.utils.output_helper import log, FNULL
from toolset.utils.docker_helper import DockerHelper
from toolset.utils.time_logger import TimeLogger
from toolset.utils.metadata import Metadata
from toolset.utils.results import Results
from toolset.utils.audit import Audit
from toolset.utils import resources
from toolset.benchmark import noise


class Benchmarker:
    def __init__(self, config):
        '''
        Initialize the benchmarker.
        '''
        self.config = config
        self.time_logger = TimeLogger()
        self.metadata = Metadata(self)
        self.audit = Audit(self)

        # a list of all tests for this run
        self.tests = self.metadata.tests_to_run()

        self.results = Results(self)
        self.docker_helper = DockerHelper(self)

    ##########################################################################################
    # Public methods
    ##########################################################################################

    def run(self):
        '''
        This process involves setting up the client/server machines
        with any necessary change. Then going through each test,
        running their docker build and run, verifying the URLs, and
        running benchmarks against them.
        '''
        # Set when the run refuses to start (guard, usage error); a suite stops on it
        self.aborted = None

        # Generate metadata
        self.metadata.list_test_metadata()

        # Set only when another run was actually found (protocol.concurrent)
        self.config.concurrent = False
        if self.config.mode == "benchmark":
            others = self.docker_helper.other_runs(self.config.run_id)
            if others and getattr(self.config, 'allow_concurrent', False):
                log("WARNING: another SSGBerk run is active (run id: %s); "
                    "results are marked concurrent and not ranked."
                    % ", ".join(others), color=Fore.YELLOW)
                self.config.concurrent = True
            elif others:
                log("ERROR: another SSGBerk run is active (run id: %s). "
                    "Concurrent runs share CPUs and invalidate results. "
                    "Wait for it to finish or pass --allow-concurrent."
                    % ", ".join(others), color=Fore.RED)
                self.aborted = "another SSGBerk run is active: %s" % ", ".join(others)
                return True

        if self.config.mode == "benchmark":
            # Usage errors (e.g. --cpus above the host's CPUs) must surface
            # before any image is built or monitor started
            try:
                self.resolve_resources()
            except ValueError as e:
                log("ERROR: %s" % e, color=Fore.RED)
                self.aborted = str(e)
                sys.exit(1)

        any_failed = False
        # Run tests
        log("Running Tests...", border='=')

        with open(os.path.join(self.results.directory, 'benchmark.log'),
                  'w') as benchmark_log:
            for index, test in enumerate(self.tests):
                cooldown = getattr(self.config, 'cooldown_seconds', 0)
                if index > 0 and cooldown:
                    log("Cooling down %s s" % cooldown)
                    time.sleep(cooldown)
                log("Running Framework: %s" % test.name, border='-')
                with self.config.quiet_out.enable():
                    if not self.__run_test(test, benchmark_log):
                        any_failed = True
                # Load intermediate result from child process
                self.results.load()

        # Parse results
        if self.config.mode == "benchmark":
            log("Parsing Results ...", border='=')
            self.results.parse(self.tests)

        self.results.set_completion_time()
        self.results.upload()
        log(self.results.write_summary())

        return any_failed

    def stop(self, signal=None, frame=None):
        log("Shutting down (may take a moment)")
        self.docker_helper.stop()
        sys.exit(0)

    ##########################################################################################
    # Private methods
    ##########################################################################################

    def __exit_test(self, success, prefix, file, message=None):
        if message:
            log(message,
                prefix=prefix,
                file=file,
                color=Fore.RED if success else '')
        self.time_logger.log_test_end(log_prefix=prefix, file=file)
        return success

    def __run_test(self, test, benchmark_log):
        '''
        Runs the given test, verifies that the webapp is accepting requests,
        optionally benchmarks the webapp, and ultimately stops all services
        started for this test.
        '''

        log_prefix = "%s: " % test.name
        # Start timing the total test duration
        self.time_logger.mark_test_start()

        if self.config.mode == "benchmark":
            log("Benchmarking %s" % test.name,
                file=benchmark_log,
                border='-')

        # If the test is in the excludes list, we skip it
        if self.config.exclude and test.name in self.config.exclude:
            message = "Test {name} has been added to the excludes list. Skipping.".format(
                name=test.name)
            self.results.write_intermediate(test.name, message)
            return self.__exit_test(
                success=False,
                message=message,
                prefix=log_prefix,
                file=benchmark_log)

        profile = getattr(self.config, 'profile', 'core')
        if self.config.mode == "benchmark" and not test.supports_profile(profile):
            # Same series semantics as SSGBERK_PROFILE_UNSUPPORTED: not run, not a failure
            message = "Test {name} does not declare profile {profile}. Skipping.".format(
                name=test.name, profile=profile)
            for test_type in test.runTests:
                self.results.report_benchmark_results(test, test_type, [], unsupported=True)
            self.results.write_intermediate(test.name, message)
            log(message, prefix=log_prefix, file=benchmark_log)
            return self.__exit_test(success=True, prefix=log_prefix, file=benchmark_log)

        try:
            # Start webapp
            container = test.start()
            self.time_logger.mark_test_starting()
            if container is None:
                message = "ERROR: Problem starting {name}".format(
                    name=test.name)
                self.results.write_intermediate(test.name, message)
                return self.__exit_test(
                    success=False,
                    message=message,
                    prefix=log_prefix,
                    file=benchmark_log)

            # Debug mode blocks execution here until ctrl+c
            if self.config.mode == "debug":
                log("Entering debug mode. Server has started. CTRL-c to stop.",
                    prefix=log_prefix,
                    file=benchmark_log,
                    color=Fore.YELLOW)
                while True:
                    time.sleep(1)

            # Benchmark this test
            benchmarked = True
            if self.config.mode == "benchmark":
                self.time_logger.mark_benchmarking_start()
                benchmarked = self.__benchmark(test, benchmark_log)
                self.time_logger.log_benchmarking_end(
                    log_prefix=log_prefix, file=benchmark_log)

            # Log test timing stats
            self.time_logger.log_build_flush(benchmark_log)

            # Save results thus far into the latest results directory
            self.results.write_intermediate(test.name,
                                            time.strftime(
                                                "%Y%m%d%H%M%S",
                                                time.localtime()))

            # Upload the results thus far to another server (optional)
            self.results.upload()

        except Exception as e:
            tb = traceback.format_exc()
            self.results.write_intermediate(test.name,
                                            "error during test: " + str(e))
            log(tb, prefix=log_prefix, file=benchmark_log)
            return self.__exit_test(
                success=False,
                message="Error during test: %s" % test.name,
                prefix=log_prefix,
                file=benchmark_log)
        finally:
            self.docker_helper.stop()

        # A build that failed, was nonconformant, timed out or ran out of
        # memory fails the run; an unsupported profile does not
        return self.__exit_test(
            success=benchmarked, prefix=log_prefix, file=benchmark_log)

    def __benchmark(self, framework_test, benchmark_log):
        '''
        Runs the benchmark for each type of test that it implements. Returns
        False when any type ended in failed (unsupported is not a failure).
        '''

        def benchmark_type(test_type):
            log("BENCHMARKING %s ... " % test_type.upper(), file=benchmark_log, border='*')

            outcome = {'status': 'ok', 'exitCode': None}
            test = framework_test.runTests[test_type]
            raw_file = self.results.get_raw_file(framework_test.name,
                                                 test_type)
            if not os.path.exists(raw_file):
                # Open to create the empty file
                with open(raw_file, 'w'):
                    pass

            if not test.failed:
                script = self.config.types[test_type].get_script_name()
                script_variables = self.config.types[test_type].get_script_variables()

                # Resource usage metrics collection, stopped even if the run raises
                self.__begin_logging(framework_test, test_type)
                try:
                    outcome = self.docker_helper.benchmark(
                        framework_test, script, script_variables, raw_file,
                        self.resolve_resources(), self.config.run_test_timeout_seconds)
                finally:
                    self.__end_logging()

            results = self.results.parse_test(framework_test, test_type)
            log("Benchmark results:", file=benchmark_log)

            if outcome['status'] == 'ok' and results['results'] and not test.failed:
                results, outcome = self.__noise_control(
                    framework_test, test_type, script, script_variables,
                    raw_file, results, benchmark_log)

            if outcome['status'] != 'ok':
                # timeout/oom: whatever was printed is not a result
                results['results'] = []
                results['unsupported'] = False
                results['failureReason'] = outcome['status']

            self.results.report_benchmark_results(framework_test, test_type, results['results'],
                                                  results.get('unsupported', False),
                                                  results.get('failureReason'))
            log("Complete", file=benchmark_log)
            return bool(results['results']) or bool(results.get('unsupported', False))

        ok = True
        for test_type in framework_test.runTests:
            if not benchmark_type(test_type):
                ok = False
        return ok

    def __noise_control(self, framework_test, test_type, script,
                        script_variables, raw_file, results, benchmark_log):
        '''
        R-21: one re-run with more runs when the CV is high. Only successful
        attempts are re-run; timeout/oom are never retried (R-19).
        '''
        runs = int(script_variables.get('min_runs') or 0)
        first = results['results'][0]
        first['minRuns'] = runs
        ok = {'status': 'ok', 'exitCode': None}
        if not noise.needs_rerun(first, runs):
            results['results'] = [self.__v1_min_runs(noise.finalize([first]))]
            return results, ok
        rerun = noise.rerun_runs(runs)
        log("CV %.3f above %.2f; re-running with %d runs" % (
            first['cv'], noise.CV_THRESHOLD, rerun), file=benchmark_log)
        shutil.copyfile(raw_file, os.path.join(
            os.path.dirname(raw_file), 'raw.attempt1.txt'))
        variables = dict(script_variables, min_runs=rerun)
        self.__begin_logging(framework_test, test_type)
        try:
            outcome = self.docker_helper.benchmark(
                framework_test, script, variables, raw_file,
                self.resolve_resources(), self.config.run_test_timeout_seconds)
        finally:
            self.__end_logging()
        second = self.results.parse_test(framework_test, test_type)
        if outcome['status'] == 'ok' and second['results']:
            second['results'][0]['minRuns'] = rerun
            second['results'] = [self.__v1_min_runs(
                noise.finalize([first, second['results'][0]]))]
        # else: the last attempt is the result (R-21), reported as its failure
        return second, outcome

    @staticmethod
    def __v1_min_runs(result):
        '''rawData minRuns stays a string, as in schema v1 (R-28); attempts keep ints.'''
        if result.get('minRuns') is not None:
            result['minRuns'] = str(result['minRuns'])
        return result

    def resolve_resources(self):
        '''
        Resolves --cpus/--memory/--cpuset against the Docker host once; the
        same values apply to every container of the run and go to results.
        '''
        if self.config.resources is None:
            ncpu = self.docker_helper.server.info().get('NCPU') or os.cpu_count()
            self.config.resources = resources.resolve(
                self.config.cpus, self.config.memory, self.config.cpuset, ncpu)
        return self.config.resources

    def __begin_logging(self, framework_test, test_type):
        '''
        Starts a thread to monitor the resource usage, to be synced with the
        client's time.
        TODO: MySQL and InnoDB are possible. Figure out how to implement them.
        '''
        output_file = "{file_name}".format(
            file_name=self.results.get_stats_file(framework_test.name,
                                                  test_type))
        dool_string = "dool -Tafilmprs --aio --fs --ipc --lock --socket --tcp \
                                      --raw --udp --unix --vm --disk-util \
                                      --rpc --rpcd --output {output_file}".format(
            output_file=output_file)
        cmd = shlex.split(dool_string)
        self.subprocess_handle = subprocess.Popen(
            cmd, stdout=FNULL, stderr=subprocess.STDOUT)

    def __end_logging(self):
        '''
        Stops the logger thread and blocks until shutdown is complete.
        '''
        self.subprocess_handle.terminate()
        self.subprocess_handle.communicate()
