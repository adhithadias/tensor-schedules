## Scheduling Tensor Expressions

## Setup inputs
For a given tensor contraction, change the accesses dictionary in src.main file

## To Run the Program

```bash
python3 -m src.main > output.txt

# to run all the tests inside tests dir
# -s prints print statements inside the execution
pytest -s <test dir> > test_output.txt
pytest -s test > test_output.txt
# to run a single test 
python3 -m <test dir>.<test name>
python3 -m test.test_union_list
```
