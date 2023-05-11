from src.file_storing import store_json
from src.testing import tests
from src.autosched import sched_enum, get_schedules_unfused, get_schedules
from src.config import Config
from src.solver_config import Solver_Config
from src.visitor import PrintConfigVisitor
# from src.gen_taco_rep import Write_Test_Code
import sys
from copy import deepcopy
import re

get_schedule_func = "get_schedules_unfused"
# get_schedule_func = "get_schedules"
# get_schedule_func = "sched_enum"

def print_example():
    print("Example execution:")
    print("\tpython3 -m src.main_store_json test1.json test2.json test3.json 1 2 3")
    print("\tThis runs tests 1, 2 and 3 and stores them in the respective json files")


def print_to_json(test_to_run, filename):
    assert type(filename) == str
    assert type(test_to_run) == dict
    # for test_num in tests_to_run:
    # file_ptr = open(filename, 'w')
    schedules = []
    output = test_to_run["output_tens"]
    expr = list(test_to_run["accesses"].keys())
    expr.remove(output)
    expr = tuple(expr)
    
    indices = set()
    for val in test_to_run["accesses"].values(): indices = indices.union(val)
    
    cache = {}
    if get_schedule_func == "get_schedules_unfused":
        schedules = get_schedules_unfused(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(
        indices), test_to_run["tensor_idx_order_constraints"], 1, cache)
    elif get_schedule_func == "get_schedules":
        schedules = get_schedules(output, test_to_run["accesses"][output], expr, test_to_run["accesses"], tuple(
            indices), test_to_run["tensor_idx_order_constraints"], 0, len(expr), 1, cache)
    elif get_schedule_func == "sched_enum":
        sched_enum(output, expr, test_to_run["accesses"][output], test_to_run
                  ["accesses"], test_to_run["tensor_idx_order_constraints"], schedules)
    else:
        print("No scheduling function input", file=sys.stderr)
        exit()
    
    solver = Solver_Config(
        test_to_run["accesses"], test_to_run["tensor_idx_order_constraints"])
    
    pruned_schedules = solver.prune_using_depth(schedules)
    pruned_schedules = solver.prune_schedules(pruned_schedules)
    
    store_json(test_to_run["accesses"], pruned_schedules, filename)
    
    # file_ptr.close()
    # printer = PrintConfigVisitor(test_to_run["accesses"])
    # printer = PrintConfigVisitor(tests[test_num]["accesses"])
    # print('\n\n\n\n\n\n\n', file=file_ptr)
    # print(len(schedules), file=file_ptr)

    # print('\n\n\n\n\n\n\n', file=file_ptr)
    # pruned_schedules = solver.prune_using_depth(schedules)
    # print(len(pruned_schedules))
    # pruned_schedules = solver.prune_schedules(pruned_schedules)
    
    # print(len(pruned_schedules), file=file_ptr)

    # print('/**************************************************************************/', file=file_ptr)
    # print('/********************** PRINTING SCHEDULES ********************************/', file=file_ptr)
    # print('/**************************************************************************/', file=file_ptr)

    # for schedule in pruned_schedules:
    #     schedule.accept(printer)
    #     # Gen_Test_Code(schedule, "TEST", file_ptr)
    #     print('-----------', file=file_ptr)
    



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
    tests_to_run = []
    
    for arg in sys.argv[1:int((len(sys.argv) + 1) / 2)]:
        assert re.match(".*\.json", arg) != None
        filenames.append(arg)
    for arg in sys.argv[int((len(sys.argv) + 1) / 2):]:
        assert re.match("[0-9]+", arg) != None
        assert int(arg) < len(tests)
        tests_to_run.append(tests[int(arg)])
    
    assert len(set(filenames)) == len(filenames) 
        
    for test_to_run, filename in zip(tests_to_run, filenames):
        print_to_json(test_to_run, filename)
    
    
    

