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
pytest -s test/test_autosched.py::test_autosched_fused1

pytest -s test/test_complexity.py::test_time_complexity
pytest -s test/test_z3.py::test_z3_expr1

pytest -s test/test_prune.py::test_depth_prune
pytest -s test/test_prune.py::test_z3_prune

pytest -s test/test_autosched.py::test_autoschedule1

# to run a single test 
python3 -m <test dir>.<test name>
python3 -m test.test_union_list
```

## To Download Tensors
```bash
./load_tensors.sh
This will create a downloads folder and put tns and mtx files in it.  It will also add a temp folder.
```

## To Run Tests
```bash
# store tests into specified json files
python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]

# example
# first generate the schedules and run the depth based first 2 pruning stages, the pruned schedules are saved to the file under "test_json_file" in the config.json
python3 -m src.main_store_json -f test2_config.json -r
python3 -m src.main_store_json -f test3_config.json -r
python3 -m src.main_store_json -f test4_config.json -r
python3 -m src.main_store_json -f test5_config.json -r
python3 -m src.main_store_json -f test6_config.json -r

# main_store_json_z3 reads the schedules in "test_json_file" in config.json file and prunes it using the z3 configs. Divides them into 
python3 -m src.main_store_json_z3 -f test2_config.json -r
python3 -m src.main_store_json_z3 -f test3_config.json -r
python3 -m src.main_store_json_z3 -f test4_config.json -r
python3 -m src.main_store_json_z3 -f test5_config.json -r
python3 -m src.main_store_json_z3 -f test6_config.json -r

python3 -m src.run_from_z3_prune -t 2

# run tests and stores runtimes in csv test file(s)
python3 -m src.main_run_test -f [json config file(s)] -p [taco file path] [optional args]

# example
python3 -m src.main_run_test_prev -f test2_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_prev -f test3_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_prev -f test4_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_prev -f test5_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_prev -f test6_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_modified -f test2_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_modified -f test3_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 -m src.main_run_test_modified -f test4_config.json -t /home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/ -p /home/min/a/kadhitha/workspace/my_taco/sparseLNR -m -x

python3 plot_graph.py -t 2

# Running tests
pytest test/test_baskets.py
pytest test/test_cache.py -s
pytest test/test_cache.py::test_remove_duplicates -s

* add -m to display messages about runtime of the python script and -x to display tensor information and taco output
* add -t [path] to change path to testing tensors to be something other than downloads in the current directory
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

## TACO Test Setup
```bash
# setup
TEST(workspaces, [test name]) {
  [variable declarations]
  [load tensor file for reading]
  [tensor declarations and packing]
  [index declarations]
  [computation declaration]
  ...
  /* [any text] */
  ...
  /* [any text] */
  [extra transformations]
  ...
  [declare expected (no transformations)]
  [declare timing variables]
  for (int [var] = 0; [var] < [any integer]; [var]++) {
    [time computation with transformations]
    [time computation without transformations]
    ...
  }
  ...
}

# example
TEST(workspaces, loopcontractfuse_real) {
  int L = 16;
  int M = 16;
  int N = 16;
  Tensor<double> A("A", {L, M, N}, Format{Dense, Dense, Dense});

  std::string mat_file = util::getFromEnv("TENSOR_FILE", "");

  Tensor<double> B = read(mat_file, Format({Dense, Sparse, Sparse}), true);
  B.setName("B");
  B.pack();

  Tensor<double> C("C", {B.getDimension(0), L}, Format{Dense, Dense});
  for (int i=0; i<B.getDimension(0); i++) {
    for (int l=0; l<L; l++) {
      C.insert({i, l}, (double) i);
    }
  }
  C.pack();
  Tensor<double> D("D", {B.getDimension(1), M}, Format{Dense, Dense});
  for (int j=0; j<B.getDimension(1); j++) {
    for (int m=0; m<M; m++) {
      D.insert({j, m}, (double) j);
    }
  }
  D.pack();
  Tensor<double> E("E", {B.getDimension(2), N}, Format{Dense, Dense});
  for (int k=0; k<B.getDimension(2); k++) {
    for (int n=0; n<N; n++) {
      E.insert({k, n}, (double) k);
    }
  }
  E.pack();

  IndexVar i("i"), j("j"), k("k"), l("l"), m("m"), n("n");
  A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n);

  IndexStmt stmt = A.getAssignment().concretize();

  std::cout << stmt << endl;

	/* BEGIN loopcontractfuse_real TEST */
	vector<int> path0;
	vector<int> path1 = {0};
	vector<int> path2 = {1};
	vector<int> path3 = {0, 1};
	stmt = stmt
		.reorder({l, i, j, k, m, n})
		.loopfuse(3, true, path0)
		.loopfuse(2, true, path1)
		.reorder(path2, {n, m, k})
		.reorder(path3, {k, j})
		;
	/* END loopcontractfuse_real TEST */


  stmt = stmt.concretize();
  cout << "final stmt: " << stmt << endl;
  printCodeToFile("loopcontractfuse", stmt);

  A.compile(stmt.concretize());
  A.assemble();

  Tensor<double> expected("expected", {N, N, N}, Format{Dense, Dense, Dense});
  expected(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n);
  expected.compile();
  expected.assemble();

  clock_t begin;
  clock_t end;

  for (int i=0; i<3; i++) {
    begin = clock();
    A.compute(stmt);
    end = clock();
    double elapsed_secs = double(end - begin) / CLOCKS_PER_SEC * 1000;

    begin = clock();
    expected.compute();
    end = clock();
    double elapsed_secs_ref = double(end - begin) / CLOCKS_PER_SEC * 1000;

    std::cout << elapsed_secs << std::endl;
    std::cout << elapsed_secs_ref << std::endl;
  }

std::cout << "workspaces, loopcontractfuse -> execution completed for matrix: " << mat_file << std::endl;

}


```