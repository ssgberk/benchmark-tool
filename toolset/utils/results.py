import os
import subprocess
import uuid
import time
import json
import requests
import threading
import re
import csv
from datetime import datetime

from toolset.utils.output_helper import log
from toolset.utils import summary, environment


RESULT_BEGIN = 'SSGBERK_RESULT_BEGIN'
RESULT_END = 'SSGBERK_RESULT_END'
PROFILE_UNSUPPORTED = 'SSGBERK_PROFILE_UNSUPPORTED'

_BOL = r'^[ \t]*'

# results.json schemaVersion. Readers treat every key added since version 1
# as optional; an absent schemaVersion means 1.
SCHEMA_VERSION = 2

PROTOCOL_REASON = 'protocol: verification markers missing before STARTTIME'

# Run-level keys a --parse keeps from the stored results.json: they describe
# how the run was made, which raw.txt cannot tell.
STORED_RUN_KEYS = ('suite', 'profile', 'resources', 'protocol', 'environment',
                   'generators', 'imageBuild')
# Per-result keys a --parse keeps from the stored result.
STORED_RESULT_KEYS = ('noisy', 'attempts', 'resources')
# Failure reasons decided by the container outcome, not by raw.txt.
OUTCOME_REASONS = ('timeout', 'oom')


def _first_line(marker, text):
    m = re.search(_BOL + marker + r'.*$', text, re.M)
    return m.group(0).strip() if m else None


def classify_build_output(text, require_conformance=False):
    """
    Returns (status, reason) for a raw build.sh output. Status is one of
    nonconformant, failed, unsupported or ok. reason is the failure line
    (prefixed 'nonconformant: ' for conformance failures), a protocol
    message, or None. With require_conformance a missing
    SSGBERK_CONFORMANCE_OK is nonconformant (reason: the first
    SSGBERK_CONFORMANCE_PENDING line, if any); otherwise it is tolerated
    (the result is recorded as conformance 'unchecked'), PENDING included.
    """
    line = _first_line('SSGBERK_CONFORMANCE_FAIL', text)
    if line:
        return 'nonconformant', 'nonconformant: ' + line
    line = _first_line('SSGBERK_VERIFY_FAIL', text)
    if line:
        return 'failed', line
    has_result = RESULT_BEGIN in text
    if re.search(_BOL + PROFILE_UNSUPPORTED, text, re.M) and not has_result:
        return 'unsupported', None
    start = re.search(_BOL + r'STARTTIME ', text, re.M)
    if not start:
        # Nothing was timed: with a result block that is a protocol breach.
        return 'failed', (PROTOCOL_REASON if has_result else None)
    verify = re.search(_BOL + r'SSGBERK_VERIFY_OK', text, re.M)
    if not verify or verify.start() > start.start():
        return 'failed', PROTOCOL_REASON
    conformance = re.search(_BOL + r'SSGBERK_CONFORMANCE_OK', text, re.M)
    if conformance:
        if conformance.start() > start.start():
            return 'failed', PROTOCOL_REASON
    else:
        # SF 006 report mode: PENDING (no OK) is informational and timing
        # follows; it is a missing OK, not a protocol breach.
        pending = _first_line('SSGBERK_CONFORMANCE_PENDING', text)
        if require_conformance:
            return 'nonconformant', 'nonconformant: ' + (
                pending or 'missing SSGBERK_CONFORMANCE_OK')
        if re.search(_BOL + r'SSGBERK_CONFORMANCE_(?!PENDING)', text, re.M):
            return 'failed', PROTOCOL_REASON
    # else: tolerated (conformance 'unchecked') until SF 006 Task 27 flips
    # --require-conformance on.
    return 'ok', None


def _number(value):
    """A hyperfine scalar, or the mean of a per-run list; None if absent."""
    if isinstance(value, list):
        value = [v for v in value if isinstance(v, (int, float))]
        return sum(value) / len(value) if value else None
    return value if isinstance(value, (int, float)) else None


def _io_marker(name, text):
    m = re.search(_BOL + name + r' files=(\d+) bytes=(\d+)', text, re.M)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def parse_build_output(text, number_of_files, content_size, min_runs,
                       require_conformance=False):
    """
    Extracts the hyperfine JSON printed by build.sh between the result
    markers plus the SSGBERK_INPUT/OUTPUT/CONFORMANCE_OK values. Returns []
    when the build did not classify as ok or produced no parseable result.
    Optional fields missing from old outputs are None.
    """
    status, _ = classify_build_output(text, require_conformance)
    if status != 'ok':
        return []
    start = text.find(RESULT_BEGIN)
    end = text.find(RESULT_END, start)
    if start == -1 or end == -1:
        return []
    try:
        result = json.loads(text[start + len(RESULT_BEGIN):end])['results'][0]
    except (ValueError, KeyError, IndexError, TypeError):
        return []
    start_time = re.search(_BOL + r'STARTTIME (\d+)', text, re.M)
    end_time = re.search(_BOL + r'ENDTIME (\d+)', text, re.M)
    mean = result.get('mean')
    median = result.get('median')
    stddev = result.get('stddev')
    user = _number(result.get('user'))
    system = _number(result.get('system'))
    memory = result.get('memory_usage_byte')
    if isinstance(memory, (int, float)):
        memory = [memory]
    memory = [m for m in memory if isinstance(m, (int, float))] if isinstance(memory, list) else []
    in_files, in_bytes = _io_marker('SSGBERK_INPUT', text)
    out_files, out_bytes = _io_marker('SSGBERK_OUTPUT', text)
    features = None
    m = re.search(_BOL + r'SSGBERK_CONFORMANCE_OK\b.*?\bfeatures=(\S*)', text, re.M)
    if m:
        features = [f for f in m.group(1).split(',') if f and f != '-']
    try:
        files = float(number_of_files)
    except (TypeError, ValueError):
        files = None
    have_cpu = user is not None and system is not None and mean
    return [{
        'mean': mean,
        'stddev': stddev,
        'median': median,
        'min': result.get('min'),
        'max': result.get('max'),
        'times': result.get('times', []),
        'numberOfFiles': number_of_files,
        'contentSize': content_size,
        'minRuns': min_runs,
        'startTime': int(start_time.group(1)) if start_time else None,
        'endTime': int(end_time.group(1)) if end_time else None,
        'user': user,
        'system': system,
        'cpuUtilization': round((user + system) / mean, 3) if have_cpu else None,
        'memoryUsageBytes': memory or None,
        'peakRssBytes': max(memory) if memory else None,
        'inputFiles': in_files,
        'inputBytes': in_bytes,
        'outputFiles': out_files,
        'outputBytes': out_bytes,
        'cv': stddev / mean if stddev is not None and mean else None,
        'postsPerSecond': files / median if files is not None and median else None,
        'inputMBPerSecond': in_bytes / 1e6 / median if in_bytes is not None and median else None,
        'features': features,
        'conformance': 'ok' if re.search(
            _BOL + r'SSGBERK_CONFORMANCE_OK', text, re.M) else 'unchecked',
        'status': 'ok',
    }]


class Results:
    def __init__(self, benchmarker):
        '''
        Constructor
        '''
        self.benchmarker = benchmarker
        self.config = benchmarker.config
        self.directory = os.path.join(self.config.results_root,
                                      self.config.timestamp)
        try:
            os.makedirs(self.directory)
        except OSError:
            pass
        self.file = os.path.join(self.directory, "results.json")

        self.uuid = getattr(self.config, 'run_id', None) or str(uuid.uuid4())
        self.name = datetime.now().strftime(self.config.results_name)
        self.environmentDescription = self.config.results_environment
        try:
            self.git = dict()
            self.git['commitId'] = self.__get_git_commit_id()
            self.git['repositoryUrl'] = self.__get_git_repository_url()
            self.git['branchName'] = self.__get_git_branch_name()
        except Exception:
            #Could not read local git repository, which is fine.
            self.git = None
        self.startTime = int(round(time.time() * 1000))
        self.completionTime = None
        self.numberOfFiles = self.config.number_of_files
        self.contentSize = self.config.content_size
        self.minRuns = self.config.min_runs
        self.profile = getattr(self.config, 'profile', 'core')
        self.verboseBuild = self.config.verbose_build
        self.frameworks = [t.name for t in benchmarker.tests]
        self.duration = self.config.duration
        self.rawData = dict()
        self.rawData['datarate'] = dict()
        self.completed = dict()
        self.succeeded = dict()
        self.succeeded['datarate'] = []
        self.failed = dict()
        self.failed['datarate'] = []
        self.unsupported = dict()
        self.unsupported['datarate'] = []
        self.failureReasons = dict()

    #############################################################################
    # PUBLIC FUNCTIONS
    #############################################################################

    def parse(self, tests):
        '''
        Ensures that the system has all necessary software to run
        the tests. This does not include that software for the individual
        test, but covers software such as curl and weighttp that
        are needed.
        '''
        # Run the method to get the commmit count of each framework.
        self.__count_commits()
        # Call the method which counts the sloc for each framework
        self.__count_sloc()

        # Time to create parsed files
        # Aggregate JSON file
        with open(self.file, "w") as f:
            f.write(json.dumps(self.__to_jsonable(), indent=2))
        self.write_summary()

    def write_summary(self):
        '''
        Writes summary.csv and summary.md next to results.json and returns
        the Markdown text ('' on error).
        '''
        try:
            data = self.__to_jsonable()
            data['excluded'] = list(self.config.exclude or [])
            languages = {t.name: getattr(t, 'language', '') for t in self.benchmarker.tests}
            rows = summary.build_rows(data, languages)
            markdown = summary.to_markdown(rows, data)
            with open(os.path.join(self.directory, 'summary.csv'), 'w', newline='') as f:
                f.write(summary.to_csv(rows))
            with open(os.path.join(self.directory, 'summary.md'), 'w') as f:
                f.write(markdown)
            return markdown
        except Exception as e:
            log("Error writing summary: %s" % e)
            return ''

    def reparse(self, tests):
        '''
        --parse: rebuilds results.json from the raw.txt files of this
        directory. Everything the stored results.json records about the run
        (suite, profile, resources, protocol, environment, generators,
        imageBuild, per-result noisy/attempts/resources, numberOfFiles,
        contentSize, minRuns) is kept; only the measured fields are refreshed.
        '''
        try:
            with open(self.file) as f:
                stored = json.load(f)
        except (ValueError, IOError):
            stored = {}
        if not isinstance(stored, dict):
            stored = {}
        self.__dict__.update(stored)
        self._stored_run = {k: stored[k] for k in STORED_RUN_KEYS if k in stored}
        self._stored_results = {}
        for name, entries in ((stored.get('rawData') or {}).get('datarate') or {}).items():
            if isinstance(entries, list) and entries and isinstance(entries[0], dict):
                self._stored_results[name] = entries[0]
        stored_reasons = dict(stored.get('failureReasons') or {})
        stored_lists = {key: list((stored.get(key) or {}).get('datarate') or [])
                        for key in ('succeeded', 'failed', 'unsupported')}
        self.rawData = {'datarate': {}}
        self.succeeded = {'datarate': []}
        self.failed = {'datarate': []}
        self.unsupported = {'datarate': []}
        self.failureReasons = {}
        for test in tests:
            if not any(os.path.exists(os.path.join(self.directory, test.name, t, 'raw.txt'))
                       for t in test.runTests):
                # never benchmarked (profile skip, start failure): nothing to
                # re-parse, so the stored outcome stands
                self.__keep_stored_outcome(test.name, stored_lists, stored_reasons)
                continue
            self.parse_all(test)
            reason = stored_reasons.get(test.name)
            if reason in OUTCOME_REASONS and test.name not in self.rawData['datarate']:
                # a timeout/oom left partial output: keep the recorded outcome
                self.failureReasons[test.name] = reason
                if test.name not in self.failed['datarate']:
                    self.failed['datarate'].append(test.name)
                if test.name in self.unsupported['datarate']:
                    self.unsupported['datarate'].remove(test.name)
            elif reason and test.name in self.failed['datarate'] \
                    and test.name not in self.failureReasons:
                self.failureReasons[test.name] = reason
        self.parse(tests)

    def __keep_stored_outcome(self, name, stored_lists, stored_reasons):
        for key, names in stored_lists.items():
            if name in names and name not in getattr(self, key)['datarate']:
                getattr(self, key)['datarate'].append(name)
        if name in stored_lists['succeeded'] and name in self._stored_results:
            self.rawData['datarate'][name] = [self._stored_results[name]]
        if name in stored_reasons:
            self.failureReasons[name] = stored_reasons[name]

    def __cell_values(self, test_name):
        '''numberOfFiles, contentSize, minRuns for parsing test_name's raw.txt.'''
        stored_results = getattr(self, '_stored_results', None)
        if stored_results is None:  # a live run: the config is the truth
            return (self.config.number_of_files, self.config.content_size,
                    self.config.min_runs)
        stored = stored_results.get(test_name) or {}
        return (stored.get('numberOfFiles', self.numberOfFiles),
                stored.get('contentSize', self.contentSize),
                str(stored.get('minRuns', getattr(self, 'minRuns', self.config.min_runs))))

    def parse_test(self, framework_test, test_type):
        '''
        Parses the given test and test_type from the raw_file.
        '''
        raw_file = self.get_raw_file(framework_test.name, test_type)
        text = ''
        if os.path.exists(raw_file):
            with open(raw_file, encoding='utf-8', errors='replace') as raw_data:
                text = raw_data.read()
        require = bool(getattr(self.config, 'require_conformance', False))
        number_of_files, content_size, min_runs = self.__cell_values(framework_test.name)
        results = {'results': parse_build_output(
            text, number_of_files, content_size, min_runs, require)}
        stored = getattr(self, '_stored_results', None)
        if stored and results['results'] and framework_test.name in stored:
            for key in STORED_RESULT_KEYS:
                if key in stored[framework_test.name]:
                    results['results'][0][key] = stored[framework_test.name][key]
        status, reason = classify_build_output(text, require)
        results['status'] = status
        results['failureReason'] = reason
        results['unsupported'] = status == 'unsupported' and not results['results']

        stats = []
        stats_path = self.get_stats_file(framework_test.name, test_type)
        has_stats = os.path.exists(stats_path) and os.path.getsize(stats_path) > 0
        for r in results['results']:
            if has_stats and r['startTime'] and r['endTime']:
                stats.append(self.__parse_stats(framework_test, test_type,
                                                r['startTime'], r['endTime'], 1))
        with open(stats_path + ".json", "w") as stats_file:
            json.dump(stats, stats_file, indent=2)

        return results

    def parse_all(self, framework_test):
        '''
        Method meant to be run for a given timestamp
        '''
        for test_type in framework_test.runTests:
            if os.path.exists(
                    self.get_raw_file(framework_test.name, test_type)):
                results = self.parse_test(framework_test, test_type)
                self.report_benchmark_results(framework_test, test_type,
                                              results['results'],
                                              results.get('unsupported', False),
                                              results.get('failureReason'))

    def write_intermediate(self, test_name, status_message):
        '''
        Writes the intermediate results for the given test_name and status_message
        '''
        self.completed[test_name] = status_message
        self.__write_results()

    def set_completion_time(self):
        '''
        Sets the completionTime for these results and writes the results
        '''
        self.completionTime = int(round(time.time() * 1000))
        self.__write_results()
        self.write_summary()

    def upload(self):
        '''
        Attempts to upload the results.json to the configured results_upload_uri
        '''
        if self.config.results_upload_uri is not None:
            try:
                requests.post(
                    self.config.results_upload_uri,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(self.__to_jsonable(), indent=2),
                    timeout=300)
            except Exception:
                log("Error uploading results.json")

    def load(self):
        '''
        Load the results.json file
        '''
        try:
            with open(self.file) as f:
                self.__dict__.update(json.load(f))
        except (ValueError, IOError):
            pass

    def get_raw_file(self, test_name, test_type):
        '''
        Returns the output file for this test_name and test_type
        Example: fw_root/results/timestamp/test_type/test_name/raw.txt
        '''
        path = os.path.join(self.directory, test_name, test_type, "raw.txt")
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
        return path

    def get_stats_file(self, test_name, test_type):
        '''
        Returns the stats file name for this test_name and
        Example: fw_root/results/timestamp/test_type/test_name/stats.txt
        '''
        path = os.path.join(self.directory, test_name, test_type, "stats.txt")
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
        return path

    def report_benchmark_results(self, framework_test, test_type, results,
                                 unsupported=False, failure_reason=None):
        '''
        Used by FrameworkTest to add benchmark data to this

        TODO: Technically this is an IPC violation - we are accessing
        the parent process' memory from the child process
        '''
        if test_type not in self.rawData.keys():
            self.rawData[test_type] = dict()

        if unsupported and not results:
            # Not a failure: the generator does not support this profile.
            self.unsupported.setdefault(test_type, [])
            if framework_test.name not in self.unsupported[test_type]:
                self.unsupported[test_type].append(framework_test.name)
        # If results has a size from the parse, then it succeeded.
        elif results:
            resources = getattr(self.config, 'resources', None)
            if resources is not None and isinstance(results[0], dict):
                results[0]['resources'] = dict(resources)
            self.rawData[test_type][framework_test.name] = results

            # This may already be set for single-tests
            if framework_test.name not in self.succeeded[test_type]:
                self.succeeded[test_type].append(framework_test.name)
        else:
            # This may already be set for single-tests
            if framework_test.name not in self.failed[test_type]:
                self.failed[test_type].append(framework_test.name)
            if failure_reason:
                self.failureReasons[framework_test.name] = failure_reason

    #############################################################################
    # PRIVATE FUNCTIONS
    #############################################################################

    def __to_jsonable(self):
        '''
        Returns a dict suitable for jsonification
        '''
        toRet = dict()

        toRet['schemaVersion'] = SCHEMA_VERSION
        toRet['uuid'] = self.uuid
        toRet['name'] = self.name
        toRet['environmentDescription'] = self.environmentDescription
        toRet['git'] = self.git
        toRet['startTime'] = self.startTime
        toRet['completionTime'] = self.completionTime
        toRet['contentSize'] = self.contentSize
        toRet['numberOfFiles'] = self.numberOfFiles
        toRet['frameworks'] = self.frameworks
        toRet['duration'] = self.duration
        toRet['rawData'] = self.rawData
        toRet['completed'] = self.completed
        toRet['succeeded'] = self.succeeded
        toRet['failed'] = self.failed
        toRet['suite'] = getattr(self.config, 'suite_info', None)
        toRet['profile'] = self.profile
        toRet['unsupported'] = self.unsupported
        toRet['failureReasons'] = self.failureReasons
        toRet['resources'] = getattr(self.config, 'resources', None)
        toRet['protocol'] = self.__protocol()
        toRet['environment'] = self.__environment()
        toRet['generators'] = self.__generators()
        toRet['imageBuild'] = self.__image_build()
        # --parse: what the stored run recorded wins over this process's config
        toRet.update(getattr(self, '_stored_run', None) or {})

        return toRet

    def __docker_client(self):
        helper = getattr(self.benchmarker, 'docker_helper', None)
        return getattr(helper, 'server', None)

    def __environment(self):
        if getattr(self, '_environment', None) is None:
            client = self.__docker_client()
            if client is None:
                return None
            fw_root = getattr(self.config, 'fw_root', None)
            self._environment = environment.capture(
                client, getattr(self.config, 'resources', None),
                environment.toolset_commit(fw_root) if fw_root else None)
        return self._environment

    def __generators(self):
        fw_root = getattr(self.config, 'fw_root', None)
        if not fw_root:
            return None
        return environment.generator_versions(
            fw_root, self.frameworks, self.__docker_client())

    def __image_build(self):
        return {t.name: t.image_build
                for t in getattr(self.benchmarker, 'tests', [])
                if getattr(t, 'image_build', None)}

    def __protocol(self):
        # concurrent: another run was found at start; allowConcurrent: the flag
        concurrent = bool(getattr(self.config, 'concurrent', False))
        return {
            'coldRebuild': True,
            'warmupBuilds': 1,
            'sequential': not concurrent,
            'concurrent': concurrent,
            'allowConcurrent': bool(getattr(self.config, 'allow_concurrent', False)),
            'cooldownSeconds': getattr(self.config, 'cooldown_seconds', 0),
            'timeoutSeconds': getattr(self.config, 'run_test_timeout_seconds', 7200),
            'cvThreshold': 0.10,
        }

    def __write_results(self):
        try:
            with open(self.file, 'w') as f:
                f.write(json.dumps(self.__to_jsonable(), indent=2))
        except IOError:
            log("Error writing results.json")

    def __count_sloc(self):
        '''
        Counts the significant lines of code for all tests and stores in results.
        '''
        frameworks = self.benchmarker.metadata.gather_frameworks(
            self.config.test, self.config.exclude)

        framework_to_count = {}

        for framework, testlist in frameworks.items():

            wd = testlist[0].directory

            # Find the last instance of the word 'code' in the yaml output. This
            # should be the line count for the sum of all listed files or just
            # the line count for the last file in the case where there's only
            # one file listed.
            command = "cloc --yaml --follow-links . | grep code | tail -1 | cut -d: -f 2"

            log("Running \"%s\" (cwd=%s)" % (command, wd))
            try:
                line_count = int(subprocess.check_output(command, cwd=wd, shell=True))
            except (subprocess.CalledProcessError, ValueError) as e:
                log("Unable to count lines of code for %s due to error '%s'" %
                    (framework, e))
                continue

            log("Counted %s lines of code" % line_count)
            framework_to_count[framework] = line_count

        self.rawData['slocCounts'] = framework_to_count

    def __count_commits(self):
        '''
        Count the git commits for all the framework tests
        '''
        frameworks = self.benchmarker.metadata.gather_frameworks(
            self.config.test, self.config.exclude)

        def count_commit(directory, jsonResult):
            command = "git rev-list HEAD -- " + directory + " | sort -u | wc -l"
            try:
                commitCount = subprocess.check_output(command, shell=True)
                jsonResult[framework] = int(commitCount)
            except subprocess.CalledProcessError:
                pass

        # Because git can be slow when run in large batches, this
        # calls git up to 4 times in parallel. Normal improvement is ~3-4x
        # in my trials, or ~100 seconds down to ~25
        # This is safe to parallelize as long as each thread only
        # accesses one key in the dictionary
        threads = []
        jsonResult = {}
        # t1 = datetime.now()
        for framework, testlist in frameworks.items():
            directory = testlist[0].directory
            t = threading.Thread(
                target=count_commit, args=(directory, jsonResult))
            t.start()
            threads.append(t)
            # Git has internal locks, full parallel will just cause contention
            # and slowness, so we rate-limit a bit
            if len(threads) >= 4:
                threads[0].join()
                threads.remove(threads[0])

        # Wait for remaining threads
        for t in threads:
            t.join()
        # t2 = datetime.now()
        # print "Took %s seconds " % (t2 - t1).seconds

        self.rawData['commitCounts'] = jsonResult
        self.config.commits = jsonResult

    def __get_git_commit_id(self):
        '''
        Get the git commit id for this benchmark
        '''
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.config.fw_root).decode('utf-8').strip()

    def __get_git_repository_url(self):
        '''
        Gets the git repository url for this benchmark
        '''
        return subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=self.config.fw_root).decode('utf-8').strip()

    def __get_git_branch_name(self):
        '''
        Gets the git branch name for this benchmark
        '''
        return subprocess.check_output(
            'git rev-parse --abbrev-ref HEAD',
            shell=True,
            cwd=self.config.fw_root).decode('utf-8').strip()

    def __parse_stats(self, framework_test, test_type, start_time, end_time,
                      interval):
        '''
        For each test type, process all the statistics, and return a multi-layered
        dictionary that has a structure as follows:

        (timestamp)
        | (main header) - group that the stat is in
        | | (sub header) - title of the stat
        | | | (stat) - the stat itself, usually a floating point number
        '''
        stats_dict = dict()
        stats_file = self.get_stats_file(framework_test.name, test_type)
        with open(stats_file) as stats:
            rows = list(csv.reader(stats))

        def is_number(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        # 'epoch' appears in both header rows; the sub header is the one
        # immediately followed by a numeric data row.
        header_index = next(
            (i for i, row in enumerate(rows)
             if 'epoch' in row and i > 0 and i + 1 < len(rows)
             and len(rows[i + 1]) > row.index('epoch')
             and is_number(rows[i + 1][row.index('epoch')])),
            None)
        if header_index is None:
            return stats_dict
        main_header = rows[header_index - 1]
        sub_header = rows[header_index]
        main_header = main_header + [''] * (len(sub_header) - len(main_header))
        time_row = sub_header.index("epoch")
        int_counter = 0
        for row in rows[header_index + 1:]:
            # dool appends to an existing file, so a noise re-run repeats the
            # preamble and header rows; only numeric rows are samples
            if len(row) != len(sub_header) or not is_number(row[time_row]):
                continue
            time = float(row[time_row])
            int_counter += 1
            if time < start_time:
                continue
            elif time > end_time:
                return stats_dict
            if int_counter % interval != 0:
                continue
            row_dict = dict()
            for nextheader in main_header:
                if nextheader != "":
                    row_dict[nextheader] = dict()
            header = ""
            for item_num, column in enumerate(row):
                if len(main_header[item_num]) != 0:
                    header = main_header[item_num]
                # all the stats are numbers, so we want to make sure that they stay that way in json
                row_dict[header][sub_header[item_num]] = float(column) if column.strip() else None
            stats_dict[time] = row_dict
        return stats_dict
