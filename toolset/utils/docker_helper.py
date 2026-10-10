import io
import json
import os
import posixpath
import socket
import tarfile
import time
import re
import traceback
import docker
import requests

from threading import Thread
from colorama import Fore, Style

from toolset.utils.output_helper import log

from psutil import virtual_memory

# memory limit for the (non-benchmark) test server container
mem_limit = int(round(virtual_memory().total * .95))

TEST_IMAGE_PREFIX = 'ssgberk/test.'
RUN_LABEL = 'ssgberk.run'
QUALITY_IMAGE = 'ssgberk/quality'
QUALITY_TIMEOUT_SECONDS = 1800
QUALITY_MEMORY = '4g'


class DockerHelper:

    @staticmethod
    def is_ssgberk_test_image(tag):
        return tag.startswith(TEST_IMAGE_PREFIX)

    def __init__(self, benchmarker=None):
        self.benchmarker = benchmarker

        self.server = docker.DockerClient(
            base_url=self.benchmarker.config.server_docker_host)

    last_build = None
    _quality_image = None

    def _run_labels(self):
        return {RUN_LABEL: str(self.benchmarker.config.run_id)}

    def __build(self, base_url, path, build_log_file, log_prefix, dockerfile,
                tag, buildargs={}, nocache=False):
        '''
        Builds docker containers using docker-py low-level api
        '''

        self.benchmarker.time_logger.mark_build_start()
        with open(build_log_file, 'w') as build_log:
            try:
                client = docker.APIClient(base_url=base_url)
                output = client.build(
                    path=path,
                    dockerfile=dockerfile,
                    tag=tag,
                    forcerm=True,
                    timeout=3600,
                    pull=True,
                    nocache=nocache,
                    buildargs=buildargs,
                    decode=True
                )
                buffer = ""
                for token in output:
                    if 'stream' in token:
                        buffer += token['stream']
                    elif 'errorDetail' in token:
                        raise Exception(token['errorDetail']['message'])
                    while "\n" in buffer:
                        index = buffer.index("\n")
                        line = buffer[:index]
                        buffer = buffer[index + 1:]
                        log(line,
                            prefix=log_prefix,
                            file=build_log,
                            color=Fore.WHITE + Style.BRIGHT
                            if re.match(r'^Step \d+\/\d+', line) else '')
                    # Kill docker builds if they exceed 60 mins. This will only
                    # catch builds that are still printing output.
                    if self.benchmarker.time_logger.time_since_start() > 3600:
                        log("Build time exceeded 60 minutes",
                            prefix=log_prefix,
                            file=build_log,
                            color=Fore.RED)
                        raise Exception

                if buffer:
                    log(buffer,
                        prefix=log_prefix,
                        file=build_log,
                        color=Fore.WHITE + Style.BRIGHT
                        if re.match(r'^Step \d+\/\d+', buffer) else '')
            except Exception:
                tb = traceback.format_exc()
                log("Docker build failed; terminating",
                    prefix=log_prefix,
                    file=build_log,
                    color=Fore.RED)
                log(tb, prefix=log_prefix, file=build_log)
                self.benchmarker.time_logger.log_build_end(
                    log_prefix=log_prefix, file=build_log)
                raise

            self.benchmarker.time_logger.log_build_end(
                log_prefix=log_prefix, file=build_log)

    def clean(self):
        '''
        Removes the ssgberk/test.* generator images. Other images (and the dangling
        images of other projects on a shared Docker host) are left alone; removing a
        tagged image already deletes its unused layers.
        '''

        for image in self.server.images.list():
            if len(image.tags) > 0:
                if DockerHelper.is_ssgberk_test_image(image.tags[0]):
                    self.server.images.remove(image.id, force=True)

    def build(self, test, build_log_dir=os.devnull):
        '''
        Builds the test docker containers
        '''
        log_prefix = "%s: " % test.name
        self.last_build = None

        # Build the test image
        test_docker_file = '%s.dockerfile' % test.name
        if hasattr(test, 'dockerfile'):
            test_docker_file = test.dockerfile
        build_log_file = build_log_dir
        if build_log_dir is not os.devnull:
            build_log_file = os.path.join(
                build_log_dir,
                "%s.log" % test_docker_file.replace(".dockerfile", "").lower())

        tag = "%s%s" % (TEST_IMAGE_PREFIX, test.name)
        no_cache = bool(getattr(self.benchmarker.config, 'no_cache', False))
        rc = 0
        start = time.monotonic()
        try:
            self.__build(
                base_url=self.benchmarker.config.server_docker_host,
                build_log_file=build_log_file,
                log_prefix=log_prefix,
                path=test.directory,
                dockerfile=test_docker_file,
                buildargs=({
                    'BENCHMARK_ENV':
                        self.benchmarker.config.results_environment,
                    'TFB_TEST_NAME': test.name,
                }),
                tag=tag,
                nocache=no_cache)
        except Exception:
            rc = 1
        seconds = time.monotonic() - start

        # Recorded (also for a failed build) apart from the timed site build
        image_id = size_bytes = None
        # (a failed build must not pick up a stale image from an earlier build)
        if rc == 0:
            try:
                image = self.server.images.get(tag)
                image_id = image.id
                size_bytes = image.attrs.get("Size")
            except Exception:
                pass
        self.last_build = {"seconds": seconds, "imageId": image_id,
                           "sizeBytes": size_bytes, "noCache": no_cache}
        return rc

    def run(self, test, run_log_dir):
        '''
        Run the given Docker container(s)
        '''

        log_prefix = "%s: " % test.name
        container = None

        try:

            def watch_container(docker_container, docker_file):
                with open(
                        os.path.join(
                            run_log_dir, "%s.log" % docker_file.replace(
                                ".dockerfile", "").lower()), 'w') as run_log:
                    for line in docker_container.logs(stream=True):
                        log(line.decode('utf-8', 'replace'), prefix=log_prefix, file=run_log)

            extra_hosts = None
            # Unique per run so concurrent runs do not collide on the name
            name = "ssgberk-%s-%s" % (
                str(self.benchmarker.config.run_id)[:8], test.name)

            if self.benchmarker.config.network is None:
                extra_hosts = {
                    socket.gethostname():
                    str(self.benchmarker.config.server_host),
                    'ssgberk-server':
                    str(self.benchmarker.config.server_host)  # ,
                }
                name = None

            sysctl = {'net.core.somaxconn': 65535}

            ulimit = [{
                'name': 'nofile',
                'hard': 200000,
                'soft': 200000
            }, {
                'name': 'rtprio',
                'hard': 99,
                'soft': 99
            }]

            docker_cmd = ''
            if hasattr(test, 'docker_cmd'):
                docker_cmd = test.docker_cmd

            # Expose ports in debugging mode
            ports = {}
            if self.benchmarker.config.mode == "debug":
                ports = {test.port: test.port}

            container = self.server.containers.run(
                "%s%s" % (TEST_IMAGE_PREFIX, test.name),
                name=name,
                labels=self._run_labels(),
                command=docker_cmd,
                network=self.benchmarker.config.network,
                network_mode=self.benchmarker.config.network_mode,
                ports=ports,
                stderr=True,
                detach=True,
                init=True,
                extra_hosts=extra_hosts,
                privileged=True,
                ulimits=ulimit,
                mem_limit=mem_limit,
                sysctls=sysctl,
                remove=True,
                log_config={'type': None})

            watch_thread = Thread(
                target=watch_container,
                args=(
                    container,
                    "%s.dockerfile" % test.name,
                ))
            watch_thread.daemon = True
            watch_thread.start()

        except Exception:
            with open(
                    os.path.join(run_log_dir, "%s.log" % test.name.lower()),
                    'w') as run_log:
                tb = traceback.format_exc()
                log("Running docker container: %s.dockerfile failed" %
                    test.name,
                    prefix=log_prefix,
                    file=run_log)
                log(tb, prefix=log_prefix, file=run_log)

        return container

    @staticmethod
    def __stop_container(container):
        try:
            container.stop(timeout=2)
            time.sleep(2)
        except:
            # container has already been killed
            pass

    @staticmethod
    def __stop_all(docker_client, run_id):
        try:
            containers = docker_client.containers.list(
                filters={'label': '%s=%s' % (RUN_LABEL, run_id)})
        except (docker.errors.NotFound, docker.errors.ImageNotFound):
            return
        for container in containers:
            DockerHelper.__stop_container(container)

    def other_runs(self, own_run_id):
        '''
        Run ids of live containers labelled ssgberk.run that belong to a run
        other than own_run_id (sorted, unique).
        '''
        try:
            containers = self.server.containers.list(filters={'label': RUN_LABEL})
        except docker.errors.NotFound:
            return []
        found = set()
        for container in containers:
            try:
                run_id = container.labels.get(RUN_LABEL)
            except docker.errors.NotFound:
                # container vanished between list and inspect
                continue
            if run_id and run_id != str(own_run_id):
                found.add(run_id)
        return sorted(found)

    def stop(self, containers=None):
        '''
        Attempts to stop a container or list of containers.
        If no containers are passed, stops the running containers of this run
        (label ssgberk.run=<run_id>); other runs are left untouched.
        '''

        if containers:
            if not isinstance(containers, list):
                containers = [containers]
            for container in containers:
                DockerHelper.__stop_container(container)
        else:
            DockerHelper.__stop_all(self.server, self.benchmarker.config.run_id)

        # Only this run's stopped containers: the Docker host is shared with other projects.
        self.server.containers.prune(
            filters={"label": "%s=%s" % (RUN_LABEL, self.benchmarker.config.run_id)})

    def server_container_exists(self, container_id_or_name):
        '''
        Returns True if the container still exists on the server.
        '''
        try:
            self.server.containers.get(container_id_or_name)
            return True
        except:
            return False

    def benchmark(self, framework_test, script, variables, raw_file,
                  resources, timeout_seconds, export=None):
        '''
        Runs the generator container with fixed resource limits and returns
        {"status": "ok"|"timeout"|"oom", "exitCode": int}. The container is
        always stopped and removed before returning. With export
        (output_folder, dest_tar), a successful build's output is copied to
        dest_tar first (spec 009 R-3).
        '''

        def watch_container(container):
            import codecs
            with open(raw_file, 'w', encoding='utf-8') as benchmark_file:
                decoder = codecs.getincrementaldecoder('utf-8')('replace')
                for chunk in container.logs(stream=True):
                    text = decoder.decode(chunk)
                    benchmark_file.write(text)
                    benchmark_file.flush()
                    log(text)
                tail = decoder.decode(b'', final=True)
                if tail:
                    benchmark_file.write(tail)
                    benchmark_file.flush()
                    log(tail)

        sysctl = {'net.core.somaxconn': 65535}

        ulimit = [
            {'name': 'nofile', 'hard': 65535, 'soft': 65535}#,
            #{'name': 'cpu', 'hard': 18446744073709551615, 'soft': 0} 
        ]

        container = self.server.containers.run(
            "%s%s" % (TEST_IMAGE_PREFIX, framework_test.name),
            "/bin/bash ./%s" % (script),
            environment=variables,
            labels=self._run_labels(),
            network=self.benchmarker.config.network,
            network_mode=self.benchmarker.config.network_mode,
            #volumes=volume,
            detach=True,
            stderr=True,
            ulimits=ulimit,
            sysctls=sysctl,
            nano_cpus=int(resources['cpus'] * 1e9),
            mem_limit=resources['memoryBytes'],
            # equal to mem_limit: swap disabled
            memswap_limit=resources['memoryBytes'],
            cpuset_cpus=resources.get('cpuset'),
            remove=False,
            log_config={'type': None}
        )
        status, exit_code = 'ok', None
        try:
            watcher = Thread(target=watch_container, args=(container,), daemon=True)
            watcher.start()
            try:
                result = container.wait(timeout=timeout_seconds)
                exit_code = result.get('StatusCode')
            except requests.exceptions.ReadTimeout:
                status = 'timeout'
            except requests.exceptions.ConnectionError as e:
                # docker-py surfaces a read timeout as ConnectionError on some urllib3 versions
                if (isinstance(e, requests.exceptions.ConnectTimeout)
                        or 'timed out' not in str(e).lower()):
                    raise
                status = 'timeout'
            if status == 'timeout':
                try:
                    container.stop(timeout=10)
                except docker.errors.APIError:
                    pass
            watcher.join(timeout=60)
            container.reload()
            state = container.attrs.get('State', {})
            if exit_code is None:
                exit_code = state.get('ExitCode')
            # R-19: OOMKilled, or exit 137 (SIGKILL) that we did not cause by
            # stopping the container after a timeout
            if status == 'ok' and (state.get('OOMKilled') or exit_code == 137):
                status = 'oom'
            if export and status == 'ok' and exit_code == 0:
                DockerHelper.__export_output(container, *export)
        finally:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass
        return {'status': status, 'exitCode': exit_code}

    @staticmethod
    def __export_output(container, output_folder, dest):
        '''Copies <WorkingDir>/<output_folder> to dest as a tar. Never raises.'''
        try:
            workdir = (container.attrs.get('Config') or {}).get('WorkingDir') or '/'
            bits, _ = container.get_archive(posixpath.join(workdir, output_folder))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                for chunk in bits:
                    f.write(chunk)
        except Exception as e:
            log("quality: could not export %s: %s" % (output_folder, e), color=Fore.YELLOW)

    def build_quality_image(self):
        '''
        Builds ssgberk/quality from <fw_root>/quality once per process
        (spec 009 R-4), outside the generator build-time accounting.
        '''
        if self._quality_image:
            return self._quality_image
        client = docker.APIClient(base_url=self.benchmarker.config.server_docker_host)
        for token in client.build(path=os.path.join(self.benchmarker.config.fw_root, 'quality'),
                                  dockerfile='Dockerfile', tag=QUALITY_IMAGE, forcerm=True,
                                  pull=True, timeout=3600, decode=True):
            if 'errorDetail' in token:
                raise RuntimeError(token['errorDetail']['message'])
            if token.get('stream', '').strip():
                log(token['stream'].rstrip(), prefix='quality: ')
        self._quality_image = self.server.images.get(QUALITY_IMAGE).id
        return self._quality_image

    def run_quality(self, tar_path, site_name, pages,
                    timeout_seconds=QUALITY_TIMEOUT_SECONDS):
        '''
        Runs quality/run.mjs on the exported site with no network and no
        mounts (spec 009 R-4, R-5) and returns its raw.json.
        '''
        image = self.build_quality_image()
        command = ['node', '/quality/run.mjs', '--site', '/work/' + site_name,
                   '--pages', json.dumps(pages), '--out', '/work/out']
        container = self.server.containers.create(
            image, command=command, labels=self._run_labels(), network_mode='none',
            mem_limit=QUALITY_MEMORY, working_dir='/work')
        try:
            with open(tar_path, 'rb') as f:
                container.put_archive('/work', f.read())
            container.start()
            result = container.wait(timeout=timeout_seconds)
            try:
                bits, _ = container.get_archive('/work/out/raw.json')
            except docker.errors.NotFound:
                logs = container.logs().decode('utf-8', 'replace')
                raise RuntimeError('collector wrote no raw.json (exit %s): %s' % (
                    result.get('StatusCode'), logs[-2000:]))
            with tarfile.open(fileobj=io.BytesIO(b''.join(bits))) as tar:
                return json.load(tar.extractfile(tar.getmembers()[0]))
        finally:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass
