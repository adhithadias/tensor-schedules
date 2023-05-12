from src.file_storing import store_json
from src.testing import tests
from src.autosched import sched_enum, get_schedules_unfused, get_schedules
from src.config import Config
from src.solver_config import Solver_Config
from src.visitor import PrintConfigVisitor
from src.util import *
# from src.gen_taco_rep import Write_Test_Code
import itertools
import sys
from copy import deepcopy
import re
import time

get_schedule_func = "get_schedules_unfused"
# get_schedule_func = "get_schedules"
# get_schedule_func = "sched_enum"

def print_example():
    print("python3 -m src.main_store_json [json file(s)] [test number(s)]")
    print("Example execution:")
    print("\tpython3 -m src.main_store_json test1.json test2.json test3.json 1 2 3")
    print("\tThis runs tests 1, 2 and 3 and stores them in the respective json files")


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
    
    # idx_perms = get_permutations_of_idx_list(list(indices))
    # print(loop_order, len(idx_perms), flush=True)
    # idx_perms = [idx_perm for idx_perm in idx_perms if is_valid_idx_perm(
    #     idx_perm, test_to_run["tensor_idx_order_constraints"], expr, output)]
    
    # initialize Z3 solver
    solver = Solver_Config(
        test_to_run["accesses"], test_to_run["tensor_idx_order_constraints"])
    
    print(f'Enumerating schedules with loop order {" ".join(indices)}')
    
    if get_schedule_func == "get_schedules_unfused":
        schedules = get_schedules_unfused(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(indices), test_to_run["tensor_idx_order_constraints"], 1, cache)
        
        # pruned_schedules = []
        # for idx_perm in idx_perms:
        #     print(f'Getting schedules with loop order {" ".join(idx_perm)}:')
        #     schedules = get_schedules_unfused(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], idx_perm, test_to_run["tensor_idx_order_constraints"], 1, cache)
            
        #     print(f'\tPruning schedules using depth')
        #     schedules = solver.prune_using_depth(schedules)
        #     print(f'\t{len(schedules)} schedule(s) unpruned')
        #     print(f'\tPruning schedules using Z3')
        #     schedules = solver.prune_schedules(schedules)
        #     print(f'\t{len(schedules)} schedule(s) unpruned\n')
        #     pruned_schedules.extend(schedules)
        # print(f'{len(pruned_schedules)} schedule(s) unpruned')
            
    elif get_schedule_func == "get_schedules":
        schedules = get_schedules(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(
            indices), test_to_run["tensor_idx_order_constraints"], 0, len(expr), 1, cache)
    elif get_schedule_func == "sched_enum":
        sched_enum(output, expr, test_to_run["accesses"][output], test_to_run
                  ["accesses"], test_to_run["tensor_idx_order_constraints"], schedules)
    else:
        print("No scheduling function input", file=sys.stderr)
        exit()
    print(f'{len(schedules)} schedule(s) enumerated in {round(time.time() - test_start_time, 4)} seconds\n')
    
    depth_start_time = time.time()
    print(f'Pruning schedules using depth')
    pruned_schedules = solver.prune_using_depth(schedules)
    print(f'{len(pruned_schedules)} schedule(s) unpruned ({round(time.time()-depth_start_time, 4)} seconds)\n')
    
    z3_start_time = time.time()
    print(f'Pruning schedules using Z3')
    pruned_schedules = solver.prune_schedules(pruned_schedules)
    
    store_json(test_to_run["accesses"], pruned_schedules, filename)
    print(f'{len(pruned_schedules)} schedule(s) stored to {filename} ({round(time.time() - z3_start_time,4)} seconds)\n')
    print(f'TEST {test_num} finished in {round(time.time() - test_start_time, 4)} seconds')
    



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Invalid arguments given.  Give file name(s) and test number(s) as command line arguments\n", file=sys.stderr)
        print_example()
        exit()
    elif sys.argv[1].lower() == "help":
        print_example()
        exit()
    elif (len(sys.argv) + 1) % 2: 
        print("Invalid arguments given.  Give file name(s) and test number(s) as command line arguments\n", file=sys.stderr)
        print_example()
        exit()
    
    filenames = []
    test_nums = []
    tests_to_run = []
    
    for arg in sys.argv[1:int((len(sys.argv) + 1) / 2)]:
        assert re.match(".*\.json", arg) != None
        filenames.append(arg)
    for arg in sys.argv[int((len(sys.argv) + 1) / 2):]:
        assert re.match("[0-9]+", arg) != None
        assert int(arg) < len(tests)
        test_nums.append(arg)
        tests_to_run.append(tests[int(arg)])
    
    assert len(set(filenames)) == len(filenames) 
        
    for test_to_run, test_num, filename in zip(tests_to_run, test_nums, filenames):
        print_to_json(test_to_run, test_num, filename)
    

