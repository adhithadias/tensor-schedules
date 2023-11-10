from src.config import Config
from src.autosched import sched_enum, get_schedules_unfused
import sys
from copy import deepcopy
from random import randint
import regex as re
from src.file_storing import Modify_Lines

header_to_read = r'/\*.*\*/'
footer_to_read = r'/\*.*\*/'
test_rep_for_loop = r'(\s*for\s*\(\s*int \s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*0\s*;\s*\2<\s*)(\d+)(\s*;\s*\2\+\+\s*\)\s*{\s*)'
MAX_LINES = 100000
# path = "~/SparseLNR_Most_Recent"

class Gen_Test_Code:
    def __init__(self, config:Config, test_name:str, file, tensor_accesses:dict = None):
        self.test_name = test_name
        self.file = file
        self.paths = []
        self.reorders = []
        self.extra_paths = []
        self.extra_reorders = []
        self.no_fusion = False
        self.partial_fusion = False
        self.config = config
        self.tensor_accesses = tensor_accesses
        
        if config.prod == None:
            self.no_fusion = True
            
        if config.fused == 0:
            self.partial_fusion = True
        
        # retrieves all paths for fusion
        self.get_paths([], config)
        
        if not self.no_fusion: self.get_extra_paths()
        # print(self.paths, file=sys.stdout)
        
        # sets all of the reorders for loop fusion
        for path in self.paths:
            # get all indices
            given_config = self.retrieve_path(path, config)
            if given_config.fused == 0: 
                self.reorders.append(())              
                continue
            # self.indices = set()
            # self.get_indices(given_config.input_idx_order)
            # reordering = self.get_reordering(given_config.input_idx_order)
            reordering = given_config.original_idx_perm
            # print(reordering)
            
            if len(self.reorders) == 0:
                if reordering == None: continue
                self.reorders.append(reordering)
            else:
                old_ordering = None
                for end_point in range(len(path)):
                    index = [str(el) for el in self.paths].index(str(path[:-(end_point + 1)]))
                    old_ordering = [i for i in self.reorders[index] if i in reordering]
                    if len(old_ordering) > 0: break
                if(str(reordering) != str(old_ordering)):
                    new_reorderings = []
                    i = 0
                    
                    parent_config = self.retrieve_path(path[1:], config)
                    if parent_config.fused == 0:
                        self.reorders.append(reordering)
                        continue
                    while i < len(old_ordering):
                        if reordering[i] == old_ordering[i]: i += 1
                        else:
                            list_old = [old_ordering[i]]
                            list_new = [reordering[i]]
                            i += 1
                            while(set(list_old) != set(list_new) and i < len(old_ordering)):
                                list_old.append(old_ordering[i])
                                list_new.append(reordering[i])
                                i += 1
                            if len(list_new) > 1: new_reorderings.append(list_new)
                    self.reorders.append(new_reorderings)
                else: self.reorders.append([])                    
        
        # get reorderings for leaf node schedules
        for extra_path in self.extra_paths:
            given_config = self.retrieve_path(extra_path, config)
            reordering = given_config.original_idx_perm
            
            if len(self.reorders) == 0:
                self.extra_reorders.append(reordering)
            else:
                old_ordering = None
                for end_point in range(len(extra_path)):  
                    index = [str(el) for el in self.paths].index(str(extra_path[:-(end_point + 1)]))
                    old_ordering = [i for i in self.reorders[index] if i in reordering]
                    
                    # if parent_config.fused == 0:
                    #     old_ordering = parent_config.input_idx_order
                    
                    if len(old_ordering) > 0: break
                # print()
                # print(reordering)
                # print(self.reorders[index])
                # print(old_ordering)
                # print(given_config)
                # print(extra_path)
                # print()
                
                if str(reordering) != str(old_ordering):
                    new_reorderings = []
                    i = 0
                    parent_config = self.retrieve_path(extra_path[:-1], config)
                    if parent_config.fused == 0:
                        self.extra_reorders.append(reordering)
                        continue
                    
                    while i < len(old_ordering):
                        if reordering[i] == old_ordering[i]: i += 1
                        else:
                            list_old = [old_ordering[i]]
                            list_new = [reordering[i]]
                            i += 1
                            while(set(list_old) != set(list_new) and i < len(old_ordering)):
                                list_old.append(old_ordering[i])
                                list_new.append(reordering[i])
                                i += 1
                            if len(list_new) > 1: new_reorderings.append(list_new)
                    self.extra_reorders.append(new_reorderings)
                else: self.extra_reorders.append([])  
        
        # removing extra paths
        temp_path = []
        temp_reorders = []
        for i, extra_reorder in enumerate(self.extra_reorders):
            if len(extra_reorder) == 0 or (len(extra_reorder) == 1 and len(extra_reorder[0]) == 0):
                continue
            temp_path.append(self.extra_paths[i])
            temp_reorders.append(extra_reorder)
            
        self.extra_reorders = temp_reorders
        self.extra_paths = temp_path
        
        self.add_header()
        self.add_expression()
        
        for i, path in enumerate(self.paths + self.extra_paths):
            # add paths
            if len(self.reorders) == 0 and self.no_fusion: continue
            if(len(path) > 0):  
                self.add_vector(name=("path" + str(i)), init=("{" + ", ".join([str(el) for el in path]) + "}"))
            else:
                self.add_vector(name=("path" + str(i)))

        # print scheduling commands
        if (len(self.reorders) > 0 or len(self.extra_reorders)):
            self.print_data("stmt = stmt")
            
        
        for i, reorder in enumerate(self.reorders):
            self.add_reorder(reorder, i)
            config_to_split = self.retrieve_path(self.paths[i], config)
            # if i != 0:
            if config_to_split.prod and config_to_split.prod_on_left:
                self.add_loopfuse(len(config_to_split.prod.expr), config_to_split.prod_on_left, i)
            elif config_to_split.cons and not config_to_split.prod_on_left:
                self.add_loopfuse(len(config_to_split.cons.expr) - 1, config_to_split.prod_on_left, i)
            elif self.no_fusion:
                continue
            else: 
                assert SyntaxError
                # parent_config = self.retrieve_path(self.paths[i][:-1], config)
                # if (parent_config.prod and self.paths[i][-1] == 0) or not parent_config.prod_on_left:
                #     self.add_loopfuse(self.get_pos(config_to_split, True), config_to_split.prod_on_left, i)
                # else:
                #     self.add_loopfuse(self.get_pos(config_to_split, False), config_to_split.prod_on_left, i)
            # else: self.add_loopfuse(self.get_pos(config_to_split, True), config_to_split.prod_on_left, i)
        for i, extra_reorder in enumerate(self.extra_reorders):
            self.add_reorder(extra_reorder, i + len(self.reorders))
        
        if len(self.reorders) != 0 or not self.no_fusion: self.print_data(";", 2)
        self.add_end()
    
    def print_data(self, data:str, num_tabs=1) -> None:
      print(data, file=self.file)
      
    def get_indices(self, input_tuple:tuple) -> None:
        for item in input_tuple:
            if type(item) == tuple:
                self.get_indices(item)
            else:
                self.indices.add(item)
    
    def get_pos(self, config:Config, is_producer: bool):
        extra = 0
        if not is_producer:
            extra = 1
        if(config.prod_on_left):
            return len(config.expr) - len(config.cons.expr) + extra
        else:
            return len(config.expr) - len(config.prod.expr) + extra
        
    
    def retrieve_path(self, ordering:list, config:Config) -> Config:
        if len(ordering) == 0:
            return config
        else:
            if ordering[0] == 0:
                next_config = config.prod
            else:
                next_config = config.cons
            return self.retrieve_path(ordering[1:], next_config)
    
    def get_paths(self, path:tuple, config:Config) -> None:
        """This retrieves all possible paths of fusion

        Args:
            path (tuple): path so far of fusion
            config (Config): Config class
        """
        if type(config.input_idx_order[-1]) != tuple and config.prod == None:
            if self.no_fusion == True: self.paths.append(path)
            return
        else:
            self.paths.append(path)
            
            if (len(config.input_idx_order) > 1 and type(config.input_idx_order[-2]) == tuple and len(config.input_idx_order[-2]) > 0 and type(config.input_idx_order[-2][-1]) == tuple) or config.fused == 0:
                self.get_paths(path + [0], config.prod)
            if (len(config.input_idx_order) > 1 and type(config.input_idx_order[-1]) == tuple and len(config.input_idx_order[-1]) > 0 and type(config.input_idx_order[-1][-1]) == tuple) or config.fused == 0:
                self.get_paths(path + [1], config.cons)
            
            # if config.prod_on_left:
            #     self.get_paths(path + [0], config.prod)
            #     self.get_paths(path + [1], config.cons)
            # else:
            #     self.get_paths(path + [1], config.prod)
            #     self.get_paths(path + [0], config.cons)
        
    def get_extra_paths(self):
        for path in self.paths:
            if (path + [0]) not in self.paths:
                self.extra_paths.append(path + [0])
            if (path + [1]) not in self.paths:
                self.extra_paths.append(path + [1])
    
    def add_header(self):
        self.print_data("/* BEGIN " + self.test_name + " TEST */")
        
    def add_expression(self):
        result = self.config.output + "(" + ", ".join([idx for idx in self.config.output_idx_order]) + ") = "
        
        for i, tensor in enumerate(self.config.expr):
            result += tensor + "(" + ", ".join([idx for idx in self.tensor_accesses[tensor]]) + ")"
            if i != len(self.config.expr) - 1:
                result += " * "
                
        self.print_data(result + ";")
        self.print_data("")
        self.print_data("IndexStmt stmt = " + self.config.output + ".getAssignment().concretize();")
        self.print_data("std::cout << stmt << endl;")
        self.print_data("")
    
    def add_end(self):
        self.print_data("/* END " + self.test_name + " TEST */")
        
    def add_vector(self, name: str, type="int", init=""):
        if len(init) == 0:
            self.print_data("vector<" + type + "> " + name + ";")
        else:
            self.print_data("vector<" + type + "> " + name + " = " + init + ";")
    def add_reorder(self, inputs:tuple, path=0):
        if len(inputs) == 0:
            return
        reorderings = "{"
        for input in inputs:
            if type(input) != tuple and type(input) != list:
                reorderings += str(input) + ", "
            else:
                if reorderings[-2:] == ", ":
                    reorderings = reorderings[:-2]
                    reorderings += "}, {"
                reorderings += ", ".join([str(el) for el in input]) + "}, {"
        if len(reorderings) > 3 and reorderings[-4:] == "}, {":
            reorderings = reorderings[:-3]
        elif reorderings[-2:] == ", ":
            reorderings = reorderings[:-2] + "}"
        if path == 0:
            self.print_data("\t.reorder(" + reorderings + ")")
        else:
            self.print_data("\t.reorder(" + "path" + str(path) + ", " + reorderings + ")")

        
    def add_loopfuse(self, pos:int, prod_on_left:bool, path_num:int):
        if prod_on_left == None: prod_on_left = True
        self.print_data("\t.loopfuse(" + str(pos) + ", " + str(prod_on_left).lower() + ", path" + str(path_num) + ")")

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
        if type(input_idx) == tuple:
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
    
class Write_Test_Code(Gen_Test_Code):
    def __init__(self, config: Config, test_name: str, filename: str, num_tests=None, tensor_accesses = None):
        # text to hold lines indicating schedule
        self.schedule_text = []
        
        # test name line of C++ code to recognize
        self.test_regex = self.get_test_regex(test_name)
        
        # open file for reading
        try:
            r_file_ptr = open(filename, "r")
        except OSError:
            print("Failed to open file for reading", file=sys.stderr)
            return
        except TypeError:
            print("Invalid type of filename.  Please enter a string", file=sys.stderr)
            return
        
        # initialize parent class
        super().__init__(config, test_name, r_file_ptr, tensor_accesses)
        
        # initialize list of all lines in file
        new_text = []
        
        file_writer = Modify_Lines(r_file_ptr.readlines(MAX_LINES))
        file_writer.match_replacement_point(self.test_regex)
        
        
        file_writer.replace_between_headers(header_to_read, footer_to_read, self.schedule_text, True, True)
        file_writer.modify_line(test_rep_for_loop, r'\g<1>' + str(num_tests) + r'\g<4>')
        
        # write new compiled info back to file
        w_file_ptr = open(filename, "w")
        w_file_ptr.writelines(new_text)
        w_file_ptr.close()
        
        
        # for line in r_file_ptr:
        #     if test_read: 
        #         new_text.append(line)
        #         continue
        #     text = re.search(self.test_regex, line)
        #     if text: 
        #         # change to true so less computations
        #         test_read = True
        #         try:
        #             # read and store lines until header is reached
        #             new_text.append(line)
                    
        #             for line2 in r_file_ptr:
        #                 # next_line = r_file_ptr.readline()
        #                 if re.search(header_to_read, line2): 
        #                     header_read = True
        #                     break
        #                 new_text.append(line2)
                        
        #             # add schedule text in
        #             new_text.extend(self.schedule_text)
                    
        #             # read only until footer is reached
        #             for line2 in r_file_ptr:
        #                 # next_line = r_file_ptr.readline()
        #                 if re.search(footer_to_read, line2): 
        #                     footer_read = True
        #                     break
                          
        #             # read until for loop reached
        #             if num_tests != None:
        #                 for line2 in r_file_ptr:
        #                     if re.search(test_rep_for_loop, line2):
        #                         new_text.append(re.sub(test_rep_for_loop, r'\g<1>' + str(num_tests) + r'\g<4>', line2))
        #                         break
        #                     else: new_text.append(line2)
                        
                    
        #         except EOFError:
        #             print("Invalid header or footer", file=sys.stderr)
        #             r_file_ptr.close()
        #             return
        #     else: new_text.append(line)
        
        # r_file_ptr.close()
        
        # # check if valid 
        # if not test_read: 
        #     print("Invalid test name", file=sys.stderr)
        #     return
        # if not header_read:
        #     print("No header present", file=sys.stderr)
        #     return
        # if not footer_read:
        #     print("No footer present", file=sys.stderr)
        #     return

    def print_data(self, data: str, num_tabs=1) -> None:
        """Override print_data to write all info into list

        Args:
            data (str): data to append to list
        """
        self.schedule_text.append("\t" * num_tabs + data + "\n")
    
    def get_test_regex(self, test_name: str):
        return re.compile(f"TEST\(workspaces, {test_name}\)")
    
    
if __name__ == "__main__":
    schedules = []
    accesses = {
        'X': ('i', 'm'),
        'A': ('i', 'j'),
        'B': ('j', 'k'),
        'C': ('k', 'l'),
        'D': ('l', 'm')
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i')],
        # 'B': [],
        # 'C': [],
        # 'D': [],
    }
    # sched_enum('X', ['A','B','C','D'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)
    cache = {}
    schedules = list(get_schedules_unfused('X', accesses['X'], ('A','B','C','D'), accesses, ('i', 'j', 'k', 'l', 'm'), tensor_idx_order_constraints, 1, cache))
    print("\n")
    counter_printing = 15
    counter = 1
    test_num = 1
    
    test_sched = Config('X', ('A', 'B', 'C', 'D'), ('i', 'j', 'k', 'l', 'm'), ('i', 'j', 'l', 'k', 'm'), 2)
    test_sched.original_idx_perm = ('i', 'j', 'l', 'k', 'm')
    # Write_Test_Code(test_sched, "loopfuse", "/home/shay/a/anderslt/tensor-schedules/src/tests-workspaces.cpp")
    
    # Write_Test_Code(schedules[0], "loopfuse", "/home/shay/a/anderslt/tensor-schedules/src/tests-workspaces.cpp")
    # Write_Test_Code(schedules[0], "loopfuse", "/home/shay/a/anderslt/tensor-schedules/src/tests-workspaces.cpp")
    # exit()
    for schedule in schedules:
        # if count_fusions(schedule) == 2 and schedule.fused:
            if type(schedule.input_idx_order[-1]) == tuple:
                Write_Test_Code(schedule, "sddmm_spmm_fake", "/home/shay/a/anderslt/tensor-schedules/src/tests-workspaces.cpp", 10, accesses)
                break
              
            counter = (counter % counter_printing) + 1
            # if counter == counter_printing:
                # Gen_Test_Code(schedule, "Test " + str(test_num), sys.stdout)
            test_num += 1
            # break
            # break
          

          
          
# [x] path is wrong when printing