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

pytest -s test/test_autosched.py::test_autosched_unfused1
pytest -s test/test_autosched.py::test_autosched_fused1

pytest -s test/test_complexity.py::test_time_complexity
pytest -s test/test_z3.py::test_z3_expr1

# to run a single test 
python3 -m <test dir>.<test name>
python3 -m test.test_union_list
```
