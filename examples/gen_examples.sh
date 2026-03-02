#!/bin/bash
# this file when run generates all examples on the user's computer

script_path=$(realpath “${BASH_SOURCE:-$0}”)
examples_dir=$(dirname ${script_path})
src_dir=${examples_dir}/../gap_profiler

for dir in $(ls -d */)
do
    dir=$(echo "$dir" | sed 's:/*$::') # removes possible trailing slashes from dir
    to_run_path=${examples_dir}/${dir}
    cd ${to_run_path}
    gap ${to_run_path}/${dir}.g
    python3 ${src_dir}/data_processing/parser.py ${dir}.json ${dir}.zip ${to_run_path}
    cd ${examples_dir}
done
