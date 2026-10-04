FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG DOOL_VERSION=v1.3.8

# WARNING: DON'T PUT A SPACE AFTER ANY BACKSLASH OR APT WILL BREAK
RUN apt-get -yqq update && apt-get -yqq install --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
      ca-certificates cloc curl git \
      python3 python3-colorama python3-pip python3-psutil python3-requests && \
    pip3 install --break-system-packages docker==7.1.0 && \
    rm -rf /var/lib/apt/lists/*

# Collect resource usage statistics
WORKDIR /tmp/dool
RUN curl -LSs "https://github.com/scottchiefbaker/dool/archive/${DOOL_VERSION}.tar.gz" | \
      tar --strip-components=1 -xz && \
    ./install.py && \
    rm -rf /tmp/dool

# The repository is bind-mounted with the host user's ownership
RUN git config --system --add safe.directory '*'

ENV PYTHONPATH=/FrameworkBenchmarks FWROOT=/FrameworkBenchmarks
WORKDIR /FrameworkBenchmarks

ENTRYPOINT ["python3", "/FrameworkBenchmarks/toolset/run-tests.py"]
