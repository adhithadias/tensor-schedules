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
import time

# enumerate_all_order = True


get_schedule_func = "get_schedules_unfused"
# get_schedule_func = "get_schedules"
# get_schedule_func = "sched_enum"

def get_time(start_time):
  return round(time.time() - start_time, 4)

def print_to_json(test_to_run, testnum, filename):
    assert type(filename) == str
    assert type(test_to_run) == dict
    # for test_num in tests_to_run:
    # file_ptr = open(filename, 'w')
    print("---------------------------------------------------")
    test_start_time = time.time()
    print(f'Running TEST {testnum}\n')
    schedules = []
    output = test_to_run["output_tens"]
    expr = list(test_to_run["accesses"].keys())
    expr.remove(output)
    expr = tuple(expr)
    
    # indices = set()
    # for val in test_to_run["accesses"].values(): indices = indices.union(val)
    indices = []
    tensors = deepcopy(test_to_run["accesses"])
    del tensors[test_to_run["output_tens"]]
    
    for val in tensors.values():
        for index in val:
            if index not in indices: indices.append(index)
    
    cache = {}
    
    
    # initialize Z3 solver
    solver = Solver_Config(
        test_to_run["accesses"], test_to_run["tensor_idx_order_constraints"])
    
    print(f'Enumerating schedules with loop order {" ".join(indices)}')
    
    if get_schedule_func == "get_schedules_unfused":
        # if enumerate_all_order == False:
        schedules = get_schedules_unfused(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(indices), test_to_run["tensor_idx_order_constraints"], 1, cache)
        # else:
        #   idx_perms = get_permutations_of_idx_list(list(indices))
        #   idx_perms = [idx_perm for idx_perm in idx_perms if is_valid_idx_perm(
        #       idx_perm, test_to_run["tensor_idx_order_constraints"], expr, output)]
          
        #   pruned_schedules = []
        #   for idx_perm in idx_perms:
        #       print(f'Getting schedules with loop order {" ".join(idx_perm)}:')
        #       schedules = get_schedules_unfused(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], idx_perm, test_to_run["tensor_idx_order_constraints"], 1, cache)
              
        #       depth_start_time = time.time()
        #       print(f'\tPruning schedules using depth')
        #       schedules = solver.prune_using_depth(schedules)
        #       print(f'\t{len(schedules)} schedule(s) unpruned in {get_time(depth_start_time)} seconds')
              
        #       z3_start_time = time.time()
        #       print(f'\tPruning schedules using Z3')
        #       schedules = solver.prune_schedules(schedules)
        #       print(f'\t{len(schedules)} schedule(s) unpruned in {get_time(z3_start_time)} seconds\n')
        #       pruned_schedules.extend(schedules)
        #   # print(f'{len(pruned_schedules)} schedule(s) unpruned in {get_time()}')
        #   schedules = pruned_schedules
            
    elif get_schedule_func == "get_schedules":
        schedules = get_schedules(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(
            indices), test_to_run["tensor_idx_order_constraints"], 0, len(expr), 1, cache)
    elif get_schedule_func == "sched_enum":
        sched_enum(output, expr, test_to_run["accesses"][output], test_to_run
                  ["accesses"], test_to_run["tensor_idx_order_constraints"], schedules)
    else:
        print("No scheduling function input", file=sys.stderr)
        exit()
    print(f'{len(schedules)} schedule(s) enumerated in {get_time(test_start_time)} seconds\n')
    
    memory_depth_start_time = time.time()
    print(f'Pruning schedules using memory depth')
    pruned_schedules = solver.prune_using_memory_depth(schedules, 2)
    print(f'{len(pruned_schedules)} schedule(s) unpruned ({get_time(memory_depth_start_time)} seconds)\n')
    
    depth_start_time = time.time()
    print(f'Pruning schedules using depth')
    pruned_schedules = solver.prune_using_depth(pruned_schedules)
    print(f'{len(pruned_schedules)} schedule(s) unpruned ({get_time(depth_start_time)} seconds)\n')
    
    z3_start_time = time.time()
    print(f'Pruning schedules using Z3')
    pruned_schedules = solver.prune_schedules(pruned_schedules)
    
    store_json(test_to_run["accesses"], pruned_schedules, filename)
    print(f'{len(pruned_schedules)} schedule(s) stored to {filename} ({get_time(z3_start_time)} seconds)\n')
    print(f'TEST {test_num} finished in {get_time(test_start_time)} seconds')
    
    for i, config1 in enumerate(pruned_schedules):
        for j, config2 in enumerate(pruned_schedules):
            if i == j: continue
            if config1 == config2:
                print(config1)
        
    



if __name__ == "__main__":
    main_store_json = Main_Store_JSON(sys.argv)
    print_visitor = Print_Help_Visitor()
    main_store_json.accept(print_visitor)
    
    filenames = []
    test_nums = []
    tests_to_run = []
    
    for arg in sys.argv[1:int((len(sys.argv) + 1) / 2)]:
        filenames.append(arg)
    for arg in sys.argv[int((len(sys.argv) + 1) / 2):]:
        test_nums.append(arg)
        tests_to_run.append(tests[int(arg)])
    
    assert len(set(filenames)) == len(filenames) 
        
    for test_to_run, test_num, filename in zip(tests_to_run, test_nums, filenames):
        print_to_json(test_to_run, test_num, filename)
    

