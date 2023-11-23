#!/bin/bash

date=$(date +%Y-%m-%d_%H-%M-%S)

python3 -m src.main_run_test_modified -f test2_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test2_run_$date.txt
python3 -m src.main_run_test_modified -f test3_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test3_run_$date.txt
python3 -m src.main_run_test_modified -f test4_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test4_run_$date.txt
python3 -m src.main_run_test_modified -f test5_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test5_run_$date.txt
python3 -m src.main_run_test_modified -f test6_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test6_run_$date.txt
python3 -m src.main_run_test_modified -f test7_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test7_run_$date.txt
python3 -m src.main_run_test_modified -f test8_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test8_run_$date.txt
python3 -m src.main_run_test_modified -f test9_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x &> logs/test9_run_$date.txt
