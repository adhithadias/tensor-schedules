#!/bin/bash

cwd=$(pwd)

python3 -m src.main_store_json -f test3_config.json -r
python3 -m src.main_store_json_z3 -f test3_config.json -r
python3 -m src.main_run_test_modified -f test3_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test3_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 3 -r 30 --directory $cwd/..

# python3 -m src.main_store_json -f test4_config.json -r
# python3 -m src.main_store_json_z3 -f test4_config.json -r
python3 -m src.main_run_test_modified -f test4_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test4_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 4 -r 30 --directory $cwd/..

# python3 -m src.main_store_json -f test7_config.json -r
# python3 -m src.main_store_json_z3 -f test7_config.json -r
python3 -m src.main_run_test_modified -f test7_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test7_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 7 -r 30--directory $cwd/..

python3 -m src.main_store_json -f test8_config.json -r
python3 -m src.main_store_json_z3 -f test8_config.json -r
python3 -m src.main_run_test_modified -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 8 -r 30 --directory $cwd/..

# python3 -m src.main_store_json -f test2_config.json -r
# python3 -m src.main_store_json_z3 -f test2_config.json -r
python3 -m src.main_run_test_modified -f test2_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test2_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 2 -r 0 --directory $cwd/..

# python3 -m src.main_store_json -f test5_config.json -r
# python3 -m src.main_store_json_z3 -f test5_config.json -r
python3 -m src.main_run_test_modified -f test5_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test5_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 5 -r 0 --directory $cwd/..

# python3 -m src.main_store_json -f test6_config.json -r
# python3 -m src.main_store_json_z3 -f test6_config.json -r
python3 -m src.main_run_test_modified -f test6_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 scripts/plot_graph.py -t 6 -r 0 --directory $cwd/..

# python3 -m src.main_store_json -f test9_config.json -r
# python3 -m src.main_store_json_z3 -f test9_config.json -r
python3 -m src.main_run_test_modified -f test9_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test9_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 scripts/plot_graph.py -t 9 -r 0 --directory $cwd/..

# combine all plots to create the main plot
python3 scipts/plot_graph_combine.py --directory $cwd/..