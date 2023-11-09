import itertools
import sys
from copy import deepcopy
from time import time
import argparse
from typing import Optional, Sequence
import json
from math import floor, ceil
from multiprocessing import Process, Lock

from src.prune import prune_using_memory_depth
from src.util import remove_duplicates
from src.file_storing import store_json
from src.testing import tests
from src.autosched import sched_enum, get_schedules_unfused, get_schedules
from src.config import Config
from src.solver_config import Solver_Config
from src.visitor import PrintConfigVisitor
from src.util import *
from src.print_help import Main_Store_JSON, Print_Help_Visitor
from copy import deepcopy

# enumerate_all_order = True


def print_message(text):
    if messages: print(text, flush=True)

def convert_sec_min_sec(seconds) -> list:
    """converts seconds into minutes and seconds

    Args:
        seconds (number): number of seconds to convert
    """
    return [floor(seconds / 60), round(seconds - (floor(seconds / 60) * 60), 3)]
  
def print_time_message(message:str, start_time, newline=False, process_num = 0):
    total_time = convert_sec_min_sec(get_time(start_time))
    if newline:
        print_message(f'{process_num}: {message} in {total_time[0]} minutes and {total_time[1]} seconds\n')
    else:
        print_message(f'{process_num}: {message} in {total_time[0]} minutes and {total_time[1]} seconds')

def get_time(start_time):
  return round(time() - start_time, 4)
        
def f(output_tensor, accesses, expr, indices, tensor_idx_order_constraints, schedules, l, i):
    output_tensor = deepcopy(output_tensor)
    accesses = deepcopy(accesses)
    expr = deepcopy(expr)
    indices = deepcopy(indices)
    tensor_idx_order_constraints = deepcopy(tensor_idx_order_constraints)
    
    t = time()
    cache = {}
    s = get_schedules(output_tensor, accesses[output_tensor], expr, accesses, tuple(
        indices), tensor_idx_order_constraints, 0, len(expr), 1, cache)
    
    del cache
    
    print_time_message(f'{i} : adding to the schedules: {len(s)}, expr: {expr}', t, True)
    
    memory_depth_start_time = time()
    print_message(f'{i}: Pruning {len(s)} schedules using memory depth')
    s = prune_using_memory_depth(s, 2)
    print_time_message(f'{i}: {len(s)} schedule(s) unpruned', memory_depth_start_time, True)
    
    l.acquire()
    try:
        schedules.extend(s)
        print_time_message(f'{i}: -----------------', t, True)
    finally:
        l.release()

    
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
    
    input_permutations = []
    for p in itertools.permutations(expr):
        if p <= p[::-1] and expr != p:
            input_permutations.append(p)
    print('Input permutations: ', len(input_permutations))    
    
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
    
    del cache
    
    memory_depth_start_time = time()
    print_message(f'Pruning schedules using memory depth')
    schedules = solver.prune_using_memory_depth(schedules, 2)
    print_time_message(f'{len(schedules)} schedule(s) unpruned', memory_depth_start_time, True)

    schedules = list(schedules)
    
    processes = [i for i in range(len(input_permutations))]
    number_of_processes = 15
    
    lock = Lock()
    
    for j in range(ceil(len(input_permutations) / number_of_processes)):
        
        start = j * number_of_processes
        end = min((j + 1) * number_of_processes, len(input_permutations))
        
        for n in range(start, end):
            p = Process(target=f, args=(output_tensor, accesses, input_permutations[n], tuple(indices), tensor_idx_order_constraints, schedules, lock, n))
            processes[n] = p
            processes[n].start()
            
        for n in range(start, end):
            processes[n].join()
            print(f'{n}: Process {n} joined')
    
    # for i, expr in enumerate(input_permutations):
    #     t = time()
    #     cache = {}
    #     s = get_schedules(output_tensor, accesses[output_tensor], expr, accesses, tuple(
    #         indices), tensor_idx_order_constraints, 0, len(expr), 1, cache)
        
    #     del cache
        
    #     print_time_message(f'{i} : adding to the schedules: {len(s)}, expr: {expr}', t, True)
        
    #     memory_depth_start_time = time()
    #     print_message(f'Pruning schedules using memory depth')
    #     s = solver.prune_using_memory_depth(s, 2)
    #     print_time_message(f'{len(s)} schedule(s) unpruned', memory_depth_start_time, True)
        
    #     schedules.extend(s)
    #     print_time_message(f'-----------------', t, True)
    
    remove_duplicates_start_time = time()
    print_message(f'Removing duplicates')
    pruned_schedules = remove_duplicates(schedules)
    print_time_message(f'{len(pruned_schedules)} schedule(s) left after removing duplicates', remove_duplicates_start_time, True)
        
    depth_start_time = time()
    print_message(f'Pruning schedules using depth')
    pruned_schedules = solver.prune_using_depth(pruned_schedules)
    print_time_message(f'{len(pruned_schedules)} schedule(s) unpruned', depth_start_time, True)
    
    print('-----------------')
    
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
    