from src.config import Config
from src.solver_config import Solver_Config
from src.autosched import sched_enum
# from src.visitor import PrintConfigVisitor
from src.visitor2 import PrintConfigVisitor
from src.gen_taco_rep import Gen_Test_Code
import sys

tests = []

# 0
tests.append({
  "accesses": {
      'X': ('i', 'm'),
      'A': ('i', 'j'),
      'B': ('j', 'k'),
      'C': ('k', 'l'),
      'D': ('l', 'm')
  },
  "tensor_idx_order_constraints": {
      'A': [('j', 'i')]
  },
  "output_tens": 'X',
  "z3_parameters": []
})

# 1
tests.append({
  "accesses": {
      'X': ('i', 'l'),
      'A': ('i', 'j'),
      'B': ('j', 'k'),
      'C': ('k', 'l')
  },
  "tensor_idx_order_constraints": {
      'A': [('j', 'i')]
  },
  "output_tens": 'X'
})

# 2
tests.append({
  "accesses": {
      'A': ('l', 'm', 'n'),
      'B': ('i', 'j', 'k'),
      'C': ('i', 'l'),
      'D': ('j', 'm'),
      'E': ('k', 'n')
  },
  "tensor_idx_order_constraints": {
      'B': [('j', 'i'), ('k', 'j'), ('k', 'i')]
  },
  "output_tens": 'A'
})

# 3
tests.append({
  "accesses": {
      'A': ('i', 'l'),
      'B': ('i', 'j'),
      'C': ('i', 'k'),
      'D': ('j', 'k'),
      'E': ('j', 'l')
  },
  "tensor_idx_order_constraints": {
      'B': [('j', 'i')]
  },
  "output_tens": 'A'
})

# 4
tests.append({
  "accesses": {
      'A': ('i', 'm'),
      'B': ('i', 'j'),
      'C': ('i', 'k'),
      'D': ('j', 'k'),
      'E': ('j', 'l'),
      'F': ('l', 'm')
  },
  "tensor_idx_order_constraints": {
      'B': [('j', 'i')]
  },
  "output_tens": 'A'
})

# 5
tests.append({
  "accesses": {
      'A': ('i', 'l', 'm'),
      'B': ('i', 'j', 'k'),
      'C': ('j', 'l'),
      'D': ('k', 'm'),
  },
  "tensor_idx_order_constraints": {
      'B': [('j', 'i'), ('k', 'j'), ('k', 'i')]
  },
  "output_tens": 'A'
})

def run_algorithm(tests_to_run):
    if type(tests_to_run) == int:
        tests_to_run = [tests_to_run]
    for test_num in tests_to_run:
        file_name = open("test_" + str(test_num) + ".txt", 'w')
        schedules = []
        output = tests[test_num]["output_tens"]
        expr = list(tests[test_num]["accesses"].keys())
        expr.remove(output)
        sched_enum(output, expr, tests[test_num]["accesses"][output], tests[test_num]["accesses"], tests[test_num]["tensor_idx_order_constraints"], schedules)
        
        solver = Solver_Config(tests[test_num]["accesses"], tests[test_num]["tensor_idx_order_constraints"])
        
        printer = PrintConfigVisitor(tests[test_num]["accesses"], out_file=file_name)
        # printer = PrintConfigVisitor(tests[test_num]["accesses"])
        print('\n\n\n\n\n\n\n', file=file_name)
        print(len(schedules), file=file_name)

        print('\n\n\n\n\n\n\n', file=file_name)
        pruned_schedules = solver.prune_using_depth(schedules)
        print(len(pruned_schedules))
        pruned_schedules = solver.prune_schedules(pruned_schedules)
        
        print(len(pruned_schedules), file=file_name)

        print('/**************************************************************************/', file=file_name)
        print('/********************** PRINTING SCHEDULES ********************************/', file=file_name)
        print('/**************************************************************************/', file=file_name)

        for schedule in pruned_schedules:
            schedule.accept(printer)
            Gen_Test_Code(schedule, "TEST", file_name)
            print('-----------', file=file_name)
        file_name.close()




if __name__ == "__main__":
    run_algorithm([4])
