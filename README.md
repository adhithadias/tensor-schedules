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
## To Run Tests
```bash
# test numbers
0 -> X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m)
2 -> A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n) - tensor contraction
3 -> A(i,l) = B(i,j) * C(i,k) * D(j,k) * E(j,l) - <SDDMM, SpMM>
4 -> A(i,m) = B(i,j) * C(i,k) * D(j,k) * E(j,l) * F(l,m) - <SDDMM, SpMM, GEMM>
5 -> A(i,l,m) = B(i,j,k) * C(j,l) * D(k,m) - <SpTTM, TTM>

# store tests into specified json files
python3 -m src.main_store_json [json file(s)] [test number(s)]

# run tests and stores runtimes in csv test file(s)
python3 -m src.main_run_test -o [csv test file(s)] -f [json test file(s)] -t [test name(s)] -p [path to taco repository] [optional args]

```
## To Download Tensors
```bash
./load_tensors.sh
```
