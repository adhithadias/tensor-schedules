from functools import reduce
import subprocess
import argparse
from typing import Optional, Sequence
import sys
import re
import os
import csv
import statistics
import json
import datetime
from math import floor
from time import time
from copy import deepcopy
from statistics import mean, stdev
from src.gen_taco_rep import Write_Test_Code
from src.config import Config
from src.file_storing import read_json, read_baskets_from_json
from src.print_help import Main_Run_Test, Print_Help_Visitor, is_valid_file_type
from src.visitor import PrintConfigVisitor
from src.testing import tests
from src.generate_taco_schedule import UnfusedConfigToTacoVisitor

ALLOWED_ELEMENT_SIZE = 2621440 # 50% of the LLC
CONFIG_JSON_FILE_FOLDER = 'test_configs/'
TEST_SCHEDULES = "test_schedules/"
CSV_RESULTS = "csv_results/"
TEMP_RESULT_FOLDER = "temp/"
OUTPUT_OFFSET = 8
NUMBER_OF_ITERATIONS = 4
TIME_OUT = 15

# incomplete argument
run_arg = "workspaces._"

def get_test_name(test): return re.sub("_", test, deepcopy(run_arg))

def print_idx_orders(config:Config, num_indent = 0):
    if config == None: return
    print("\t" * num_indent + str(config.original_idx_perm), flush=True)
    print_idx_orders(config.prod, num_indent + 1)
    print_idx_orders(config.cons, num_indent + 1)
    
def convert_sec_hour_min_sec(seconds) -> list:
    """converts seconds into minutes and seconds

    Args:
        seconds (number): number of seconds to convert
    """
    return [floor(seconds / 3600), floor(seconds / 60) % 60, round(seconds - (floor(seconds / 60) * 60), 3)]

def get_time(start_time):
  return round(time() - start_time, 4)
  
def print_message(message):
    if messages: print(message, flush=True)
    
def print_extra_message(message):
    if extra_messages: print(message, flush=True)
    
def print_time_message(message:str, start_time, newline=False, only_time=False):
    total_time = convert_sec_hour_min_sec(get_time(start_time))
    newline_char = ""
    plural_hour = "s"
    plural_min = "s"
    in_word = " in "
    
    if newline:
        newline_char = "\n"
    
    if only_time:
        in_word = ""
    
    if total_time[0] == 1:
        plural_hour = ""
    if total_time[1] == 1:
        plural_min = ""
        
    if total_time[1] == 0:
        print_message(f'{message}{in_word}{total_time[2]} seconds{newline_char}')
    elif total_time[0] == 0:
        print_message(f'{message}{in_word}{total_time[1]} minute{plural_min} and {total_time[2]} seconds{newline_char}')
    else:
        print_message(f'{message}{in_word}{total_time[0]} hour{plural_hour}, {total_time[1]} minute{plural_min} and {total_time[2]} seconds{newline_char}')


def get_schedule_commands_for_saving(test_code):
    schedule_commands = []
    for line in test_code.schedule_text:
        match_ob = re.search("(reorder\(.*\))|(loopfuse\(.*\))|(vector\<int\>.*;)", line)
        if match_ob:
            if match_ob.groups()[0] != None: schedule_commands.append(match_ob.groups()[0])
            elif match_ob.groups()[1] != None: schedule_commands.append(match_ob.groups()[1])
            else: schedule_commands.append(match_ob.groups()[2])
            
    return schedule_commands

def compile_taco_test(path_makefile, command, iter, tensor, config_list): 
    
    print(f'cd {path_makefile} && {command}')
    make_output = subprocess.Popen(f'cd {path_makefile} && {command}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
    
    # wait for compilation to finish
    make_output.wait()
    stdout_lines = make_output.stdout.readlines()
    stderr_lines = make_output.stderr.readlines()
    
    if (stderr_lines or stdout_lines):
        stdout_lines_str = "".join(stdout_lines)
        stderr_lines_str = "".join(stderr_lines)
        # if stdout_lines: print_extra_message(f'make std out: {stdout_lines_str}')
        if stderr_lines: print_extra_message(f'make std err: {stderr_lines_str}')
    print_message(f'Config {iter + 1}/{len(config_list)} test compiled for tensor {tensor}')

def get_execution_times(test_output, config, debug, num_tests):
    stdout_lines = test_output.stdout.splitlines()
    stderr_lines = test_output.stderr.splitlines()

    if (stdout_lines or stderr_lines):
        stdout_lines_str = "".join(stdout_lines)
        print_extra_message(f'test std out: {stdout_lines_str}')
    
    if stderr_lines:
        print("\n".join(stdout_lines), flush=True)
        print("", flush=True)
        print("\n".join(stderr_lines), flush=True)
        print("", flush=True)
        visitor = PrintConfigVisitor(tests[0]["accesses"])
        config.accept(visitor)
        exit()
    
    if debug and not re.search("PASSED", stdout_lines[-1]):
        print(f'Config {iter + 1} Test Failed', flush=True)
        print("".join(stdout_lines), flush=True)
        print("", flush=True)
        print("".join(stderr_lines), flush=True)
        print("", flush=True)
        # print("".join(test_code.schedule_text))
        # print()
        visitor = PrintConfigVisitor(tests[0]["accesses"])
        config.accept(visitor)
        print_idx_orders(config)
        exit()
        
    execution_times = []
    for iteration in range(num_tests-1):
        # print(f'{iteration}: {stdout_lines[8 + iteration]}')
        time_to_run = float(stdout_lines[OUTPUT_OFFSET + iteration])
        execution_times.append(time_to_run)
        # if iter == 0:
        #     expected_times.append(float(stdout_lines[10 + test_iter*2]))
    # print(execution_times)
            
    # gets schedule statement of given schedule
    schedule_stmt = re.sub("final stmt: ", "", stdout_lines[6])
    return execution_times, schedule_stmt

def main(argv: Optional[Sequence[str]] = None):
    print('starting to evaluate the script', flush=True)
    parser = argparse.ArgumentParser(description='Tests time of various fused and unfused schedules as found by autoscheduler.', usage="python3 -m src.main_run_test -f [json config file(s)] -p [taco file path] [optional args]", formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-c', '--test_file', help='cpp file to write scheduling code into', default="tests-workspaces.cpp")
    parser.add_argument('-f', '--config_files', help='json formatted configuration file(s) with the following key-value pairs required:\n\t\ttest_json_file:\t\t[json file to read configs from]\n\t\ttest_name:\t\t[taco test name]\n\t\toutput_csv_file:\t[csv file to output stats]\n\t\teval_files:\t\t[mtx/tns files to run]\n\t\t(optional) num_tests:\t[number of iterations of a given test to run]', nargs='+', required=True)
    parser.add_argument('-p', '--path', help='path to taco directory', default="/home/min/a/kadhitha/workspace/my_taco/sparseLNR")
    parser.add_argument('-t', '--tensor_file_path', help='path to downloads folder containing tensors and matrices (default: %(default)s)', default=os.curdir + "/downloads/")
    parser.add_argument('-d', '--debug', action='store_true', help='enable debugging')
    parser.add_argument('-m', '--messages', action='store_true', help='enable printing of progress')
    parser.add_argument('-x', '--extra_messages', action='store_true', help='enable printing of extra progress messages')
    parser.add_argument('-i', '--iterations', help="number of iterations to run the test", default=4)
    parser.add_argument('-e', '--extra-argument-val', help='extra argument value', default=64)
    parser.add_argument('--tensor', help='tensor to evaluate', default="bcsstk17.mtx")
    parser.add_argument('--timeout', help='timeout in seconds', default=60) # in seconds per test
    
    args = vars(parser.parse_args(argv))
    config_files = args["config_files"]
    path_root = args['path']
    tensor_file_path = args['tensor_file_path']
    test_file = f'{path_root}/test/{args["test_file"]}'
    debug = args['debug']
    global messages
    messages = args['messages']
    global extra_messages
    extra_messages = args['extra_messages']
    NUMBER_OF_ITERATIONS = int(args['iterations'])
    dimension = int(args['extra_argument_val'])
    tensor = args['tensor']
    TIME_OUT = int(args['timeout']) * NUMBER_OF_ITERATIONS
    
    
    print(dimension)
    
    config_files = [CONFIG_JSON_FILE_FOLDER + config_file for config_file in config_files]
    
    print_extra_message(test_file)
    
    # relative path to Makefile
    path_makefile = path_root + "/build"

    # relative path to taco-test executable
    path_test = path_makefile + "/bin/taco-test"

    # Makefile command to run
    command = "make -j 8"
    # print(output_files, json_files, test_names)  
    
    program_start_time = time()
    
    config_file = config_files[0]

    try:
        fileptr = open(config_file, "r")
        new_dict = json.load(fileptr)
        fileptr.close()
    except OSError:
        print("Invalid JSON file for reading. config file: ", config_file, file=sys.stderr)
        return

    json_file = new_dict["test_json_file_without_depth"]
    json_file = TEST_SCHEDULES + json_file
    test_name = new_dict["test_name"]
    out_file = new_dict["output_csv_file"]
    
    time_test_start = time()
    
    # make sure file types are correct
    assert is_valid_file_type(out_file, "csv")
    assert is_valid_file_type(json_file, "json")
    config_list, tensor_accesses = read_json(json_file, with_accesses=True)
    
    print_message(f'{len(config_list)} schedules found for the given evaluation')
    
    runtime_list = []
    output_csv_file = out_file.split(".")[0] + f"_all_schedules_{dimension}x{dimension}.csv"
    print(output_csv_file)
    print(len(config_list))

    tensor_file = tensor_file_path + tensor
    os.environ["TENSOR_FILE"] = tensor_file
    print(tensor_file)

        
    print_extra_message(f'evaluating tensor {tensor}')
    
    print(output_csv_file)
    with open(CSV_RESULTS + output_csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        
        list_times = ["Time " + str(num + 1) for num in range(NUMBER_OF_ITERATIONS-1)]
        header_row = list_times + ['Median', 'Std', 'Config', 'Stmt', 'Schedule']
        writer.writerow(header_row)
        csvfile.flush()

        
        for iter, config in enumerate(config_list):
            
            print_extra_message(f'\n------\n{iter}: tensor: {tensor}')
            pc = PrintConfigVisitor(tensor_accesses)
            pc.visit(config)
            # write testing code/schedule into testing file
            tf = UnfusedConfigToTacoVisitor(test_name, tensor_accesses, config.original_idx_perm, test_file, nthreads=1)
            # tf.set_tensor_accesses(tensor_accesses)
            tf.visit(config)
            tf.write_to_file(True)
            # test_code = Write_Test_Code(config, test_name, test_file, num_tests + 1, tensor_accesses)
            
            # compiles with changed config
            compile_taco_test(path_makefile, command, iter, tensor, config_list)
            
            # individual times to compute for given schedule
            output_times = []
            start_time = time()
            
            # runs test
            try:
                print(f'K={dimension} L={dimension} OMP_NUM_THREADS={1} ITERATIONS={NUMBER_OF_ITERATIONS} TENSOR_FILE={tensor_file} {path_test} --gtest_filter={get_test_name(test_name)}', flush=True)
                test_output = subprocess.run(f'K={dimension} L={dimension} OMP_NUM_THREADS={1} ITERATIONS={NUMBER_OF_ITERATIONS} TENSOR_FILE={tensor_file} {path_test} --gtest_filter={get_test_name(test_name)}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid, timeout=TIME_OUT)
            
                # wait for output to generate
                # test_output.wait()
                output_times, schedule_stmt = get_execution_times(test_output, config, debug, NUMBER_OF_ITERATIONS)
            
            except subprocess.TimeoutExpired:
                print('subprocess ran too long', flush=True)
                output_times = [0 for _ in range(NUMBER_OF_ITERATIONS - 1)]
                schedule_stmt = ""
                
            print(output_times)
            
            # output_times = [0 for _ in range(NUMBER_OF_ITERATIONS)]
            # schedule_stmt = ""
            # time_to_run = re.search("(\d+) ms total", stdout_lines[-2]).groups()[0]
                    
            print_time_message(f'Config {iter + 1} Test Passed With 0 Errors', start_time)
            print_time_message(f'Elapsed time: ', program_start_time, only_time=True)
            
            schedule_stmt = re.sub("\n", "", schedule_stmt)
            # new_row = [schedule_stmt, "\n".join(get_schedule_commands_for_saving(test_code))]
            new_row = [] 
            new_row.extend(output_times)
            float_times = [float(output_time) for output_time in output_times]
            current_exec_time = round(statistics.median(float_times),6)
            current_exec_time_std = round(stdev(float_times),6)
            
            new_row.extend([current_exec_time, current_exec_time_std, config])
            new_row.extend([schedule_stmt, tf.text])
            writer.writerow(new_row)
            csvfile.flush()
            
            # del test_code
            print_message("")
        
        print_time_message(f'{test_name} test finished', time_test_start)
        print("\n========================\n")
        
        del os.environ['TENSOR_FILE']
                
    print("runtime list: ", runtime_list)
    print("max runtime: ", max(runtime_list))
    if messages: 
        print_time_message(f'All tests ran', program_start_time)
        
if __name__ == "__main__":
    exit(main())
