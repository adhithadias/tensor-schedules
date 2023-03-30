large_number_value = 100




class Solver_Config:
  def __init__(self, output: str, expr: list, output_idx_order: list, tensor_accesses: dict,
              tensor_idx_order_constraints: dict, scheds: list) -> None: 
      constraints = []
      # TODO change to account for sparse tensors
      
      # get total list of indexes
      index_list = set()
      index_list = [index_list.union(set(indexes)) for indexes in tensor_accesses.values()]
      
      # set constraints to approximate large numbers
      for index in index_list:
          constraints.append(index + ">" + "1000")
          
      



