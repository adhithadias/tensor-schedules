import subprocess
import argparse
from typing import Optional, Sequence
import sys
import re
import os
import csv
from time import time
from copy import deepcopy
from statistics import mean, stdev
from src.gen_taco_rep import Write_Test_Code
from src.config import Config
from src.file_storing import read_json
from src.print_help import Main_Run_Test, Print_Help_Visitor, is_valid_file_type
from src.visitor import PrintConfigVisitor
from src.testing import tests

# incomplete argument
run_arg = "workspaces._"

def get_arg(test): return re.sub("_", test, deepcopy(run_arg))

def print_idx_orders(config:Config, num_indent = 0):
    if config == None: return
    print("\t" * num_indent + str(config.original_idx_perm))
    print_idx_orders(config.prod, num_indent + 1)
    print_idx_orders(config.cons, num_indent + 1)
    




def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description='Tests time of various fused and unfused schedules as found by autoscheduler.', usage="python3 -m src.main_run_test.py -o [csv test file(s)] -f [json test file(s)] -t [test name(s)] [optional args]")
    
    parser.add_argument('-c', '--test_file', help='cpp file to write scheduling code into', default="tests-workspaces.cpp")
    parser.add_argument('-o', '--output_files', help='csv file(s) for writing tests into', nargs='+', required=True)
    parser.add_argument('-f', '--json_files', help='json file(s) to read configs from', nargs='+', required=True)
    parser.add_argument('-t', '--test_names', help='name of corresponding test(s)', nargs='+', required=True)
    parser.add_argument('-n', '--num_tests', help='number of tests for each config to run', type=int, default=100)
    parser.add_argument('-p', '--path', help='path to taco directory', default="../SparseLNR_Most_Recent")
    parser.add_argument('-d', '--debug', action='store_true', help='enable debugging')
    parser.add_argument('-r', '--messages', action='store_true', help='enable printing of progress')
    
    args = vars(parser.parse_args(argv))
    path_root = args['path']
    test_file = f'{path_root}/test/{args["test_file"]}'
    output_files = args['output_files']
    json_files = args['json_files']
    test_names = args['test_names']
    num_tests = args['num_tests']
    path_root = args['path']
    debug = args['debug']
    messages = args['messages']
    
    print(test_file)
    # relative path to Makefile
    path_makefile = path_root + "/build"

    # relative path to taco-test executable
    path_test = path_makefile + "/bin/taco-test"

    # Makefile command to run
    command = "make taco-test/fast"
    
    # number of tests must match
    assert len(output_files) == len(json_files) and len(output_files) == len(test_names)
    
    # print(output_files, json_files, test_names)  
    
    program_start_time = time()
    # run tests for each test case
    for out_file, json_file, test_name in zip(output_files, json_files, test_names):
        time_test_start = time()
        
        # make sure file types are correct
        if not is_valid_file_type(out_file, "csv"): continue
        if not is_valid_file_type(json_file, "json"): continue
        config_list = read_json(json_file)
        
        # for i, config1 in enumerate(config_list):
        #     for j, config2 in enumerate(config_list):
        #         if i == j: continue
        #         if config1 == config2: print(config1)
        # exit()
        
        existing_schedules = {}
        
        with open(out_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            list_times = ["Time " + str(num + 1) for num in range(num_tests)]
            # print(len(list_times))
            header_row = ['Schedule', 'Commands']
            header_row.extend(list_times)
            header_row.append("Average Runtime")
            header_row.append("Runtime Standard Dev")
            
            writer.writerow(header_row)
        
            for iter, config in enumerate(config_list):
                # write testing code into testing file
                test_code = Write_Test_Code(config, test_name, test_file)
                # compiles with changed config
                make_output = subprocess.Popen(f'(cd {path_makefile} && {command})', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                
                # wait for compilation to finish
                make_output.wait()
                if messages: print(f'Config {iter + 1}/{len(config_list)} test compiled')
                
                # individual times to compute for given schedule
                output_times = []
                
                start_time = time()
                
                # statement in the form forall(i, forall, j, where(etc.))
                schedule_stmt = ""
                
                # get list of scheduling commands
                schedule_commands = []
                for line in test_code.schedule_text:
                    match_ob = re.search("(reorder\(.*\))|(loopfuse\(.*\))|(vector\<int\>.*;)", line)
                    if match_ob:
                        if match_ob.groups()[0] != None: schedule_commands.append(match_ob.groups()[0])
                        elif match_ob.groups()[1] != None: schedule_commands.append(match_ob.groups()[1])
                        else: schedule_commands.append(match_ob.groups()[2])
                
                # print(existing_schedules[tuple(schedule_commands)])
                if debug and tuple(schedule_commands) in existing_schedules.keys():
                    print()
                    print("\n".join(schedule_commands))
                    print()
                    print_idx_orders(config)
                    print()
                    visitor = PrintConfigVisitor(tests[0]["accesses"])
                    config.accept(visitor)
                    print()
                    print_idx_orders(existing_schedules[tuple(schedule_commands)])
                    existing_schedules[tuple(schedule_commands)].accept(visitor)
                    
                    exit()
                existing_schedules[tuple(schedule_commands)] = config
                
                # outer for loop here
                for test_iter in range(num_tests):
                    # runs test
                    test_output = subprocess.Popen(f'{path_test} {get_arg(test_name)}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                    
                    # wait for output to generate
                    test_output.wait()
                    
                    stdout_lines = test_output.stdout.readlines()
                    stderr_lines = test_output.stderr.readlines()
                    
                    if test_iter == 0:
                        if stderr_lines:
                            print("".join(stdout_lines))
                            print("".join(test_code.schedule_text))
                            print()
                            print("".join(stderr_lines))
                            print()
                            visitor = PrintConfigVisitor(tests[0]["accesses"])
                            config.accept(visitor)
                            exit()
                        
                        if debug and not re.search("PASSED", stdout_lines[-1]):
                            print(f'Config {iter + 1} Test Failed')
                            print("".join(stdout_lines))
                            print("".join(test_code.schedule_text))
                            print()
                            print("".join(stderr_lines))
                            print()
                            # print("".join(test_code.schedule_text))
                            # print()
                            visitor = PrintConfigVisitor(tests[0]["accesses"])
                            config.accept(visitor)
                            print_idx_orders(config)
                            exit()
                        
                        # gets schedule statement of given schedule
                        schedule_stmt = re.sub("final stmt: ", "", stdout_lines[6])
                      
                    time_to_run = re.search("(\d+) ms total", stdout_lines[-2]).groups()[0]
                    output_times.append(time_to_run)
                if messages: print(f'Config {iter + 1} Test Passed With 0 Errors in {round(time() - start_time, 3)} seconds')
                # print(schedule_stmt, schedule_commands)
                # print(output_times)
                # print(re.sub(",", "\",\"", schedule_stmt))
                del test_code
                
                schedule_stmt = re.sub("\n", "", schedule_stmt)
                new_row = [schedule_stmt, "\n".join(schedule_commands)]
                new_row.extend(output_times)
                int_times = [int(output_time) for output_time in output_times]
                new_row.extend([mean(int_times), stdev(int_times)])
                writer.writerow(new_row)
                if messages: print()
                
                # break
                
                # print()
                # print(stdout_lines[6])
                # print(stdout_lines[7])
                # print(test_output.stderr.readlines())
                
                # break
        if messages: print(f'{test_name} test finished in {round(time() - time_test_start, 3)} seconds')
    if messages: print(f'All tests ran in {round(time() - program_start_time, 3)} seconds')
        
if __name__ == "__main__":
    exit(main())
