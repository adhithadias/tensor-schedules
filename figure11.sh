#!/bin/bash

cwd=$(pwd)

python3 -m src.main_store_json -f test8_config.json -r
python3 -m src.main_store_json_z3 -f test8_config.json -r

# plot all graphs execution times
# you may have to increase the timeout if you are running inside the docker container
python3 -m src.main_run_test_all_schedules -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -m -x -e 64 --timeout 15
python3 scripts/plot_all_times.py -t 1 -d $cwd/../ --dimension 64

python3 -m src.main_run_test_all_schedules -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -m -x -e 128 --timeout 15
python3 scripts/plot_all_times.py -t 2 -d $cwd/../ --dimension 128