## Scheduling Tensor Expressions

## Setup inputs
For a given tensor contraction, change the accesses dictionary in src.main file

## To Activate the Virtual Environment
```bash
# create virtual environment
python3 -m venv .venv

# activate the python virtual environment
source ./.venv/bin/activate

# freeze packages
pip freeze > requirements.txt
# install packages from the requirements.txt
pip install -r requirements.txt
```

## To Run the Program

```bash
python3 -m src.main > output.txt

# to run all the tests inside tests dir
# -s prints print statements inside the execution
pytest -s <test dir> > test_output.txt
pytest -s test > test_output.txt

pytest -s test/test_define_data_layout.py::test_check_data_layout

pytest -s test/test_autosched.py::test_autosched_unfused1
<<<<<<< HEAD
=======
pytest -s test/test_autosched.py::test_autosched_fused1

pytest -s test/test_complexity.py::test_time_complexity
pytest -s test/test_z3.py::test_z3_expr1

pytest -s test/test_prune.py::test_depth_prune
pytest -s test/test_prune.py::test_z3_prune

<<<<<<< HEAD
>>>>>>> origin/dev-cost-model-3
=======
pytest -s test/test_autosched.py::test_autoschedule1

>>>>>>> origin/dev-cost-model-4
# to run a single test 
python3 -m <test dir>.<test name>
python3 -m test.test_union_list
```
## To Download Tensors
```bash
./load_tensors.sh
This will create a downloads folder and put tns and mtx files in it.  It will also add a temp folder.
```

## To Format Config Files
Config files must be in JSON format with the following key-value pairs
```bash
# format
{
    "accesses": {
        "[tensor]": list[indices]
    }
    "tensor_idx_order_constraints": {
        "[tensor]": list[list[indices]]
    }
    "output_tensor": [tensor]
    "test_json_file": [json file to store configs into]
    *"z3_constraints": list[constraints]
    "test_name": [taco test name]
    "output_csv_file": [csv file to output stats]
    "type": [0 for matrix test, 1 for tensor test] 
    *"num_tests": [number of iterations of a given test to run]
}

* not explicitly required but a good idea to have

# example
{
  "accesses": {
    "A": ["l", "m", "n"],
    "B": ["i", "j", "k"],
    "C": ["i", "l"],
    "D": ["j", "m"],
    "E": ["k", "n"]
  },
  "tensor_idx_order_constraints": {
    "B": [["j", "i"], ["k", "j"], ["k", "i"]]
  },
  "output_tensor": "A",
  "test_json_file": "test2.json",
  "test_name": "loopcontractfuse_real",
  "z3_constraints": [
    "i >= 5000", "i <= 15000",
    "j >= 5000", "j <= 15000",
    "k >= 5000", "k <= 15000",
    "l >= 8", "l <= 256",
    "m >= 8", "m <= 256",
    "n >= 8", "n <= 256",
    "jpos >= 0", "kpos >= 0",
    "100 * i * jpos * kpos < i * j * k",
    "i*jpos < 0.01 * i*j",
    "i * j * k < 1000 * i * jpos * kpos"
  ],
  "output_csv_file": "test2.csv",
  "type": 1,
  "num_tests": 3
}
```

## To Run Tests
```bash
# store tests into specified json files
python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]

# example
python3 -m src.main_store_json -f test2_config.json

# run tests and stores runtimes in csv test file(s)
python3 -m src.main_run_test -f [json config file(s)] -p [taco file path] [optional args]

# example
python3 -m src.main_run_test -f test2_config.json -p ~/SparseLNR -m -x

* add -m to display messages about runtime of the python script and -x to display tensor information and taco output
* add -t [path] to change path to testing tensors to be something other than downloads in the current directory
```
