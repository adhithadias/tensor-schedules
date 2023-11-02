from src.file_storing import store_json
from src.testing import tests
from src.autosched import sched_enum, get_schedules_unfused, get_schedules
from src.config import Config
from src.solver_config import Solver_Config
from src.visitor import PrintConfigVisitor
from src.util import *
from src.print_help import Main_Store_JSON, Print_Help_Visitor
# from src.gen_taco_rep import Write_Test_Code
import itertools
import sys
from copy import deepcopy
import re
from time import time
import argparse
from typing import Optional, Sequence
import json
from math import floor

# enumerate_all_order = True


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

# def print_to_json(test_to_run, testnum, filename):
#     assert type(filename) == str
#     assert type(test_to_run) == dict
#     # for test_num in tests_to_run:
#     # file_ptr = open(filename, 'w')
#     print("---------------------------------------------------")
#     test_start_time = time()
#     print(f'Running TEST {testnum}\n')
#     schedules = []
#     output = test_to_run["output_tens"]
#     expr = list(test_to_run["accesses"].keys())
#     expr.remove(output)
#     expr = tuple(expr)
    
#     # indices = set()
#     # for val in test_to_run["accesses"].values(): indices = indices.union(val)
#     indices = []
#     tensors = deepcopy(test_to_run["accesses"])
#     del tensors[test_to_run["output_tens"]]
    
#     for val in tensors.values():
#         for index in val:
#             if index not in indices: indices.append(index)
    
#     cache = {}
    
#     # initialize Z3 solver
#     solver = Solver_Config(
#         test_to_run["accesses"], test_to_run["tensor_idx_order_constraints"], "test2_config.json")
#     print(f'Enumerating schedules with loop order {" ".join(indices)}')
    
#     if get_schedule_func == "get_schedules_unfused":
#         schedules = get_schedules_unfused(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(indices), test_to_run["tensor_idx_order_constraints"], 1, cache)
#     elif get_schedule_func == "get_schedules":
#         schedules = get_schedules(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(
#             indices), test_to_run["tensor_idx_order_constraints"], 0, len(expr), 1, cache)
#     elif get_schedule_func == "sched_enum":
#         sched_enum(output, expr, test_to_run["accesses"][output], test_to_run
#                   ["accesses"], test_to_run["tensor_idx_order_constraints"], schedules)
#     else:
#         print("No scheduling function input", file=sys.stderr)
#         exit()
    
#     total_time = convert_sec_min_sec(get_time(test_start_time))
#     print(f'{len(schedules)} schedule(s) enumerated in {total_time[0]} minutes and {total_time[1]} seconds\n')
    
#     memory_depth_start_time = time()
#     print(f'Pruning schedules using memory depth')
#     pruned_schedules = solver.prune_using_memory_depth(schedules, 2)
#     print(f'{len(pruned_schedules)} schedule(s) unpruned ({get_time(memory_depth_start_time)} seconds)\n')
    
#     depth_start_time = time()
#     print(f'Pruning schedules using depth')
#     pruned_schedules = solver.prune_using_depth(pruned_schedules)
#     print(f'{len(pruned_schedules)} schedule(s) unpruned ({get_time(depth_start_time)} seconds)\n')
    
#     z3_start_time = time()
#     print(f'Pruning schedules using Z3')
#     pruned_schedules = solver.prune_schedules(pruned_schedules)
    
#     store_json(test_to_run["accesses"], pruned_schedules, filename)
#     print(f'{len(pruned_schedules)} schedule(s) stored to {filename} ({get_time(z3_start_time)} seconds)\n')
#     print(f'TEST {testnum} finished in {get_time(test_start_time)} seconds')
    
#     for i, config1 in enumerate(pruned_schedules):
#         for j, config2 in enumerate(pruned_schedules):
#             if i == j: continue
#             if config1 == config2:
#                 print(config1)
        
    
def print_to_json2(accesses:dict, tensor_idx_order_constraints:dict, output_tensor:str, test_json_file:str, testnum:int, get_schedule_func:str, z3_constraints=None):
    print_message("---------------------------------------------------")
    test_start_time = time()
    print_message(f'Running TEST {testnum}\n')
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
    
    cache = {}
    
    # initialize Z3 solver
    solver = Solver_Config(
        accesses, tensor_idx_order_constraints, z3_constraints)
    
    print_message(f'Enumerating schedules with loop order {" ".join(indices)}')
    
    # mostly irrelevant (as only get_schedules_unfused is needed) but generates necessary schedules
    if get_schedule_func == "get_schedules_unfused":
        schedules = get_schedules_unfused(output_tensor, accesses[output_tensor], expr, accesses, tuple(indices), tensor_idx_order_constraints, 1, cache)
    elif get_schedule_func == "get_schedules":
        schedules = get_schedules(output_tensor, accesses[output_tensor], expr, accesses, tuple(
            indices), tensor_idx_order_constraints, 0, len(expr), 1, cache)
    elif get_schedule_func == "sched_enum":
        sched_enum(output_tensor, expr, accesses[output_tensor], accesses, tensor_idx_order_constraints, schedules)
    else:
        print("No scheduling function input", file=sys.stderr)
        exit()
    print_time_message(f'{len(schedules)} schedule(s) enumerated', test_start_time, True)
    
    memory_depth_start_time = time()
    print_message(f'Pruning schedules using memory depth')
    pruned_schedules = solver.prune_using_memory_depth(schedules, 2)
    print_time_message(f'{len(pruned_schedules)} schedule(s) unpruned', memory_depth_start_time, True)
    
    depth_start_time = time()
    print_message(f'Pruning schedules using depth')
    pruned_schedules = solver.prune_using_depth(pruned_schedules)
    print_time_message(f'{len(pruned_schedules)} schedule(s) unpruned', depth_start_time, True)
    
    # z3_start_time = time()
    # print_message(f'Pruning schedules using Z3')
    # pruned_schedules = solver.prune_schedules(pruned_schedules)
    # print_time_message(f'{len(pruned_schedules)} schedule(s) unpruned', z3_start_time, True)
    
    # locality_pruning_start_time = time()
    # print_message(f'Pruning schedules with same complexity using Z3')
    # pruned_schedules = solver.prune_same_loop_nest(pruned_schedules)
    # print_time_message(f'{len(pruned_schedules)} schedule(s) unpruned', locality_pruning_start_time, True)
    
    
    
    # print(solver.get_leaf_configs(pruned_schedules[0], []), file=sys.stdout)
    # print(pruned_schedules[0], file=sys.stdout)
    
    store_json(accesses, pruned_schedules, test_json_file)
    print_time_message(f'{len(pruned_schedules)} schedule(s) stored to {test_json_file}', depth_start_time, True)
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
        test_json_file = new_dict["test_json_file"]
        test_json_file = TEST_JSON_FILE_LOCATION + test_json_file     # place in tensors_stored folder
        try:
            z3_constraints = new_dict["z3_constraints"]
        except:
            z3_constraints = ""
        
        
        
        print_to_json2(accesses, tensor_idx_order_constraints, output_tensor, test_json_file, i, function_type, z3_constraints)


if __name__ == "__main__":
    exit(main())
    