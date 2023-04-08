from src.config import Config
from src.autosched import sched_enum
import sys
from copy import deepcopy
from random import randint

class Gen_Test_Code:
    def __init__(self, config:Config, test_name:str, file):
        self.test_name = test_name
        self.file = file
        self.paths = []
        self.reorders = []
        
        # retrieves all paths for fusion
        self.get_paths([], config)
        
        for path in self.paths:
            # get all indices
            given_config = self.retrieve_path(path, config)
            self.indices = set()
            self.get_indices(given_config.input_idx_order)
            reordering = self.get_reordering(given_config.input_idx_order)
            
            if len(self.reorders) == 0:
                self.reorders.append(reordering)
            else:
                old_ordering = [i for i in self.reorders[-1] if i in reordering]
                print(old_ordering)
                
            
        
        self.add_header()
        
        for i, path in enumerate(self.paths):
            # add paths
            if(len(path) > 0):  
                self.add_vector(name=("path" + str(i)), init=("{" + ", ".join([str(el) for el in path]) + "}"))
            else:
                self.add_vector(name=("path" + str(i)))

        
        
        # print scheduling commands
        print("stmt = stmt", file=self.file)
        
        
        self.add_end()
        
    def get_indices(self, input_list:list) -> None:
        for item in input_list:
            if type(item) == list:
                self.get_indices(item)
            else:
                self.indices.add(item)
    
    def retrieve_path(self, ordering:list, config:Config) -> Config:
        if len(ordering) == 0:
            return config
        else:
            if (ordering[0] == 0 and config.prod_on_left) or (ordering[0] == 1 and not config.prod_on_left):
                next_config = config.prod
            else:
                next_config = config.cons
            return self.retrieve_path(ordering[1:], next_config)
    
    def get_paths(self, path:list, config:Config) -> None:
        """This retrieves all possible paths of fusion

        Args:
            path (list): path so far of fusion
            config (Config): Config class
        """
        if type(config.input_idx_order[-1]) != list:
            return
        else:
            self.paths.append(path)
            if config.prod_on_left:
                self.get_paths(path + [0], config.prod)
                self.get_paths(path + [1], config.cons)
            else:
                self.get_paths(path + [1], config.prod)
                self.get_paths(path + [0], config.cons)
        
    
    def add_header(self):
        print("/* BEGIN " + self.test_name + " TEST */", file=self.file)
    
    def add_end(self):
        print("*/ END " + self.test_name + " TEST */", file=self.file)
        
    def add_vector(self, name: str, type="int", init=""):
        if len(init) == 0:
            print("vector<" + type + "> " + name + ";", file=self.file)
        else:
            print("vector<" + type + "> " + name + " = " + init + ";", file=self.file)

    def get_index_orders(self, trav_mat, orderings=[[]]):
        """Returns all possible orderings of indexes

        Args:
            trav_mat (dict[dict]): traversal matrix
            *orderings (tuple[list]): sets of orderings to initialize traversal matrix

        Returns:
            list[list]: all orderings based upon traversal matrix
        """
        trav_mat = deepcopy(trav_mat)
        # sets matrix up
        for ordering in orderings:
          pairs = list(zip(ordering, ordering[1:] + ordering[:1]))
          pairs.pop()   # remove because this would wrap back around
          for pair in pairs:
            if(trav_mat[pair[0]][pair[1]] == 0):
              trav_mat[pair[0]][pair[1]] = 1
              trav_mat["Total"][pair[1]] += 1

        tot_index_orders = []

        def get_indexes(trav_mat={}, index_order=[]):
          # base case
          if len(trav_mat) == 1:
            tot_index_orders.append(index_order)
            return

          # if impossible ordering, return
          if 0 not in trav_mat["Total"].values():
            return

          # get all next possible indices in ordering
          zero_columns = []
          for key, val in trav_mat["Total"].items():
            if val == 0 and key not in index_order:
              zero_columns.append(key)

          # if there becomes branch in possible indexes
          for index in zero_columns:
            index_cpy = deepcopy(index_order)
            trav_cpy = deepcopy(trav_mat)
            index_cpy.append(index)
            for value in trav_cpy.values():
              del value[index]
            del trav_cpy[index]
            trav_cpy = self._updateTotals(trav_cpy)
            get_indexes(trav_cpy, index_cpy)

        get_indexes(trav_mat, [])

        return tot_index_orders

    def _updateTotals(self, trav_mat={}):
        """Updates totals of traversal matrix"""
        trav_mat = deepcopy(trav_mat)
        new_total = trav_mat["Total"]
        for key in new_total.keys():
          new_total[key] = 0
        for key, value in trav_mat.items():
          if(key == "Total"):
            continue
          else:
            for key2, value2 in value.items():
              new_total[key2] += value2
        trav_mat["Total"] = new_total
        return trav_mat

    def get_index_orders_from_idx_order(self, input_idx_order=[]):
      """Returns all orderings as a list of lists\n
      Example:\n
      ['m', ['l', [], ['j', 'k']], ['i', 'j']] -> [['m', 'l', 'j', 'k'], ['m', 'i', 'j']]"""
      shared_order = []
      producer = []
      consumer = []
      prod_read = False
      for input_idx in input_idx_order:
        if type(input_idx) == list:
          if not prod_read:
            prod_read = True
            producer = self.get_index_orders_from_idx_order(input_idx)
          else:
            consumer = self.get_index_orders_from_idx_order(input_idx)
        else:
          shared_order.append(input_idx)
      if not prod_read:
        return [shared_order]

      prod_ordering = []
      for ordering in producer:
        prod_ordering.append(shared_order + ordering)
      cons_ordering = []
      for ordering in consumer:
        cons_ordering.append(shared_order + ordering)

      return prod_ordering + cons_ordering
    
    
    def _build_traversal_matrix(self, indexes=list):
      """Builds matrix of 0's where Mat['i']['j'] == 1 means i -> j ordering\n
      Example: (t represents Total)\n
      _ i j k l m\n
      i 0 0 0 0 0\n
      j 0 0 0 0 0\n
      k 0 0 0 0 0\n
      l 0 0 0 0 0\n
      m 0 0 0 0 0\n
      t 0 0 0 0 0"""
      mat = {}
      row_indexes = deepcopy(indexes)
      indexes.append('Total')
      for index1 in indexes:
        mat[index1] = {}
        for index2 in row_indexes:
          mat[index1][index2] = 0

      return mat
    
    def _delete_elements_trav_mat(self, trav_mat={}, els_to_del=[]):
      """Deletes indexes in list from all parts of traversal matrix"""
      trav_mat = deepcopy(trav_mat)
      for el in els_to_del:
        del trav_mat[el]
        for value in trav_mat.values():
          del value[el]

      return trav_mat
    
    def get_reordering(self, loop_order:list):
        # build traversal matrix from all indexes
        self.trav_mat = self._build_traversal_matrix(list(self.indices))
        
        valid_reorderings = self.get_index_orders(self.trav_mat, self.get_index_orders_from_idx_order(loop_order))
        self.trav_mat.clear()
        
        return valid_reorderings[0]

def count_fusions(config:Config):
    if (config.prod == None and config.cons == None) or not config.fused:
        return 0
    else:
        return 1 + count_fusions(config.prod) + count_fusions(config.cons)
    
if __name__ == "__main__":
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
    sched_enum('X', ['A','B','C','D'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)
    print("\n")
    counter_printing = 20
    counter = 0
    
    for schedule in schedules:
        if count_fusions(schedule) == 2 and schedule.fused:
            counter = (counter % counter_printing) + 1
            if counter == counter_printing:
                Gen_Test_Code(schedule, "Test 1", sys.stdout)
            # break
            
