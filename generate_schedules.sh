#!/bin/bash

date=$(date +%Y-%m-%d_%H-%M-%S)

python3 -m src.main_store_json -f test2_config.json -r &> logs/test2_schedule_generation_$date.txt
python3 -m src.main_store_json -f test3_config.json -r &> logs/test3_schedule_generation_$date.txt
python3 -m src.main_store_json -f test4_config.json -r &> logs/test4_schedule_generation_$date.txt
python3 -m src.main_store_json -f test5_config.json -r &> logs/test5_schedule_generation_$date.txt
python3 -m src.main_store_json -f test6_config.json -r &> logs/test6_schedule_generation_$date.txt
python3 -m src.main_store_json -f test7_config.json -r &> logs/test7_schedule_generation_$date.txt
python3 -m src.main_store_json -f test8_config.json -r &> logs/test8_schedule_generation_$date.txt
python3 -m src.main_store_json -f test9_config.json -r &> logs/test9_schedule_generation_$date.txt


python3 -m src.main_store_json_z3 -f test2_config.json -r &> logs/test2_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test3_config.json -r &> logs/test3_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test4_config.json -r &> logs/test4_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test5_config.json -r &> logs/test5_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test6_config.json -r &> logs/test6_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test7_config.json -r &> logs/test7_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test8_config.json -r &> logs/test8_z3_pruning_$date.txt
python3 -m src.main_store_json_z3 -f test9_config.json -r &> logs/test9_z3_pruning_$date.txt