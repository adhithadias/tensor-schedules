import functools
import sys
from copy import deepcopy
from time import time
import argparse
from typing import Optional, Sequence
import json
from math import floor

from src.file_storing import store_json, store_baskets_to_json, read_json
from src.config import Config
from src.solver_config import Solver_Config
from src.visitor import PrintConfigVisitor
from src.basket import Baskets
from src.cache import add_cache_locality


def print_message(text):
    if messages: print(text, flush=True)

def convert_sec_min_sec(seconds) -> list:
    """converts seconds into minutes and seconds

    Args:
        seconds (number): number of seconds to convert
    """
    return [floor(seconds / 60), round(seconds - (floor(seconds / 60) * 60), 3)]
  
def print_time_message(message:str, start_time, newline=False):
    total_time = convert_sec_min_sec(get_time(start_time))
    if newline:
        print_message(f'{message} in {total_time[0]} minutes and {total_time[1]} seconds\n')
    else:
        print_message(f'{message} in {total_time[0]} minutes and {total_time[1]} seconds')

def get_time(start_time):
  return round(time() - start_time, 4)
        
    
    
def print_to_json2(accesses:dict, tensor_idx_order_constraints:dict, output_tensor:str, read_json_file:str, write_json_file: str, testnum:int, get_schedule_func:str, z3_constraints=None):
    print_message("---------------------------------------------------")
    print_message(f'Pruning schedules {testnum}\n')
    schedules = []
    expr = list(accesses.keys())
    expr.remove(output_tensor)
    expr = tuple(expr)
    
    indices = []
    tensors = deepcopy(accesses)
    del tensors[output_tensor]
    
    for val in tensors.values():
        for index in val:
            if index not in indices: indices.append(index)
    
    # initialize Z3 solver
    solver = Solver_Config(
        accesses, tensor_idx_order_constraints, z3_constraints)
    
    print_message(f'Reading config {read_json_file}')
    pruned_schedules = read_json(read_json_file)
    
    test_start_time = time()
    print_message(f'Creating baskets for {len(pruned_schedules)} schedules')
    baskets = Baskets(pruned_schedules)
    print_time_message(f'{len(baskets)} basket(s) created', test_start_time, True)
    
    z3_start_time = time()
    print_message(f'Pruning {len(baskets)} baskets using Z3')
    pruned_baskets = solver.prune_baskets(baskets)
    pruned_baskets = Baskets(pruned_baskets)
    for i, (tc, mc, l) in enumerate(pruned_baskets.get_baskets()):
        print(f'basket {i}: {tc} {mc} {len(l)}')
    print_time_message(f'{len(pruned_baskets)} baskets(s) exists after Z3 pruning', z3_start_time, True)
    
    no_z3_pruned_schedules = functools.reduce(lambda a, b: a+b, [len(schedules) for _, _, schedules in pruned_baskets])
    
    # locality_pruning_start_time = time()
    # print_message(f'Pruning schedules with same complexity using Z3')
    # pruned_schedules = solver.prune_same_loop_nest(pruned_schedules)
    # print_time_message(f'{len(pruned_schedules)} schedule(s) unpruned', locality_pruning_start_time, True)
    
    # print(solver.get_leaf_configs(pruned_schedules[0], []), file=sys.stdout)
    # print(pruned_schedules[0], file=sys.stdout)
    
    add_cache_locality(accesses, pruned_baskets)
    
    store_baskets_to_json(accesses, pruned_baskets, write_json_file)
    print_time_message(f'{no_z3_pruned_schedules} schedule(s) stored to {write_json_file}', z3_start_time, True)
    print_time_message(f'TEST {testnum} finished', test_start_time)
    
def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', '--config_files', help='json formatted configuration file(s) with the following key-value pairs required:\n\t\taccesses:\n\t\t\t\t[tensor]: list[indices]\n\t\ttensor_idx_order_constraints:\n\t\t\t\t[tensor]: list[list[indices]]\n\t\toutput_tensor: [tensor]\n\t\ttest_json_file: [json file to store configs into]\n\t\t(optional) z3_constraints: list[constraints]', required=True, nargs="+")
    parser.add_argument('-o', '--function_type', default='get_schedules_unfused', help='optional argument to change function for generating schedules (default: %(default)s)', choices=['get_schedules_unfused', 'get_schedules', 'sched_enum'])
    parser.add_argument('-r', '--messages', action='store_true', help='enable printing of progress')
    
    TEST_JSON_FILE_LOCATION = "test_schedules/"
    CONFIG_FILE_LOCATION = "test_configs/"
    
    args = vars(parser.parse_args(argv))
    config_files = args["config_files"]
    config_files = [CONFIG_FILE_LOCATION + config_file for config_file in config_files] # read from test_configs folder
    function_type = args["function_type"]
    global messages
    messages = args["messages"]
    for i,config_file in enumerate(config_files):
        try:
            fileptr = open(config_file, "r")
            new_dict = json.load(fileptr)
            fileptr.close()
        except OSError:
            print("Invalid JSON file for reading", file=sys.stderr)
            return
        
        accesses = new_dict["accesses"]
        for key,value in accesses.items():
            accesses[key] = tuple(value)
            
        tensor_idx_order_constraints = new_dict["tensor_idx_order_constraints"]
        for key,value in tensor_idx_order_constraints.items():
            tensor_idx_order_constraints[key] = [tuple(inner_list) for inner_list in value]
        output_tensor = new_dict["output_tensor"]
        read_json_file = new_dict["test_json_file"]
        read_json_file = TEST_JSON_FILE_LOCATION + read_json_file     # place in tensors_stored folder
        write_json_file = new_dict["test_json_file_after_z3"]
        write_json_file = TEST_JSON_FILE_LOCATION + write_json_file
        try:
            z3_constraints = new_dict["z3_constraints"]
        except:
            z3_constraints = ""
        
        print_to_json2(accesses, tensor_idx_order_constraints, output_tensor, read_json_file, write_json_file, i, function_type, z3_constraints)


if __name__ == "__main__":
    exit(main())
    