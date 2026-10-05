#!/bin/bash
# Thin wrapper: runs a named suite (smoke, standard, stress, legacy-2019).
# Suite definitions live in toolset/benchmark/suites.json.
exec ./ssgberk --suite "${1:-standard}" "${@:2}"
