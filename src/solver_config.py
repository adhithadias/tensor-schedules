from src.config import Config
from z3 import *

min_dense = 10
max_dense = 100
min_sparse = 5
max_sparse = 50

class Solver_Config:
  def __init__(self, output: str, expr: list, output_idx_order: list, tensor_accesses: dict,
              tensor_idx_order_constraints: dict, scheds: list) -> None: 
      constraints = []
      # TODO change to account for sparse tensors
      self.solver = Solver()
      
      # list of all indices separated by dense/sparse
      self.total_indices = {
        "dense": {},
        "sparse": {}
      }
      
      # get dense set of indices
      dense_set = set(index for indexes in tensor_accesses.values() for index in indexes)
      
      # initializes dense index variables as ints
      for element in dense_set:
          self.total_indices["dense"][element] = Int(element)
      
      # get sparse set of indices
      sparse_set = set()
      for constraints in tensor_idx_order_constraints.values():
          for pair in constraints:
              if len(pair) > 0:
                  sparse_set.add(pair[0] + "pos")
      
      # initializes sparse index variables as ints
      for element in sparse_set:
          self.total_indices["sparse"][element] = Int(element)
                  
      # adds minimum and maximum constraints for dense
      for index in self.total_indices["dense"].values():
          self.solver.add(index > min_dense, index < max_dense)
          
      # adds minimum and maximum constraints for sparse
      for index in self.total_indices["sparse"].values():
          self.solver.add(index > min_sparse, index < max_sparse)
          
      # add sparse constraints
      for key in self.total_indices["sparse"].keys():
          self.solver.add(self.total_indices["sparse"][key] < self.total_indices["dense"][key[0:-3]])
      
      self.solver.push()
      print(self.solver)
  
  def compare_schedules(self, config_1:Config, config_2:Config) -> int:
      
      
      return 0

schedules = []
accesses = {
    'X': ['i', 'm'],
    'A': ['i', 'j'],
    'B': ['j', 'k'],
    'C': ['k', 'l'],
    'D': ['l', 'm']
}
tensor_idx_order_constraints = {
    'A': [('j', 'i')],
    # 'B': [],
    # 'C': [],
    # 'D': [],
}

Solver_Config('X', ['A', 'B', 'C', 'D'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)

