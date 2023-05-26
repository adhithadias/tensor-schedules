import subprocess
from src.gen_taco_rep import Write_Test_Code
from src.config import Config
from src.file_storing import read_json
from src.print_help import Main_Run_Test, Print_Help_Visitor
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

def get_arg(test): return re.sub("_", test, deepcopy(run_arg))

if __name__ == "__main__":
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
        
