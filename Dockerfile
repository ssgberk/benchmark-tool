FROM buildpack-deps:bionic

RUN apt-get -yqq update

# WARNING: DONT PUT A SPACE AFTER ANY BACKSLASH OR APT WILL BREAK
RUN apt-get -yqq install -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
git-core cloc dstat python-dev python-pip software-properties-common

RUN pip install colorama==0.3.1 requests docker==4.0.2 psutil

# Fix for docker-py trying to import one package from the wrong location
RUN cp -r /usr/local/lib/python2.7/dist-packages/backports/ssl_match_hostname/ /usr/lib/python2.7/dist-packages/backports

ENV PYTHONPATH /FrameworkBenchmarks
ENV FWROOT /FrameworkBenchmarks

ENTRYPOINT ["python", "/FrameworkBenchmarks/toolset/run-tests.py"]
