#!/bin/bash

cwd=$(pwd)

# plot all graphs execution times
python3 -m src.main_run_test_all_schedules -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -m -x -e 64 --timeout 15
python3 scripts/plot_all_times.py -t 1 -d $cwd/../ --dimension 64

python3 -m src.main_run_test_all_schedules -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -m -x -e 128 --timeout 15
python3 scripts/plot_all_times.py -t 2 -d $cwd/../ --dimension 128