#!/bin/bash

cwd=$(pwd)

python3 -m src.main_store_json -f test3_config.json -r
python3 -m src.main_store_json_z3 -f test3_config.json -r
python3 -m src.main_run_test_modified -f test3_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test3_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 3 -r 30 --directory $cwd/..
