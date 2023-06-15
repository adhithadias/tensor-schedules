import subprocess
import argparse
from typing import Optional, Sequence
import sys
import re
import os
import csv
import statistics
from math import floor
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
    print("\t" * num_indent + str(config.original_idx_perm), flush=True)
    print_idx_orders(config.prod, num_indent + 1)
    print_idx_orders(config.cons, num_indent + 1)
    
def convert_sec_min_sec(seconds) -> list:
    """converts seconds into minutes and seconds

    Args:
        seconds (number): number of seconds to convert
    """
    return [floor(seconds / 60), round(seconds - (floor(seconds / 60) * 60), 3)]


def main(argv: Optional[Sequence[str]] = None):
    print('starting to evaluate the script', flush=True)
    parser = argparse.ArgumentParser(description='Tests time of various fused and unfused schedules as found by autoscheduler.', usage="python3 -m src.main_run_test.py -o [csv test file(s)] -f [json test file(s)] -t [test name(s)] [optional args]")
    
    parser.add_argument('-c', '--test_file', help='cpp file to write scheduling code into', default="tests-workspaces.cpp")
    parser.add_argument('-o', '--output_files', help='csv file(s) for writing tests into', nargs='+', required=True)
    parser.add_argument('-f', '--json_files', help='json file(s) to read configs from', nargs='+', required=True)
    parser.add_argument('-t', '--test_names', help='name of corresponding test(s)', nargs='+', required=True)
    parser.add_argument('-n', '--num_tests', help='number of tests for each config to run', type=int, default=100)
    parser.add_argument('-p', '--path', help='path to taco directory', default="../SparseLNR_Most_Recent")
    parser.add_argument('-d', '--debug', action='store_true', help='enable debugging')
    parser.add_argument('-r', '--messages', action='store_true', help='enable printing of progress')
    parser.add_argument('-v', '--type', help="matrices or tensors. 0 is matrices, 1 is 3D tensors", required=True, type=int)
    
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
    type_of_data = args['type']
    
    print(test_file, flush=True)
    # relative path to Makefile
    path_makefile = path_root + "/build"

    # relative path to taco-test executable
    path_test = path_makefile + "/bin/taco-test"

    # Makefile command to run
    command = "make -j 8"
    
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
        
        print(len(config_list), 'configs found for the given evaluation', flush=True)
        
        tensor_list = []
        if (type_of_data == 0):
            # "com-Amazon.mtx", amazon one fails saying mtx signature is not available 
            tensor_list = ["bcsstk17.mtx", "cant.mtx", "consph.mtx", 
                        "cop20k_A.mtx", "mac_econ_fwd500.mtx", "pdb1HYS.mtx", "rma10.mtx",
                        "scircuit.mtx", "shipsec1.mtx", "webbase-1M.mtx", "circuit5M.mtx"]
        elif (type_of_data == 1):
            tensor_list = ["vast-2015-mc1-3d.tns", "nell-1.tns", "nell-2.tns", "flickr-3d.tns"]
        tensor_file_path = "/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/"
        
        with open(out_file, 'w', newline='') as csvfile2:
            eval_writer = csv.writer(csvfile2, delimiter=',')
            list_times = ["Time " + str(num + 1) for num in range(num_tests)]
            # print(len(list_times))
            header_row = ['Tensor', 'Median Runtime', 'Runtime Standard Dev', 'Default runtime', 'Default runtime std', 'Config']
            # header_row.extend(list_times)
            # header_row.append("Median Runtime")
            # header_row.append("Runtime Standard Dev")
            
            eval_writer.writerow(header_row)
            csvfile2.flush()
            
            out_temp = out_file
        
            for tensor in tensor_list:
                out_file = tensor + "_" + out_temp
                tensor_file = tensor_file_path + tensor
                os.environ["TENSOR_FILE"] = tensor_file
                
                print('evaluating tensor', tensor, flush=True)
            
                # for i, config1 in enumerate(config_list):
                #     for j, config2 in enumerate(config_list):
                #         if i == j: continue
                #         if config1 == config2: print(config1)
                # exit()
                
                existing_schedules = {}
                default_time = 10000000000000000
                default_time_std = 0
                min_time = 10000000000000000
                min_time_std = 0
                min_config = None
            
                
                with open("temp/" + out_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    list_times = ["Time " + str(num + 1) for num in range(num_tests)]
                    # print(len(list_times))
                    header_row = ['Schedule', 'Commands']
                    header_row.extend(list_times)
                    header_row.append("Median Runtime")
                    header_row.append("Runtime Standard Dev")
                    
                    writer.writerow(header_row)
                    csvfile.flush()
                
                    # # write basic testing code first
                    # basic_test_code = Write_Test_Code(config_list[0], test_name, test_file, basic_config=True)
                    # make_basic_output = subprocess.Popen(f'(cd {path_makefile} && {command})', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                    # make_basic_output.wait()
                    # if messages: print(f'Basic test compiled')
                    # # individual times to compute for given schedule
                    # output_times = []

                    # start_time = time()

                    # # statement in the form forall(i, forall, j, where(etc.))
                    # schedule_stmt = ""
                    # schedule_commands = []
                    
                    # for test_iter in range(num_tests):
                    #     # runs test
                    #     test_output = subprocess.Popen(f'{path_test} {get_arg(test_name)}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                        
                    #     # wait for output to generate
                    #     test_output.wait()
                        
                    #     stdout_lines = test_output.stdout.readlines()
                    #     stderr_lines = test_output.stderr.readlines()
                    #     print("".join(stdout_lines))
                    #     if test_iter == 0:
                    #         # gets schedule statement of given schedule
                    #         schedule_stmt = re.sub("final stmt: ", "", stdout_lines[6])
                        
                    #     time_to_run = re.search("(\d+) ms total", stdout_lines[-2]).groups()[0]
                    #     output_times.append(time_to_run)
                    # if messages: print(f'Basic Config Test Passed With 0 Errors in {round(time() - start_time, 3)} seconds')
                    # # print(schedule_stmt, schedule_commands)
                    # # print(output_times)
                    # # print(re.sub(",", "\",\"", schedule_stmt))
                    # del basic_test_code
                    
                    # schedule_stmt = re.sub("\n", "", schedule_stmt)
                    # new_row = [schedule_stmt, "\n".join(schedule_commands)]
                    # new_row.extend(output_times)
                    # int_times = [int(output_time) for output_time in output_times]
                    # new_row.extend([round(mean(int_times),3), round(stdev(int_times),3)])
                    # writer.writerow(new_row)
                    # if messages: print()
                    
                    for iter, config in enumerate(config_list):
                        
                        print(iter, ': tensor: ', tensor, 'config:', config, flush=True)
                        # write testing code into testing file
                        test_code = Write_Test_Code(config, test_name, test_file)
                        # compiles with changed config
                        make_output = subprocess.Popen(f'(cd {path_makefile} && {command})', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                        
                        # wait for compilation to finish
                        make_output.wait()
                        stdout_lines = make_output.stdout.readlines()
                        stderr_lines = make_output.stderr.readlines()
                        
                        if (stderr_lines):
                            print('make std out', stdout_lines, flush=True)
                            print('make std err', stderr_lines, flush=True)
                        if messages: print(f'Config {iter + 1}/{len(config_list)} test compiled', flush=True)
                        
                        # individual times to compute for given schedule
                        output_times = []
                        expected_times = []
                        
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
                            print("", flush=True)
                            print("\n".join(schedule_commands), flush=True)
                            print("", flush=True)
                            print_idx_orders(config)
                            print("", flush=True)
                            visitor = PrintConfigVisitor(tests[0]["accesses"])
                            config.accept(visitor)
                            print("", flush=True)
                            print_idx_orders(existing_schedules[tuple(schedule_commands)])
                            existing_schedules[tuple(schedule_commands)].accept(visitor)
                            
                            exit()
                        existing_schedules[tuple(schedule_commands)] = config
                        
                        # outer for loop here
                        
                        # runs test
                        test_output = subprocess.Popen(f'TENSOR_FILE={tensor_file} {path_test} {get_arg(test_name)}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                        
                        # wait for output to generate
                        test_output.wait()
                        
                        stdout_lines = test_output.stdout.readlines()
                        stderr_lines = test_output.stderr.readlines()
                        print(stdout_lines, flush=True)
                        print("\n", flush=True)
                        # if test_iter == 0:
                        if stderr_lines:
                            print("".join(stdout_lines), flush=True)
                            print("".join(test_code.schedule_text), flush=True)
                            print("", flush=True)
                            print("".join(stderr_lines), flush=True)
                            print("", flush=True)
                            visitor = PrintConfigVisitor(tests[0]["accesses"])
                            config.accept(visitor)
                            exit()
                        
                        if debug and not re.search("PASSED", stdout_lines[-1]):
                            print(f'Config {iter + 1} Test Failed', flush=True)
                            print("".join(stdout_lines), flush=True)
                            print("".join(test_code.schedule_text), flush=True)
                            print("", flush=True)
                            print("".join(stderr_lines), flush=True)
                            print("", flush=True)
                            # print("".join(test_code.schedule_text))
                            # print()
                            visitor = PrintConfigVisitor(tests[0]["accesses"])
                            config.accept(visitor)
                            print_idx_orders(config)
                            exit()
                            
                            # gets schedule statement of given schedule
                            schedule_stmt = re.sub("final stmt: ", "", stdout_lines[6])
                            
                        # time_to_run = re.search("(\d+) ms total", stdout_lines[-2]).groups()[0]
                        for test_iter in range(num_tests):
                            time_to_run = float(stdout_lines[7 + test_iter*2])
                            output_times.append(time_to_run)
                            if iter == 0:
                                expected_times.append(float(stdout_lines[8 + test_iter*2]))
                                
                        if messages: print(f'Config {iter + 1} Test Passed With 0 Errors in {round(time() - start_time, 3)} seconds', flush=True)
                        # print(schedule_stmt, schedule_commands)
                        # print(output_times)
                        # print(re.sub(",", "\",\"", schedule_stmt))
                        del test_code
                        if iter == 0:
                            new_row = ["Default", ""]
                            new_row.extend(expected_times)
                            float_times = [float(expected_time) for expected_time in expected_times]
                            new_row.extend([round(statistics.median(float_times),6), round(stdev(float_times),6)])
                            writer.writerow(new_row)
                            default_time = round(statistics.median(float_times),6)
                            default_time_std = stdev(float_times)
                        
                        schedule_stmt = re.sub("\n", "", schedule_stmt)
                        new_row = [schedule_stmt, "\n".join(schedule_commands)]
                        new_row.extend(output_times)
                        float_times = [float(output_time) for output_time in output_times]
                        new_row.extend([round(statistics.median(float_times),6), round(stdev(float_times),6)])
                        writer.writerow(new_row)
                        csvfile.flush()
                        
                        if messages: print("", flush=True)
                        
                        if (min_time > round(statistics.median(float_times),6)):
                            min_time = round(statistics.median(float_times),6)
                            min_time_std = round(stdev(float_times),6)
                            min_config = config
                            
                        
                        
                        # break
                        
                        # print()
                        # print(stdout_lines[6])
                        # print(stdout_lines[7])
                        # print(test_output.stderr.readlines())
                        
                        # break
                    
                    data_row = [tensor, min_time, min_time_std, default_time, default_time_std, min_config]
                    eval_writer.writerow(data_row)
                    csvfile2.flush()
                    
                if messages: print(f'{test_name} test finished in {round(time() - time_test_start, 3)} seconds', flush=True)
                
                del os.environ['TENSOR_FILE']
    if messages: 
        total_time = convert_sec_min_sec(round(time() - program_start_time, 3))
        print(f'All tests ran in {total_time[0]} minutes and {total_time[1]} seconds')
        
if __name__ == "__main__":
    exit(main())
