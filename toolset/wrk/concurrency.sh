#!/bin/bash
#echo " %wrk -H 'Host: $server_host' -H 'Accept: $accept' -H 'Connection: keep-alive' --latency -d 5 -c 8 --timeout 8 -t 8 $url"
hyperfine --export-json hugo_throughputTest_date.json 'hugo' --show-output
sleep 5
