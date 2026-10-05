import argparse
import glob
import os
import socket
import sys
import json
import signal
import time
import traceback
from toolset.benchmark import suites
from toolset.benchmark.benchmarker import Benchmarker
from toolset.utils.scaffolding import Scaffolding
from toolset.utils.audit import Audit
from toolset.utils import cleaner
from toolset.utils.benchmark_config import BenchmarkConfig
from toolset.utils.output_helper import log

# Enable cross-platform colored output
from colorama import init, Fore
init()


class StoreSeqAction(argparse.Action):
    '''
    Helper class for parsing a sequence from the command line
    '''

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(
            option_strings, dest, type=str, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.parse_seq(values))

    def parse_seq(self, argument):
        result = argument.split(',')
        sequences = [x for x in result if ":" in x]
        for sequence in sequences:
            try:
                (start, step, end) = sequence.split(':')
            except ValueError:
                log("  Invalid: {!s}".format(sequence), color=Fore.RED)
                log("  Requires start:step:end, e.g. 1:2:10", color=Fore.RED)
                raise
            result.remove(sequence)
            result = result + list(range(int(start), int(end), int(step)))
        return [abs(int(item)) for item in result]


###################################################################################################
# Parser Builder
###################################################################################################
def build_parser():
    '''
    Builds and returns the argument parser for the toolset.
    '''
    parser = argparse.ArgumentParser(
        description="Run the Static Site Generator Benchmarks (SSGBerk) suite.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='''If an argument includes (type int-sequence), then it accepts integer lists in multiple forms.
        Using a single number e.g. 5 will create a list [5]. Using commas will create a list containing those
        values e.g. 1,3,6 creates [1, 3, 6]. Using three colon-separated numbers of start:step:end will create a
        list, using the semantics of python's range function, e.g. 1:3:15 creates [1, 4, 7, 10, 13] while
        0:1:5 creates [0, 1, 2, 3, 4]
        ''')

    # Suite options
    parser.add_argument(
        '--audit',
        action='store_true',
        default=False,
        help='Audits framework tests for inconsistencies'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        default=False,
        help='Removes the results directory'
    )
    parser.add_argument(
        '--new',
        action='store_true',
        default=False,
        help='Initialize a new framework test'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        default=False,
        help='Only print a limited set of messages to stdout, keep the bulk of messages in log files only'
    )
    parser.add_argument(
        '--results-name',
        help='Gives a name to this set of results, formatted as a date',
        default='(unspecified, datetime = %Y-%m-%d %H:%M:%S)'
    )
    parser.add_argument(
        '--results-environment',
        help='Describes the environment in which these results were gathered',
        default='(unspecified, hostname = %s)' % socket.gethostname()
    )
    parser.add_argument(
        '--results-upload-uri',
        default=None,
        help='A URI where the in-progress results.json file will be POSTed periodically'
    )
    parser.add_argument(
        '--parse',
        help='Parses the results of the given timestamp and merges that with the latest results'
    )

    # Test options
    parser.add_argument(
        '--test',
        default=None,
        nargs='+',
        help='names of tests to run'
    )
    parser.add_argument(
        '--test-dir',
        nargs='+',
        dest='test_dir',
        help='name of framework directory containing all tests to run'
    )
    parser.add_argument(
        '--test-lang',
        nargs='+',
        dest='test_lang',
        help='name of language directory containing all tests to run'
    )
    parser.add_argument(
        '--exclude',
        default=None,
        nargs='+',
        help='names of tests to exclude'
    )
    parser.add_argument(
        '--type',
        choices=[
            'all', 'datarate'
        ],
        nargs='+',
        default=['all'],
        help='which type of test to run'
    )
    parser.add_argument(
        '-m',
        '--mode',
        choices=['benchmark', 'debug'],
        default='benchmark',
        help='Debug mode will skip verification and leave the server running.'
    )
    parser.add_argument(
        '--list-tests',
        action='store_true',
        default=False,
        help='lists all the known tests that can run'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='Run the generator build command in verbose mode')

    # Benchmark options
    parser.add_argument(
        '--duration',
        default=15,
        help='Time in seconds that each test should run for.'
    )
    parser.add_argument(
        '-nf', '--number-of-files', default='10',
        help='Number of markdown posts generated for each build')
    parser.add_argument(
        '-cs', '--content-size',
        choices=['0.500', '500', '1000', '5000', '10000', '100000'],
        default='0.500',
        help='Size of each post in KB (0.500 = one paragraph)')
    parser.add_argument(
        '-mr', '--min-runs', default='3',
        help='Number of timed hyperfine runs per build')
    parser.add_argument(
        '--suite',
        choices=suites.names(),
        default=None,
        help='Run a named suite of (number of files, content size) cells; '
             'cannot be combined with -nf, -cs or -mr')
    parser.add_argument(
        '--server-host',
        default='ssgberk-server',
        help='Hostname/IP for application server'
    )

    # Network options
    parser.add_argument(
        '--network-mode',
        default=None,
        help='The network mode to run docker in')

    return parser


SUITE_CONFLICTS = ('-nf', '--number-of-files', '-cs', '--content-size',
                   '-mr', '--min-runs')


def run_suite(args):
    '''
    Runs every cell of the suite, one Benchmarker per cell, then writes suite.json.
    '''
    suite = suites.load(args.suite)
    profile = os.getenv('SSGBERK_PROFILE', 'core')
    base = BenchmarkConfig(args)
    start = int(round(time.time() * 1000))
    cells = []
    benchmarker = None
    interrupted = []

    def stop(signum=None, frame=None):
        interrupted.append(signum)
        if benchmarker is not None:
            benchmarker.stop(signum, frame)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    try:
        for index, cell in enumerate(suite.cells):
            if interrupted:
                break
            config = base.for_cell(suite, cell, index, profile)
            benchmarker = Benchmarker(config)
            order = suites.rotate([t.name for t in benchmarker.tests], index)
            benchmarker.tests.sort(key=lambda t: order.index(t.name))
            benchmarker.run()
            results = benchmarker.results
            cells.append({
                'index': index,
                'numberOfFiles': cell.number_of_files,
                'contentSize': cell.content_size,
                'dir': suites.cell_dir(profile, cell),
                'order': order,
                'succeeded': len(results.succeeded.get('datarate', [])),
                'failed': len(results.failed.get('datarate', [])),
            })
            if index < len(suite.cells) - 1 and suite.cooldown_seconds:
                time.sleep(suite.cooldown_seconds)
    except Exception:
        log("A fatal error has occurred", color=Fore.RED)
        log(traceback.format_exc())
        try:
            benchmarker.stop()
        except Exception:
            pass
        return 1
    finally:
        out = os.path.join(base.results_root, base.timestamp, 'suite.json')
        with open(out, 'w') as f:
            json.dump({
                'schemaVersion': 1, 'suite': suite.name,
                'version': suite.version, 'profile': profile,
                'startTime': start,
                'completionTime': int(round(time.time() * 1000)),
                'cells': cells,
            }, f, indent=2)

    return 0


###################################################################################################
# Main
###################################################################################################
def main(argv=None):
    '''
    Runs the toolset.
    '''
    # Do argv default this way, as doing it in the functional declaration sets it at compile time
    if argv is None:
        argv = sys.argv

    args = build_parser().parse_args(argv[1:])

    if args.suite:
        explicit = [a for a in argv[1:] if a.split('=')[0] in SUITE_CONFLICTS]
        if explicit:
            log("--suite cannot be combined with %s" % ", ".join(explicit),
                color=Fore.RED)
            return 1
        return run_suite(args)

    if args.parse:
        # Validate before BenchmarkConfig/Benchmarker, which create the directory
        results_dir = os.path.join(os.getenv('FWROOT', ''), 'results', args.parse)
        if not glob.glob(os.path.join(results_dir, '*', '*', 'raw.txt')):
            log("Cannot --parse %s: no raw.txt files found under %s" %
                (args.parse, results_dir), color=Fore.RED)
            return 1

    config = BenchmarkConfig(args)
    benchmarker = Benchmarker(config)

    signal.signal(signal.SIGTERM, benchmarker.stop)
    signal.signal(signal.SIGINT, benchmarker.stop)

    try:
        if config.new:
            Scaffolding(benchmarker)

        elif config.audit:
            Audit(benchmarker).start_audit()

        elif config.clean:
            cleaner.clean(benchmarker.results)
            benchmarker.docker_helper.clean()

        elif config.list_tests:
            all_tests = benchmarker.metadata.gather_tests()

            for test in all_tests:
                log(test.name)

        elif config.parse:
            all_tests = benchmarker.metadata.gather_tests()

            # Keep the metadata of the original run; recompute only the outcomes
            results = benchmarker.results
            results.load()
            results.rawData = {'datarate': {}}
            results.succeeded = {'datarate': []}
            results.failed = {'datarate': []}

            for test in all_tests:
                results.parse_all(test)

            results.parse(all_tests)

        else:
            benchmarker.run()

    except Exception:
        tb = traceback.format_exc()
        log("A fatal error has occurred", color=Fore.RED)
        log(tb)
        # try one last time to stop docker containers on fatal error
        try:
            benchmarker.stop()
        except:
            sys.exit(1)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
