import os
import socket
import json
import time
import re
import traceback
import docker

from threading import Thread
from colorama import Fore, Style

from toolset.utils.output_helper import log

from psutil import virtual_memory

# total memory limit allocated for the test container
mem_limit = int(round(virtual_memory().total * .95))


class DockerHelper:
    def __init__(self, benchmarker=None):
        self.benchmarker = benchmarker

        self.server = docker.DockerClient(
            base_url=self.benchmarker.config.server_docker_host)

    def __build(self, base_url, path, build_log_file, log_prefix, dockerfile,
                tag, buildargs={}):
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
                    buildargs=buildargs
                )
                buffer = ""
                for token in output:
                    if token.startswith('{"stream":'):
                        token = json.loads(token)
                        token = token[token.keys()[0]].encode('utf-8')
                        buffer += token
                    elif token.startswith('{"errorDetail":'):
                        token = json.loads(token)
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
        Cleans all the docker images from the system
        '''

        self.server.images.prune()
        for image in self.server.images.list():
            if len(image.tags) > 0:
                # 'matheusrv/ssgberk.test.gemini:0.1' -> 'matheusrv/ssgberk.test.gemini'
                image_tag = image.tags[0].split(':')[0]
                if image_tag != 'matheusrv/ssgberk' and 'matheusrv' in image_tag:
                    self.server.images.remove(image.id, force=True)
        self.server.images.prune()

    def build(self, test, build_log_dir=os.devnull):
        '''
        Builds the test docker containers
        '''
        log_prefix = "%s: " % test.name

        # Build the test image
        test_docker_file = '%s.dockerfile' % test.name
        if hasattr(test, 'dockerfile'):
            test_docker_file = test.dockerfile
        build_log_file = build_log_dir
        if build_log_dir is not os.devnull:
            build_log_file = os.path.join(
                build_log_dir,
                "%s.log" % test_docker_file.replace(".dockerfile", "").lower())

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
                tag="matheusrv/ssgberk.test.%s" % test.name)
        except Exception:
            return 1

        return 0

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
                        log(line, prefix=log_prefix, file=run_log)

            extra_hosts = None
            name = "ssgberk-server"

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
                "matheusrv/ssgberk.test.%s" % test.name,
                name=name,
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
    def __stop_all(docker_client):
        for container in docker_client.containers.list():
            if len(container.image.tags) > 0 \
                    and 'matheusrv' in container.image.tags[0] \
                    and 'ssgberk:latest' not in container.image.tags[0]:
                DockerHelper.__stop_container(container)

    def stop(self, containers=None):
        '''
        Attempts to stop a container or list of containers.
        If no containers are passed, stops all running containers.
        '''

        if containers:
            if not isinstance(containers, list):
                containers = [containers]
            for container in containers:
                DockerHelper.__stop_container(container)
        else:
            DockerHelper.__stop_all(self.server)

        self.server.containers.prune()

    def server_container_exists(self, container_id_or_name):
        '''
        Returns True if the container still exists on the server.
        '''
        try:
            self.server.containers.get(container_id_or_name)
            return True
        except:
            return False

    def benchmark(self, framework_test, script, variables, raw_file):
        '''
        Runs the given remote_script on the wrk container on the client machine.
        '''

        def watch_container(container):
            with open(raw_file, 'w') as benchmark_file:
                for line in container.logs(stream=True):
                    log(line, file=benchmark_file)

        sysctl = {'net.core.somaxconn': 65535}

        ulimit = [
            {'name': 'nofile', 'hard': 65535, 'soft': 65535}#,
            #{'name': 'cpu', 'hard': 18446744073709551615, 'soft': 0} 
        ]

        watch_container(
            self.server.containers.run(
                "matheusrv/ssgberk.test.%s" % framework_test.name,
                "/bin/bash ./%s" % (script),
                environment=variables,
                network=self.benchmarker.config.network,
                network_mode=self.benchmarker.config.network_mode,
                #volumes=volume,
                detach=True,
                stderr=True,
                ulimits=ulimit,
                sysctls=sysctl,
                remove=True,
                log_config={'type': None}
            )
        )
