import os
import re
import subprocess
import argparse

def extract_values(output):
    # Regular expression pattern to match floating-point numbers
    pattern = r'\d+\.\d+'
    pattern = r'(?<=\n)\d+\.\d+\b|\d+(?:\.\d+)?(?=\n)'
    
    # Find all matches of the pattern in the output
    matches = re.findall(pattern, output)
    
    # Convert matched strings to floats and append them to a list
    values = [float(match) for match in matches]
    
    return values

def build_project(directory):
    # Change directory
    os.chdir(directory)
    
    # Execute 'make' command and capture the output
    try:
        result = subprocess.run(['make'], capture_output=True, text=True, check=True)
        print("Project build successful!")
        print("Output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to build project.")
        print("Error Output:")
        print(e.stderr)
        
def execute_terminal_command(command):
    try:
        # Execute the terminal command
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        # Return the output
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Print error message
        print("Error: Failed to execute command.")
        print("Error Output:")
        print(e.stderr)
        # Return None if there's an error
        return None

def replace_text_in_file(file_path, start_text, end_text, replacement_text):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    start_index = None
    end_index = None

    # Find the indices of start and end text
    for i, line in enumerate(lines):
        if start_text in line:
            start_index = i
        elif end_text in line:
            end_index = i

    # Replace the text between start and end indices
    if start_index is not None and end_index is not None:
        lines[start_index + 1:end_index] = [replacement_text + '\n']

    # Write the modified lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)

replacement_texts_spttm_willow = [
"""
	A(i, j, m) = B(i, j, k) * C(k, l) * D(l, m);
	
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	
	vector<int> path0;
    vector<int> path1 = {0};
	stmt = stmt
		.reorder({i, j, k, l, m})
		.loopfuse(2, true, path0)
        .reorder(path1, {l, k})
		;
""",
"""
	A(i, j, m) = B(i, j, k) * C(k, l) * D(l, m);
	
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	
	vector<int> path0;
    vector<int> path1 = {0};
	stmt = stmt
		.reorder({i, j, k, l, m})
		.loopfuse(2, true, path0)
        .reorder(path1, {k, l})
		;
"""
]

replacement_texts_spttm_ours = ["""
	A(i, j, m) = B(i, j, k) * C(k, l) * D(l, m);
	
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	
	vector<int> path0;
    vector<int> path1 = {0};
	stmt = stmt
		.reorder({i, j, k, l, m})
		.loopfuse(2, true, path0)
    .reorder(path1, {l, k})
		;
"""]

replacement_texts_spmm_willow = ["""
	vector<int> path_ = {};
    vector<int> path1_ = {1};

	A(i, l) = B(i, j) * C(j, k) * D(k, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	stmt = stmt
	    .reorder(path_, {k,l,i,j})
	    .loopfuse(2, true, path_)
        .reorder(path1_, {i,l})
	;
""",
"""
	vector<int> path_ = {};
    vector<int> path1_ = {1};

	A(i, l) = B(i, j) * C(j, k) * D(k, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;

	stmt = stmt
	    .reorder(path_, {k,l,i,j})
	    .loopfuse(2, true, path_)
        .reorder(path1_, {l,i})
	    ;
""",
"""
	vector<int> path_ = {};
    vector<int> path1_ = {1};

	A(i, l) = B(i, j) * C(j, k) * D(k, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;

	stmt = stmt
		.reorder(path_, {i,l,k,j})
		.loopfuse(2, true, path_)
        .reorder(path1_, {k,l})
		;
""",
"""
	vector<int> path_ = {};
    vector<int> path1_ = {1};

	A(i, l) = B(i, j) * C(j, k) * D(k, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;

	stmt = stmt
		.reorder(path_, {i,l,k,j})
		.loopfuse(2, true, path_)
        .reorder(path1_, {l,k})
		;
"""
]

replacement_texts_spmm_ours = ["""
	vector<int> path_ = {};

	A(i, l) = B(i, j) * C(j, k) * D(k, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	stmt = stmt
		.reorder(path_, {i,j,k,l})
		.loopfuse(2, true, path_)
		;
"""]

num_iterations = 4

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, help='Path to taco directory')
args = parser.parse_args()

# taco_dir = '/home/min/a/kadhitha/workspace/my_taco'
taco_dir = args.directory
# Test file
file_path = f"{taco_dir}/sparseLNR/test/tests-workspaces.cpp"
# Directory where the project is located
project_directory = f'{taco_dir}/sparseLNR/build'

terminal_command = f'OMP_NUM_THREADS=1 ITERATIONS={num_iterations} TENSOR_FILE={taco_dir}/tensor-schedules/downloads/matrix_name_placeholder {taco_dir}/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.test_name_placeholder'

# # Text to replace
# start_text = '/* BEGIN spttm_spttm_willow TEST */'
# end_text = '/* END spttm_spttm_willow TEST */'

test_types = {
    0: [[
        {
            'test_name': 'spmm_gemm_real', 
            'start_text': '/* BEGIN spmm_gemm_real TEST */', 
            'end_text': '/* END spmm_gemm_real TEST */',
            'replacement_texts': replacement_texts_spmm_ours
        }, 
        {
            'test_name': 'spmm_gemm_willow', 
            'start_text': '/* BEGIN spmm_gemm_willow TEST */', 
            'end_text': '/* END spmm_gemm_willow TEST */',
            'replacement_texts': replacement_texts_spmm_willow
        }
        ]],
    1: [[
        {
            'test_name': 'spttm_spttm_real', 
            'start_text': '/* BEGIN spttm_spttm_real TEST */', 
            'end_text': '/* END spttm_spttm_real TEST */',
            'replacement_texts': replacement_texts_spttm_ours
        }, 
        {
            'test_name':'spttm_spttm_willow', 
            'start_text': '/* BEGIN spttm_spttm_willow TEST */', 
            'end_text': '/* END spttm_spttm_willow TEST */',
            'replacement_texts': replacement_texts_spttm_willow
        }
        ]],
}

mtx_matrices = [
    'bcsstk17.mtx', 
    # 'cant.mtx', 'consph.mtx', 'cop20k_A.mtx', 'pdb1HYS.mtx',  'rma10.mtx', 'scircuit.mtx', 'shipsec1.mtx',  'mac_econ_fwd500.mtx',  'webbase-1M.mtx', 'circuit5M.mtx'
]
# mtx_matrices = ['bcsstk17.mtx', 'scircuit.mtx']

tns_tensors = [
    'nell-2.tns', 'darpa1998.tns', 'flickr-3d.tns', 'vast-2015-mc1-3d.tns'
]
# tns_tensors = ['nell-2.tns']

# if not exists create a directory called pigeon
if not os.path.exists('pigeon'):
    os.makedirs('pigeon')

for test_type in test_types:
    if test_type == 1:
        dataset = tns_tensors
        # continue
    else:
        dataset = mtx_matrices
        
    for i, test_ in enumerate(test_types[test_type]):
        
        iter_string = ','.join(['iter_' + str(i) for i in range(1, num_iterations + 1)])
        
        write_str = f'test_name,data,schedule,{iter_string}\n'
        
        # # create a csv file called test{i}.csv
        # with open(f'test{i}.csv', 'w') as f:
        #     f.write(f'test_name,data,schedule,{iter_string}\n')
        
        for data in dataset:
            for test in test_: # test_ contains our test and their test
                
                test_name = test['test_name']
                start_text = test['start_text']
                end_text = test['end_text']
                replacement_texts = test['replacement_texts']
            
                terminal_command_theirs = terminal_command.replace('matrix_name_placeholder', data)
                terminal_command_theirs = terminal_command_theirs.replace('test_name_placeholder', test_name)
                print(terminal_command_theirs)
                
                for j, replacement_text in enumerate(replacement_texts):
                    # Call the function to replace text in the file
                    replace_text_in_file(file_path, start_text, end_text, replacement_text)
                    # Call the function to build the project
                    build_project(project_directory)
                    # Call the function to execute the terminal command
                    output = execute_terminal_command(terminal_command_theirs)
                    # Print the output if it's not None
                    if output is not None:
                        print("output:")
                        print(output, flush=True)
                        values = extract_values(output)
                        print('values: ', values, flush=True)
                        
                    # # save test_name, data, values to the csv file
                    # with open(f'test{i}.csv', 'a') as f:
                    #     f.write(f'{test_name},{data},{j},{",".join(str(value) for value in values)}\n')
                        
                    write_str = write_str + f'{test_name},{data},{j},{",".join(str(value) for value in values)}\n'
        
        file = f"{taco_dir}/tensor-schedules/pigeon/test_{test_type}_{i}.csv"
        f = open(file, "w")
        # write write str to the csv file
        print(write_str, flush=True)
        f.write(write_str)
        f.close()
         
            
    print('-----------------------------------')
    # exit(0)



