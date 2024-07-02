import argparse
import os
import subprocess

def build_project(directory):
    print(f"Building project in directory: {directory}")
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
parser.add_argument('--directory', type=str, help='Path to tensor-schedules directory')
args = parser.parse_args()

print(parser)
directory = args.directory

# loopcontractfuse_real // test 3
sddmm_spmm_real = """
	vector<int> path_ = {};

	A(i, l) = B(i, j) * C(i, k) * D(j, k) * E(j, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	stmt = stmt
		.reorder(path_, {i,j,k,l})
		.loopfuse(3, true, path_)
		.parallelize(i, ParallelUnit::CPUThread, OutputRaceStrategy::NoRaces)
		;
"""

# sddmm_spmm_gemm_real // test 4
sddmm_spmm_gemm_real = """
	vector<int> path_ = {};
	vector<int> path_0 = {0};
	vector<int> path_1 = {1};

	A(i, m) = B(i, j) * C(i, k) * D(j, k) * E(j, l) * F(l, m);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	stmt = stmt
		.reorder(path_, {i,j,k,l,m})
		.loopfuse(4, true, path_)
		.reorder(path_0, {j,k,l})
		.loopfuse(3, true, path_0)
		.reorder(path_1, {l,m})
		.parallelize(i, ParallelUnit::CPUThread, OutputRaceStrategy::NoRaces)
		;
"""

spttm_ttm_real = """
	vector<int> path_ = {};

	A(i, l, m) = B(i, j, k) * D(k, m) * C(j, l);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	stmt = stmt
        .reorder({i, j, m, k, l})
        .loopfuse(2, true, path_)
        .parallelize(i, ParallelUnit::CPUThread, OutputRaceStrategy::NoRaces)
	    ;
"""

mttkrp_gemm_real = """
	vector<int> path_ = {};

	A(i, m) = B(i, k, l) * C(l, j) * D(k, j) * E(j, m);
	IndexStmt stmt = A.getAssignment().concretize();
	std::cout << stmt << endl;
	stmt = stmt
      .reorder({i, j, k, l, m})
      .loopfuse(3, true, path_)
      .parallelize(i, ParallelUnit::CPUThread, OutputRaceStrategy::NoRaces)
		;
"""

project_directory = f'{directory}/sparseLNR/build'
test_file = f"{directory}/sparseLNR/test/tests-workspaces.cpp"

replace_text_in_file(
    test_file, 
    "/* BEGIN sddmm_spmm_real TEST */", 
    "/* END sddmm_spmm_real TEST */", 
    sddmm_spmm_real)

replace_text_in_file(
    test_file,
    "/* BEGIN sddmm_spmm_gemm_real TEST */", 
    "/* END sddmm_spmm_gemm_real TEST */", 
    sddmm_spmm_gemm_real)

replace_text_in_file(
    test_file, 
    "/* BEGIN spttm_ttm_real TEST */", 
    "/* END spttm_ttm_real TEST */", 
    spttm_ttm_real)

replace_text_in_file(
    test_file,
    "/* BEGIN mttkrp_gemm_real TEST */", 
    "/* END mttkrp_gemm_real TEST */", 
    mttkrp_gemm_real)

build_project(project_directory)