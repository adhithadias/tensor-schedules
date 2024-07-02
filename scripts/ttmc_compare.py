import argparse
import os
import subprocess
import re
import statistics

def extract_values(output):
    # Regular expression pattern to match floating-point numbers
    pattern = r'\d+\.\d+'
    pattern = r'(?<=\n)\d+\.\d+\b|\d+(?:\.\d+)?(?=\n)'
    pattern = r'^\s*(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'
    pattern = r'(?<=\n)\d+\.\d+\b|\d+(?:\.\d+)?(?=\n)|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?=\n)'
    
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

parser = argparse.ArgumentParser(description='Run sparseLNR tests')
parser.add_argument('--directory', type=str, help='Path to taco directory')
parser.add_argument('--iterations', type=int, help="Number of iterations", default=3)
args = parser.parse_args()

print(parser)
directory = args.directory
num_iterations = args.iterations

# loopcontractfuse_real
replacement_text_ttmc_ours = """
	A(l, m, n) = B(i, j, k) * E(k, n) * D(j, m) * C(i, l);
	
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	
	vector<int> path0;
	vector<int> path1 = {0};
    vector<int> path2 = {1};
	stmt = stmt
    .reorder({i, n, j, k, l, m})
    .loopfuse(3, true, path0)
    .loopfuse(2, true, path1)
		;
    if (nthreads > 1) {
        stmt = stmt.parallelize(i, ParallelUnit::CPUThread, OutputRaceStrategy::Atomics);
    }
"""

# spttn_cyclops_loopcontractfuse_real
replacement_text_ttmc_theirs = """
	A(l, m, n) = B(i, j, k) * E(k, n) * D(j, m) * C(i, l);
	
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	
	vector<int> path0;
	vector<int> path1 = {0};
	stmt = stmt
		.reorder({i, j, k, l, m, n})
		.loopfuse(2, true, path0)
		.loopfuse(2, true, path1)
		;
"""

project_directory = f'{directory}/sparseLNR/build'
dataset_directory = f"{directory}/tensor-schedules/downloads"
executable = f"{project_directory}/bin/taco-test"

test_file = f"{directory}/sparseLNR/test/tests-workspaces.cpp"


replace_text_in_file(
    test_file, 
    "/* BEGIN loopcontractfuse_real TEST */", 
    "/* END loopcontractfuse_real TEST */", 
    replacement_text_ttmc_ours)

replace_text_in_file(
    test_file,
    "/* BEGIN spttn_cyclops_loopcontractfuse_real TEST */", 
    "/* END spttn_cyclops_loopcontractfuse_real TEST */", 
    replacement_text_ttmc_theirs)

# build project once after replacing the texts
build_project(project_directory)

def get_list(tensor):
    if tensor == 'nell-2.tns':
        return [16, 32, 64, 128]
    elif tensor == 'flickr-3d.tns':
        return [16, 32, 64]

    assert(False)

tensors = ['nell-2.tns', 'flickr-3d.tns']

for tensor in tensors:
    
    output_text = "Dense Dimensions,SparseAuto;L=16,Cyclops;L=16,SparseAuto;L=32,Cyclops;L=32,SparseAuto;L=64,Cyclops;L=64,SparseAuto;L=128,Cyclops;L=128\n"
    
    for m in get_list(tensor): # for flickr 128 is not used
        n = m
        output_text += f"M={m};N={n}"
        for l in get_list(tensor):
            terminal_command = f'L={l} M={m} N={n} OMP_NUM_THREADS=1 ITERATIONS={num_iterations} TENSOR_FILE={dataset_directory}/matrix_name_placeholder {executable} --gtest_filter=workspaces.test_name_placeholder'
            
            terminal_command_ours = terminal_command.replace("matrix_name_placeholder", tensor).replace("test_name_placeholder", "loopcontractfuse_real")
            print(terminal_command_ours)
            output = execute_terminal_command(terminal_command_ours)
            if output is not None:
                print("output:")
                print(output, flush=True)
                values = extract_values(output)
                print('values: ', values, flush=True)
                v = statistics.median(values)
                output_text += f",{v}"
            
            terminal_command_spttn_cyclops = terminal_command.replace("matrix_name_placeholder", tensor).replace("test_name_placeholder", "spttn_cyclops_loopcontractfuse_real")
            print(terminal_command_spttn_cyclops)
            output = execute_terminal_command(terminal_command_spttn_cyclops)
            if output is not None:
                print("output:")
                print(output, flush=True)
                values = extract_values(output)
                print('values: ', values, flush=True)
                v = statistics.median(values)
                output_text += f",{v}"
                
        output_text += "\n"
        print(output_text)
        # exit(0)
        
    t = tensor.split('.')[0]
    csv_file = f"{directory}/tensor-schedules/csv-results/ttmc_compare_{t}.csv"
    
    f = open(csv_file, 'w')
    f.write(output_text)
    f.close()

