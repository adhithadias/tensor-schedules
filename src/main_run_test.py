import subprocess
from src.gen_taco_rep import Write_Test_Code
from src.config import Config
from src.file_storing import read_json
import sys
import re
import os
from copy import deepcopy

# path to taco directory
path_root = "../SparseLNR_Most_Recent"

# relative path to Makefile
path_makefile = path_root + "/build"

# relative path to taco-test executable
path_test = path_makefile + "/bin/taco-test"

# Makefile command to run
command = "make taco-test/fast"

# incomplete argument
run_arg = "workspaces._"

def print_help_info():
    print("Proper usage:")
    print("python3 -m src.main_run_test [test_file] [json file(s)] [test name(s)]")
    print("\nExample execution:")
    print("python3 -m src.main_run_test tests-workspaces.cpp test1.json test2.json test3.json test1 test2 test3")

def get_arg(test): return re.sub("_", test, deepcopy(run_arg))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "help":
        print_help_info()
        exit()
    elif len(sys.argv) < 4:
        print("Too few arguments\n", file=sys.stderr)
        print_help_info()
        exit()
    elif len(sys.argv) % 2:
        print("Invalid arguments given.  Give file name(s) and test number(s) as command line arguments\n", file=sys.stderr)
        print_help_info()
        exit()
        
    filenames = []
    tests_to_run = []

    for arg in sys.argv[2:int((len(sys.argv) + 2) / 2)]:
        if re.match(".*\.json", arg) == None:
            print("All file inputs must be json files", file=sys.stderr)
            exit()
        filenames.append(arg)
    for arg in sys.argv[int((len(sys.argv) + 2) / 2):]:
        # TODO maybe check if it matches a test in my test file?  May be too much unnecessary work
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
        
