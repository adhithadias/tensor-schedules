#!/bin/bash

./download_tensors.sh

cwd=$(pwd)

python3 -m src.main_store_json -f test3_config.json -r
python3 -m src.main_store_json_z3 -f test3_config.json -r
python3 -m src.main_run_test_modified -f test3_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test3_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 3 -r 30

python3 -m src.main_store_json -f test4_config.json -r
python3 -m src.main_store_json_z3 -f test4_config.json -r
python3 -m src.main_run_test_modified -f test4_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test4_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 4 -r 30

python3 -m src.main_store_json -f test7_config.json -r
python3 -m src.main_store_json_z3 -f test7_config.json -r
python3 -m src.main_run_test_modified -f test7_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test7_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 7 -r 30

python3 -m src.main_store_json -f test8_config.json -r
python3 -m src.main_store_json_z3 -f test8_config.json -r
python3 -m src.main_run_test_modified -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 8 -r 30

python3 -m src.main_store_json -f test2_config.json -r
python3 -m src.main_store_json_z3 -f test2_config.json -r
python3 -m src.main_run_test_modified -f test2_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test2_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 2 -r 0

python3 -m src.main_store_json -f test5_config.json -r
python3 -m src.main_store_json_z3 -f test5_config.json -r
python3 -m src.main_run_test_modified -f test5_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test5_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 5 -r 0

python3 -m src.main_store_json -f test6_config.json -r
python3 -m src.main_store_json_z3 -f test6_config.json -r
python3 -m src.main_run_test_modified -f test6_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 plot_graph.py -t 6 -r 0

python3 -m src.main_store_json -f test9_config.json -r
python3 -m src.main_store_json_z3 -f test9_config.json -r
python3 -m src.main_run_test_modified -f test9_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 1 -m -x
python3 -m src.main_run_test_modified -f test9_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -n 32 -m -x
python3 plot_graph.py -t 9 -r 0

# combine all plots to create the main plot
python plot_graph_combine.py

# comparison against willow
python test_willow.py --directory $cwd/..  &> ./logs/test_willow.log
python test_willow_plot.py --directory $cwd --test-name spmm_gemm_real &> ./logs/test_willow_plot.log
python test_willow_plot.py --directory $cwd --test-name spttm_spttm_real &> ./logs/test_willow_plot.log

# comparison against SpTTN
python ttmc_compare.py --directory=$cwd/.. &> ./logs/ttmc_compare.log

# plot the comparison results
python ttmc_compare_line_plot.py -t 1 --directory $cwd/..
python ttmc_compare_line_plot.py -t 2 --directory $cwd/..

plot all graphs execution times
python3 -m src.main_run_test_all_schedules -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -m -x -e 64 --timeout 5
python plot_all_times.py -t 1 -d $cwd/../ --dimension 64

python3 -m src.main_run_test_all_schedules -f test8_config.json -t $cwd/downloads/ -p $cwd/../sparseLNR -m -x -e 128 --timeout 15
python plot_all_times.py -t 2 -d $cwd/../ --dimension 128


scale plots
python scaling_exec_replace.py --directory $cwd/..
scaling_exec.sh &> scaling.txt
python3 scaling_exec.py --directory $cwd
python3 plot_scale_graph.py --directory $cwd -t 1
python3 plot_scale_graph.py --directory $cwd -t 2
