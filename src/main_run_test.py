import subprocess
import argparse
from typing import Optional, Sequence
import sys
import re
import os
import csv
from copy import deepcopy
from src.gen_taco_rep import Write_Test_Code
from src.config import Config
from src.file_storing import read_json
from src.print_help import Main_Run_Test, Print_Help_Visitor, is_valid_file_type
from src.visitor import PrintConfigVisitor
from src.testing import tests

# incomplete argument
run_arg = "workspaces._"

def get_arg(test): return re.sub("_", test, deepcopy(run_arg))

def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description='Tests time of various fused and unfused schedules as found by autoscheduler.')
    
    parser.add_argument('-c', '--test_file', help='cpp file to write scheduling code into', default="tests-workspaces.cpp")
    parser.add_argument('-o', '--output_files', help='csv file(s) for writing tests into', nargs='+', required=True)
    parser.add_argument('-f', '--json_files', help='json file(s) to read configs from', nargs='+', required=True)
    parser.add_argument('-t', '--test_names', help='name of corresponding test(s)', nargs='+', required=True)
    parser.add_argument('-n', '--num_tests', help='number of tests for each config to run', type=int, default=100)
    parser.add_argument('-p', '--path', help='path to taco directory', default="../SparseLNR_Most_Recent")
    
    args = vars(parser.parse_args(argv))
    path_root = args['path']
    test_file = f'{path_root}/test/{args["test_file"]}'
    output_files = args['output_files']
    json_files = args['json_files']
    test_names = args['test_names']
    num_tests = args['num_tests']
    path_root = args['path']
    
    print(test_file)
    # relative path to Makefile
    path_makefile = path_root + "/build"

    # relative path to taco-test executable
    path_test = path_makefile + "/bin/taco-test"

    # Makefile command to run
    command = "make taco-test/fast"
    
    # number of tests must match
    assert len(output_files) == len(json_files) and len(output_files) == len(test_names)
    
    print(output_files, json_files, test_names)       
    # run tests for each test case
    for out_file, json_file, test_name in zip(output_files, json_files, test_names):
        # make sure file types are correct
        if not is_valid_file_type(out_file, "csv"): continue
        if not is_valid_file_type(json_file, "json"): continue
        config_list = read_json(json_file)
        with open(out_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            list_times = ["Time" + str(num + 1) for num in range(num_tests)]
            print(len(list_times))
            header_row = ['Schedule', 'Commands']
            header_row.extend(list_times)
            writer.writerow(header_row)
        
            for config in config_list:
                # write testing code into testing file
                test_code = Write_Test_Code(config, test_name, test_file)
                
                # compiles with changed config
                make_output = subprocess.Popen(f'(cd {path_makefile} && {command})', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)

                make_output.wait()
                
                # outer for loop here 
                # runs test
                test_output = subprocess.Popen(f'{path_test} {get_arg(test_name)}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
                
                test_output.wait()
                stdout_lines = test_output.stdout.readlines()
                print("".join(stdout_lines))
                stderr_lines = test_output.stderr.readlines()
                print("".join(test_code.schedule_text))
                print()
              
                
                
                visitor = PrintConfigVisitor(tests[0]["accesses"])
                config.accept(visitor)
                
                if stderr_lines:
                    print("".join(stderr_lines))
                    print()
                    # print("".join(test_code.schedule_text))
                    # print()
                    # visitor = PrintConfigVisitor(tests[0]["accesses"])
                    # config.accept(visitor)
                    exit()
                else: print("No Errors")
                
                print("------")
                print(stdout_lines[-3:])
                print("--------")
                if re.match("FAILED", stdout_lines[-1]): exit()
                  
              
                # break  
                print()
                # print(stdout_lines[6])
                # print(stdout_lines[7])
                # print(test_output.stderr.readlines())
                
                # break
        




if __name__ == "__main__":
    exit(main())
    main_class = Main_Run_Test(sys.argv)
    print_visitor = Print_Help_Visitor()
    main_class.accept(print_visitor)
    
    filenames = []
    tests_to_run = []

    for arg in sys.argv[2:int((len(sys.argv) + 2) / 2)]:
        filenames.append(arg)
    for arg in sys.argv[int((len(sys.argv) + 2) / 2):]:
        tests_to_run.append(arg)

    assert len(set(filenames)) == len(filenames)

    for test_to_run, filename in zip(tests_to_run, filenames):
        config_list = read_json(filename)
        
        make_output = subprocess.Popen(f'(cd {path_makefile} && {command})', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
        
        print(make_output.stdout.readlines())
        print(make_output.stderr.readlines())
        
        test_output = subprocess.Popen(f'{path_test} {get_arg(arg)}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
        
        print(test_output.stdout.readlines())
        print(test_output.stderr.readlines())
        
        
        
        
        # assembly_loops = subprocess.Popen('./taco ' + args + "-print-assembly", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid, cwd='/web/entities/sparseshed')
        # full_code = subprocess.Popen('./taco ' + args + "-write-source=/dev/stdout", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid, cwd='/web/entities/sparseshed')
        
