#!/bin/bash
# this file when run generates all examples on the user's computer

script_path=$(realpath “${BASH_SOURCE:-$0}”)
examples_dir=$(dirname ${script_path})
src_dir=${examples_dir}/../gap_profiler

for dir in $(ls -d */)
do
    dir=${dir%\/} # strips forward slash from end of dirname
    to_run_path=${examples_dir}/${dir}
    rm $to_run_path/${dir}.json
    rm $to_run_path/${dir}.zip
done
