from z3 import *
from src.complexity import retrieve_all_complexities
from src.autosched import sched_enum
from src.config import Config

# Given schedule and returns validity given various constraints
# Example:
#   A(i,j) = B(i,k) * C(k,j) unfused with input ordering i,j,k and output ordering i,j
s = Solver()


def get_schedules(accesses={}, result_tensor="") -> list:
  if result_tensor not in accesses:
    print("Error: Invalid Resultant Tensor", file=sys.stderr)
    return []
  tens_list = list(accesses.keys())
  tens_list.remove(result_tensor)
  return sched_enum(tens_list, accesses[result_tensor], accesses)

if __name__ == "__main__":
# Step 1: retrieve listing of all possible schedules for given computation  
  schedules = get_schedules(accesses={
      'X': ['i', 'm'],
      'A': ['i', 'j'],
      'B': ['j', 'k'],
      'C': ['k', 'l'],
      'D': ['l', 'm']
  }, result_tensor="X")

# Step 2: Retrieve "global" complexities
  glob_complex = retrieve_all_complexities(schedules)
  
# ***Step 3: Filter out duplicate schedules 

# Step 4: Separate "global" complexities into separate schedules to find "local" complexities

# Step 5: Send "local" schedules to autoscheduler to optimize them

# Step 6: Combine local schedules complexities with global schedule complexity to achieve an overall complexity

# Step 7: Using set of requirements for maximum space allowed, find the schedule with optimal runtime using Z3




# accesses = {
#     'X': ['i', 'm'],
#     'A': ['i', 'j'],
#     'B': ['j', 'k'],
#     'C': ['k', 'l'],
#     'D': ['l', 'm']
# }
# schedules = sched_enum(['A', 'B', 'C', 'D'], accesses['X'], accesses)
# print(retrieve_all_complexities(schedules))


# x = Int('x')
# y = Int('y')

# solve(x > y, x < 5, x > 0)


