#!/bin/bash

set -e

echo "running ssgberk-shutdown script"
./ssgberk-shutdown.sh

echo "removing old ssgberk directory if necessary"
if [ -d "$TFB_REPOPARENT/$TFB_REPONAME" ]; then
  sudo rm -rf $TFB_REPOPARENT/$TFB_REPONAME
fi

echo "cloning ssgberk repository"
git clone \
  -b $TFB_REPOBRANCH \
  $TFB_REPOURI \
  $TFB_REPOPARENT/$TFB_REPONAME \
  --depth 1

echo "moving to ssgberk directory"
cd $TFB_REPOPARENT/$TFB_REPONAME

echo "building ssgberk docker image"
docker build -t matheusrv/ssgberk .

echo "running ssgberk docker image"
docker run \
  --network=host \
  --mount type=bind,source=$TFB_REPOPARENT/$TFB_REPONAME,target=/FrameworkBenchmarks \
  matheusrv/ssgberk \
  --server-host $TFB_SERVER_HOST \
  --client-host $TFB_CLIENT_HOST \
  --database-host $TFB_DATABASE_HOST \
  --network-mode host \
  --results-name "$TFB_RUN_NAME" \
  --results-environment "$TFB_ENVIRONMENT" \
  --results-upload-uri "$TFB_UPLOAD_URI" \
  --quiet

echo "zipping the results"
zip -r results.zip results

echo "uploading the results"
curl \
  -i -v \
  -X POST \
  --header "Content-Type: application/zip" \
  --data-binary @results.zip \
  $TFB_UPLOAD_URI

echo "done uploading results"
