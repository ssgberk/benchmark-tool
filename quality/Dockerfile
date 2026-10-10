# SSGBerk quality collector (benchmark-tool spec 009): Lighthouse, axe-core,
# html-validate and lychee against Playwright's Chromium. Runs with no network.
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=24.21.0
ARG LYCHEE_VERSION=0.24.2

RUN apt-get -yqq update \
 && apt-get -yqq install --no-install-recommends ca-certificates curl xz-utils \
 && rm -rf /var/lib/apt/lists/*

RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in amd64) NARCH=x64 ;; arm64) NARCH=arm64 ;; *) echo "unsupported $ARCH"; exit 1 ;; esac \
 && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1 \
 && node --version

RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in amd64) LARCH=x86_64 ;; arm64) LARCH=aarch64 ;; *) echo "unsupported $ARCH"; exit 1 ;; esac \
 && curl -fsSL "https://github.com/lycheeverse/lychee/releases/download/lychee-v${LYCHEE_VERSION}/lychee-${LARCH}-unknown-linux-gnu.tar.gz" \
    | tar -xz -C /usr/local/bin --strip-components=1 --wildcards '*/lychee' \
 && lychee --version

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright NPM_CONFIG_UPDATE_NOTIFIER=false
WORKDIR /quality
COPY package.json package-lock.json ./
RUN npm ci --omit=dev \
 && npx playwright install --with-deps chromium \
 && rm -rf /root/.npm /var/lib/apt/lists/*
COPY run.mjs ./
RUN mkdir -p /work /quality-out
WORKDIR /work
