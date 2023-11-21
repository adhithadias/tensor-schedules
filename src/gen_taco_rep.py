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
    def __init__(self, config:Config, test_name:str, tensor_accesses:dict = None):
        self.test_name = test_name
        self.vector_num = 0
        self.sep_scheds = []
        self.temp_rename = []
        
        self.no_fusion = False
        self.unfused = False
        self.orig_config = deepcopy(config)
        self.config = deepcopy(config)
        self.tensor_accesses = tensor_accesses
        self.temp_accesses = {}
        
        if config.prod == None:
            self.no_fusion = True
        
        # replace tensor names with temporary names if any part of schedule is unfused/ also separates different schedules,
        # holding in sep_schedules
        self.get_temps_names(config)
        
        if len(self.sep_scheds) == 0: 
            self.sep_scheds.append(config)
            self.unfused = True
        else:
            for sched in self.sep_scheds:
                if sched.temporary: 
                    keys = list(sched.temporary.keys())
                    self.temp_accesses[keys[0]] = sched.temporary[keys[0]]
                    self.temp_accesses[keys[1]] = sched.temporary[keys[1]]
        
        # holds statement objects with relevant info for each separate schedule
        self.statements = [self.statement_obj for _ in range(len(self.sep_scheds))]
        
        for i, config in enumerate(self.sep_scheds):
            self.get_lines(config, i)     
        
        """# retrieves all paths for fusion
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
        for i, extra_reorder in enumerate(self.extra_reorders):
            self.add_reorder(extra_reorder, i + len(self.reorders))
        
        if len(self.reorders) != 0 or not self.no_fusion: self.print_data(";", 2)
        self.add_end()"""
    
    
    @property
    def statement_obj(self):
        return {
          "paths": [],
          "extra_paths": [],
          "reorders": [],
          "extra_reorders": [],
          "expr": [],
          "lines": {
              "tens_decl": "",
              "expr_decl": "",
              "stmt_decl": "",
              "concretize": "",
              "compile": "",
              "assemble": "",
              "compute": "",
              "sched_change": []
          },
          "root_sched": False
        }
        
    def get_tensor_expr(self, tensor):
        assert tensor in self.tensor_accesses or tensor in self.temp_accesses
        if tensor in self.tensor_accesses:
            return f'{tensor}({",".join(self.tensor_accesses[tensor])})'
        else:
            return f't_{tensor}({",".join(self.temp_accesses[tensor])})'
        
    def get_lines(self, config:Config, stmt_num=0):
        # retrieves all paths for fusion
        self.get_paths([], config, stmt_num)
        
        # add extra paths for reordering inner expressions
        if config.prod != None: self.get_extra_paths(stmt_num)
        
        # sets all of the reorders for loop fusion
        self.set_reorders(config, stmt_num=stmt_num)
        self.set_reorders(config, path_name="extra_paths", reorder_name="extra_reorders", stmt_num=stmt_num)
        """for path in self.statements[stmt_num]["paths"]:
            # get all indices
            given_config = self.retrieve_path(path, config)
            reordering = given_config.original_idx_perm
            
            if len(self.statements[stmt_num]["reorders"]) == 0:
                if reordering == None: continue
                self.statements[stmt_num]["reorders"].append(reordering)
            else:
                old_ordering = None
                for end_point in range(len(path)):
                    index = [str(el) for el in self.statements[stmt_num]["paths"]].index(str(path[:-(end_point + 1)]))
                    old_ordering = [i for i in self.statements[stmt_num]["reorders"][index] if i in reordering]
                    if len(old_ordering) > 0: break
                if(str(reordering) != str(old_ordering)):
                    new_reorderings = []
                    i = 0
                    
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
                    self.statements[stmt_num]["reorders"].append(new_reorderings)
                else: self.statements[stmt_num]["reorders"].append([])"""
       
        # sets all of the extra reorders for loop fusion
        """for path in self.statements[stmt_num]["extra_paths"]:
            # get all indices
            given_config = self.retrieve_path(path, config)
            reordering = given_config.original_idx_perm
            
            if len(self.statements[stmt_num]["extra_reorders"]) == 0:
                if reordering == None: continue
                self.statements[stmt_num]["extra_reorders"].append(reordering)
            else:
                old_ordering = None
                for end_point in range(len(path)):
                    index = [str(el) for el in self.statements[stmt_num]["extra_paths"]].index(str(path[:-(end_point + 1)]))
                    old_ordering = [i for i in self.statements[stmt_num]["extra_reorders"][index] if i in reordering]
                    if len(old_ordering) > 0: break
                if(str(reordering) != str(old_ordering)):
                    new_reorderings = []
                    i = 0
                    
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
                    self.statements[stmt_num]["extra_reorders"].append(new_reorderings)
                else: self.statements[stmt_num]["extra_reorders"].append([])"""
                
        # removing extra paths
        temp_path = []
        temp_reorders = []
        for i, extra_reorder in enumerate(self.statements[stmt_num]["extra_reorders"]):
            if len(extra_reorder) == 0 or (len(extra_reorder) == 1 and len(extra_reorder[0]) == 0):
                continue
            temp_path.append(self.statements[stmt_num]["extra_paths"][i])
            temp_reorders.append(extra_reorder)
                         
        self.statements[stmt_num]["extra_reorders"] = temp_reorders
        self.statements[stmt_num]["extra_paths"] = temp_path
        
        # get various expressions needed for given computation
        if config.output == self.config.output: self.add_expression(config, stmt_num, False)
        else: self.add_expression(config, stmt_num)
        
        vec_nums = []
        for i, path in enumerate(self.statements[stmt_num]["paths"] + self.statements[stmt_num]["extra_paths"]):
            # add paths
            if len(self.statements[stmt_num]["reorders"]) == 0 and config.prod == None: continue
            if(len(path) > 0):  
                vec_nums.append(self.add_vector(name="path", init=("{" + ", ".join([str(el) for el in path]) + "}"), stmt_num=stmt_num))
            else:
                vec_nums.append(self.add_vector(name="path", stmt_num=stmt_num))

        # print scheduling commands
        if (len(self.statements[stmt_num]["reorders"]) > 0 or len(self.statements[stmt_num]["extra_reorders"]) > 0):
            self.statements[stmt_num]["lines"]["sched_change"].append("stmt = stmt")
            # self.print_data("stmt = stmt")
        
        
        for i, reorder in enumerate(self.statements[stmt_num]["reorders"]):
            self.add_reorder(reorder, stmt_num=stmt_num)
            config_to_split = self.retrieve_path(self.statements[stmt_num]["paths"][i], config)
            # if i != 0:
            if config_to_split.prod and config_to_split.prod_on_left:
                self.add_loopfuse(len(config_to_split.prod.expr), config_to_split.prod_on_left, vec_nums[i], stmt_num)
            elif config_to_split.cons and not config_to_split.prod_on_left:
                self.add_loopfuse(len(config_to_split.cons.expr) - 1, config_to_split.prod_on_left, vec_nums[i], stmt_num)
            elif config.prod == None:
                continue
            else: 
                assert SyntaxError
        for i, extra_reorder in enumerate(self.statements[stmt_num]["extra_reorders"]):
            self.add_reorder(extra_reorder, i + len(self.statements[stmt_num]["reorders"]), stmt_num)
        
        if len(self.statements[stmt_num]["reorders"]) != 0 or config.prod != None: 
            # self.print_data(";", 2)
            self.statements[stmt_num]["lines"]["sched_change"].append("\t\t;")
        # self.add_end()
        
        
        
        # if config.fused == 0:
        #     self.get_lines(config.prod, stmt_num + 1)
        #     self.get_lines(config.cons, stmt_num + 2)
            
        #     if stmt_num == 0:
        #         self.statements[stmt_num].append(config.output)
        #     else:    
        #         self.statements[stmt_num].append("t_" + config.output)
                
        #     self.statements[stmt_num].append("t_" + config.prod.output)
        #     self.statements[stmt_num].append("t_" + config.cons.output)

    def set_reorders(self, root_config:Config, path_name="paths", reorder_name="reorders", stmt_num=0):
        for path in self.statements[stmt_num][path_name]:
            # get all indices
            given_config = self.retrieve_path(path, root_config)
            reordering = given_config.original_idx_perm
            
            if len(self.statements[stmt_num][reorder_name]) == 0:
                if reordering == None: continue
                self.statements[stmt_num][reorder_name].append(reordering)
            else:
                old_ordering = None
                for end_point in range(len(path)):
                    index = [str(el) for el in self.statements[stmt_num][path_name]].index(str(path[:-(end_point + 1)]))
                    old_ordering = [i for i in self.statements[stmt_num][reorder_name][index] if i in reordering]
                    if len(old_ordering) > 0: break
                if(str(reordering) != str(old_ordering)):
                    new_reorderings = []
                    i = 0
                    
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
                    self.statements[stmt_num][reorder_name].append(new_reorderings)
                else: self.statements[stmt_num][reorder_name].append([])

    def get_temps_names(self, config:Config):
        if config.prod == None: return
        
        self.get_temps_names(config.prod)
        self.get_temps_names(config.cons)
        
        # only match schedule if unfused
        if config.fused == 0:
            for temp_replacement in self.temp_rename:
                if temp_replacement[1][0] in config.prod.expr:
                    config.prod.expr = [tens for tens in config.prod.expr if (tens not in temp_replacement[1] or tens == temp_replacement[1][0])]
                    config.prod.expr[config.prod.expr.index(temp_replacement[1][0])] = temp_replacement[0]
                if temp_replacement[1][0] in config.cons.expr:
                    config.cons.expr = [tens for tens in config.cons.expr if (tens not in temp_replacement[1] or tens == temp_replacement[1][0])]
                    config.cons.expr[config.cons.expr.index(temp_replacement[1][0])] = temp_replacement[0]
                    
            self.temp_rename.append((config.prod.output, config.prod.expr))
            self.temp_rename.append((config.cons.output, config.cons.expr))
            
            for temp_replacement in self.temp_rename:
                if temp_replacement[1][0] in config.expr:
                    config.expr = [tens for tens in config.expr if (tens not in temp_replacement[1] or tens == temp_replacement[1][0])]
                    config.expr[config.expr.index(temp_replacement[1][0])] = temp_replacement[0]
            
            # break apart schedule so it's separate
            if config.prod not in self.sep_scheds: self.sep_scheds.append(config.prod)
            if config.cons not in self.sep_scheds: self.sep_scheds.append(config.cons)
            if config not in self.sep_scheds: self.sep_scheds.append(config)
            config.fused = 1
            config.prod = None
            config.cons = None
            
    def __find_tensor_with_index(self, given_index):
        """Gets tensor with same accesses as the given index

        Args:
            given_index (str): index given to find tensor

        Returns:
            tuple: holds (tensor, index) 
        """
        for tensor, tens_indices in self.tensor_accesses.items():
            for index, tens_index in enumerate(tens_indices):
                if given_index == tens_index: return (tensor, index)
    
    def __find_tensors_with_indices(self, given_indices):
        all_accesses = []        
        for given_index in given_indices:
            all_accesses.append(self.__find_tensor_with_index(given_index))
        return all_accesses
    
    def get_temp_declaration(self, temp):
        assert temp in self.temp_accesses
        
        index_order = self.temp_accesses[temp]
        temp_accesses = self.__find_tensors_with_indices(index_order)
        accesses_str = ""
        for i, temp_access in enumerate(temp_accesses):
            accesses_str += f'{temp_access[0]}.getDimension({temp_access[1]})'
            if i != len(temp_accesses) - 1: accesses_str += f','
        
        format = ",".join(["Dense" for _ in range(len(temp_accesses))])
        declar = f'Tensor<double> t_{temp}(\"t_{temp}\", {{{accesses_str}}}, Format{{{format}}});'
        
        return declar
    # def replace_tens_with_temp(self, config:Config, temp: str, tens_names:tuple):
    #     if config == None: return
    #     if 
    
    
    def print_data(self, data:str, num_tabs=1) -> None:
      # print(data, file=self.file)
      print(data)
      
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
    
    def get_paths(self, path:tuple, config:Config, stmt_num=0) -> None:
        """This retrieves all possible paths of fusion

        Args:
            path (tuple): path so far of fusion
            config (Config): Config class
        """
        if type(config.input_idx_order[-1]) != tuple and config.prod == None:
            if config.prod == None: self.statements[stmt_num]["paths"].append(path)
            return
        else:
            self.statements[stmt_num]["paths"].append(path)
            
            if len(config.input_idx_order) > 1 and type(config.input_idx_order[-2]) == tuple and len(config.input_idx_order[-2]) > 0 and type(config.input_idx_order[-2][-1]) == tuple:
                self.get_paths(path + [0], config.prod)
            if len(config.input_idx_order) > 1 and type(config.input_idx_order[-1]) == tuple and len(config.input_idx_order[-1]) > 0 and type(config.input_idx_order[-1][-1]) == tuple:
                self.get_paths(path + [1], config.cons)
                
    def get_extra_paths(self, stmt_num=0):
        for path in self.statements[stmt_num]["paths"]:
            if (path + [0]) not in self.statements[stmt_num]["paths"]:
                self.statements[stmt_num]["extra_paths"].append(path + [0])
            if (path + [1]) not in self.statements[stmt_num]["paths"]:
                self.statements[stmt_num]["extra_paths"].append(path + [1])
    
    def add_header(self):
        self.print_data("/* BEGIN " + self.test_name + " TEST */")
        
    def add_expression(self, config:Config, stmt_num=0, temporary=True):
        if temporary: 
            self.statements[stmt_num]["lines"]["tens_decl"] = self.get_temp_declaration(config.output)
            self.statements[stmt_num]["lines"]["stmt_decl"] = f'IndexStmt stmt{stmt_num} = t_{config.output}.getAssignment().concretize();'
            self.statements[stmt_num]["lines"]["concretize"] = f'stmt{stmt_num} = stmt{stmt_num}.concretize();'
            self.statements[stmt_num]["lines"]["compile"] = f't_{config.output}.compile(stmt{stmt_num});'
            self.statements[stmt_num]["lines"]["assemble"] = f't_{config.output}.assemble();'
            self.statements[stmt_num]["lines"]["compute"] = f't_{config.output}.compute(stmt{stmt_num});'
        else: self.statements[stmt_num]["root_sched"] = True
        self.statements[stmt_num]["lines"]["expr_decl"] = f'{self.get_tensor_expr(config.output)} = {" * ".join([self.get_tensor_expr(tens) for tens in config.expr])};'
        # result = config.output + "(" + ", ".join([idx for idx in config.output_idx_order]) + ") = "
        
        # for i, tensor in enumerate(config.expr):
        #     result += tensor + "(" + ", ".join([idx for idx in self.tensor_accesses[tensor]]) + ")"
        #     if i != len(config.expr) - 1:
        #         result += " * "
        
        
        
        # self.print_data(result + ";")
        # self.print_data("")
        # self.print_data("IndexStmt stmt = " + config.output + ".getAssignment().concretize();")
        # self.print_data("std::cout << stmt << endl;")
        # self.print_data("")
    
    def add_end(self):
        self.print_data("/* END " + self.test_name + " TEST */")
        
    def add_vector(self, name: str, type="int", init="", stmt_num=0):
        if len(init) == 0:
            # self.print_data("vector<" + type + "> " + name + ";")
            self.statements[stmt_num]["lines"]["sched_change"].append(f'vector<{type}> {name}{self.vector_num};')
        else:
            # self.print_data("vector<" + type + "> " + name + " = " + init + ";")
            self.statements[stmt_num]["lines"]["sched_change"].append(f'vector<{type}> {name}{self.vector_num} = {init};')

        self.vector_num += 1      
        return self.vector_num - 1
        
    def add_reorder(self, inputs:tuple, path=0, stmt_num=0):
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
            # self.print_data("\t.reorder(" + reorderings + ")")
            self.statements[stmt_num]["lines"]["sched_change"].append("\t.reorder(" + reorderings + ")")
        else:
            # self.print_data("\t.reorder(" + "path" + str(path) + ", " + reorderings + ")")
            self.statements[stmt_num]["lines"]["sched_change"].append("\t.reorder(" + "path" + str(path) + ", " + reorderings + ")")

    def add_loopfuse(self, pos:int, prod_on_left:bool, path_num:int, stmt_num=0):
        if prod_on_left == None: prod_on_left = True
        self.statements[stmt_num]["lines"]["sched_change"].append("\t.loopfuse(" + str(pos) + ", " + str(prod_on_left).lower() + ", path" + str(path_num) + ")")
        # self.print_data("\t.loopfuse(" + str(pos) + ", " + str(prod_on_left).lower() + ", path" + str(path_num) + ")")

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
        self.temp_accesses = {}
        self.temp_decls = []
        self.temp_expressions = []
        self.stmts = {}
        self.num_tests = num_tests
        self.filename = filename
        
        # open file for reading
        # try:
        #     r_file_ptr = open(filename, "r")
        # except OSError:
        #     print("Failed to open file for reading", file=sys.stderr)
        #     return
        # except TypeError:
        #     print("Invalid type of filename.  Please enter a string", file=sys.stderr)
        #     return
        
        # initialize parent class
        super().__init__(config, test_name, tensor_accesses)
        
        # read all lines in given file up to MAX_LINES
        # all_lines = r_file_ptr.readlines(MAX_LINES)
        # r_file_ptr.close()
        
        # initialize file writer to interact with actual manipulation of lines
        self.file_writer = Modify_Lines(filename)
        
        # set replacement point at start of test case
        self.match_test_case()
        
        # if schedule has some unfused component, add additional lines
        if self.unfused == False:
            # set replacement point to declaration of last tensor (Tensor<double> ...)
            self.match_decls()
            
            # add all declarations
            self.add_declarations()
        
            # match original expression statement (A(i,l) = ...)
            self.match_expr_stmt()
            
            # remove this
            self.file_writer.remove_line()
            
            # add in new expression statements
            self.add_expr_statements()
            
            # match statmement declaration (IndexStmt stmt = ...)
            self.match_stmt_decl()
            
            # add all new statement declarations
            self.add_stmt_decls()
            
            # replace scheduling directive text in between headers with new schedule
            self.replace_schedule()
            
            # match stmt concretize statement (stmt = stmt.concretize();)
            self.match_stmt_concr()
            
            # add stmt concretize statements
            self.add_stmt_concr()
            
            # match compile statement (A.compile(stmt);)
            self.match_compile()
            
            # add compilation statements
            self.add_compile_stmts()
            
            # match assemble statement (A.assemble())
            self.match_assemble()
            
            # add assemble statements
            self.add_assemble()
            
            # modify for loop based on number of tests
            self.modify_for_loop()
            
            # match compute statement
            self.match_compute()
            
            # move back by one to put previous computations first
            self.file_writer.move_replace_point(-1)
            
            # add compute statements
            self.add_compute()
            
        else:
            # replace scheduling directive text in between headers with new schedule
            self.replace_schedule()
            
            # modify for loop based on number of tests
            self.modify_for_loop()
        
        
        
        print("hi")
        # write new compiled info back to file
        # w_file_ptr = open(filename, "w")
        # w_file_ptr.writelines(new_text)
        # w_file_ptr.close()
        
    def revert_file(self):
        self.file_writer.revert_file()
    
    def match_test_case(self):
        """Sets replacement/addition point to the actual test case
        """
        self.file_writer.match_replacement_point(f"TEST\(workspaces, {self.test_name}\)")
    
    def match_decls(self):
        """Sets replacement/addition point to the last tensor in the given computation
        """
        for _ in range(len(self.orig_config.expr) + 1):
            if self.file_writer.match_replacement_point(r'Tensor<double> ' r'.+;', no_move=True, include_line=False):
                self.file_writer.match_replacement_point(r'Tensor<double> ' + r'.+;', include_line=False)
            else:
                return
    
    def match_expr_stmt(self):
        """Sets replacement/addition point to the base expression statement
        """
        orig_output = self.orig_config.output
        self.file_writer.match_replacement_point(f'{orig_output}\({",".join(self.tensor_accesses[orig_output])}\).+;')
        
    def match_stmt_decl(self):
        """Sets replacement/addition point to the base IndexStmt stmt
        """
        orig_output = self.orig_config.output
        self.file_writer.match_replacement_point(f'IndexStmt stmt = {orig_output}\.getAssignment\(\)\.concretize\(\);')
        
    def match_stmt_concr(self):
        """Sets replacement/addition point to the concretization statement
        """
        self.file_writer.match_replacement_point("stmt = stmt\.concretize\(\);")
        
    def match_compile(self):
        """Sets replacement/addition point to the compile statement
        """
        orig_output = self.orig_config.output
        self.file_writer.match_replacement_point(f'{orig_output}\.compile\(stmt\);')
    
    def match_assemble(self):
        """Sets replacement/addition point to the assemble statement
        """
        orig_output = self.orig_config.output
        self.file_writer.match_replacement_point(f'{orig_output}\.assemble\(\);')
        
    def match_compute(self):
        """Sets replacement/addition point to the compute statement
        """
        orig_output = self.orig_config.output
        self.file_writer.match_replacement_point(f'{orig_output}\.compute\(stmt\);')
        
    def replace_schedule(self):
        """Replaces given schedule using stmt's
        """
        lines = [statement["lines"]["sched_change"] for statement in self.statements if len(statement["lines"]["sched_change"]) != 0]
        lines = [decl for line in lines for decl in line]
        self.file_writer.replace_between_headers(header_to_read, footer_to_read, lines)
        
    def modify_for_loop(self):
        """Modifies for loop to account for proper number of tests
        """
        self.file_writer.modify_line(test_rep_for_loop, r'\g<1>' + str(self.num_tests) + r'\g<4>')
        
    def add_declarations(self):
        """Adds given tensor declarations at replacement/addition point
        """
        decls = [statement["lines"]["tens_decl"] for statement in self.statements if len(statement["lines"]["tens_decl"]) != 0]
        self.file_writer.add_lines(decls)
        
    def add_expr_statements(self):
        """Adds expression statements at replacement/addition point
        """
        exprs = [statement["lines"]["expr_decl"] for statement in self.statements if len(statement["lines"]["expr_decl"]) != 0]
        self.file_writer.add_lines(exprs)
        
    def add_stmt_decls(self):
        """Adds statement declarations at replacement/addition point
        """
        stmts = [statement["lines"]["stmt_decl"] for statement in self.statements if len(statement["lines"]["stmt_decl"]) != 0]
        self.file_writer.add_lines(stmts)
        
    def add_stmt_concr(self):
        """Adds concretization statements at replacement/addition point
        """
        stmts = [statement["lines"]["concretize"] for statement in self.statements if len(statement["lines"]["concretize"]) != 0]
        self.file_writer.add_lines(stmts)
        
    def add_compile_stmts(self):
        """Adds compile statements at replacement/addition point
        """
        stmts = [statement["lines"]["compile"] for statement in self.statements if len(statement["lines"]["compile"]) != 0]
        self.file_writer.add_lines(stmts)
        
    def add_assemble(self):
        """Adds assemble statements at replacement/addition point
        """
        stmts = [statement["lines"]["assemble"] for statement in self.statements if len(statement["lines"]["assemble"]) != 0]
        self.file_writer.add_lines(stmts)
        
    def add_compute(self):
        """Adds compute statements at replacement/addition point
        """
        stmts = [statement["lines"]["compute"] for statement in self.statements if len(statement["lines"]["compute"]) != 0]
        self.file_writer.add_lines(stmts)
    
    def print_data(self, data: str, num_tabs=1) -> None:
        """Override print_data to write all info into list

        Args:
            data (str): data to append to list
        """
        self.schedule_text.append("\t" * num_tabs + data + "\n")
    
    def __get_indices(self, config:Config):
        """Retrieves the indices accessed by a given expression

        Args:
            config (Config): schedule given
        """
        
        if config.original_idx_perm == None:
            return self.__get_indices(config.prod) + self.__get_indices(config.cons)
        return config.original_idx_perm  
    
    def get_temporaries(self, sched:Config):
        if sched.prod == None: return []
        
        temps = []
        if sched.fused == 0: 
            # shared_indices = list(set(self.__get_indices(sched.prod)).intersection(set(self.__get_indices(sched.cons))))
            # root_indices = self.__get_indices(sched)
            # shared_index_locations = [root_indices.index(shared_index) for shared_index in shared_indices]
            # index_order = [index for _, index in sorted(zip(shared_index_locations, shared_indices))]
            temporaries = list(sched.temporary.values())
            index_order_prod = temporaries[0]
            # [idx for idx in self.config.original_idx_perm if idx in sched.prod.input_idx_order]
            
            index_order_cons = temporaries[1]
            # [idx for idx in self.config.original_idx_perm if idx in sched.cons.input_idx_order]
            
            temps.append({"index_order_prod": index_order_prod, 
                          "index_order_cons": index_order_cons, 
                          "output_temp_name_prod": sched.prod.output,
                          "output_temp_name_cons": sched.cons.output,
                          "config": sched})
        
        temps.extend(self.get_temporaries(sched.prod))
        temps.extend(self.get_temporaries(sched.cons))
        
        return temps
    
    
if __name__ == "__main__":
    schedules = []
    accesses = {
        'A': ('i', 'l'),
        'B': ('i', 'j'),
        'C': ('i', 'k'),
        'D': ('j', 'k'),
        'E': ('j', 'l')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i')],
        # 'B': [],
        # 'C': [],
        # 'D': [],
    }
    # sched_enum('X', ['A','B','C','D'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)
    cache = {}
    schedules = list(get_schedules_unfused('A', accesses['A'], ('B','C','D', 'E'), accesses, ('i', 'j', 'k', 'l'), tensor_idx_order_constraints, 1, cache))
    print("\n")
    counter_printing = 15
    counter = 1
    test_num = 1
    
    # test_sched = Config('X', ('A', 'B', 'C', 'D'), ('i', 'j', 'k', 'l', 'm'), ('i', 'j', 'l', 'k', 'm'), 2)
    # test_sched.original_idx_perm = ('i', 'j', 'l', 'k', 'm')
    for schedule in schedules:
        # if count_fusions(schedule) == 2 and schedule.fused:
            if schedule.fused == 0 and schedule.cons != None and schedule.cons.fused == 0:
                Write_Test_Code(schedule, "sddmm_spmm_fake", "/home/shay/a/anderslt/tensor-schedules/src/tests-workspaces.cpp", 10, accesses)
                break
              
            counter = (counter % counter_printing) + 1
            # if counter == counter_printing:
                # Gen_Test_Code(schedule, "Test " + str(test_num), sys.stdout)
            test_num += 1
            # break
            # break
          

          
          
# [x] path is wrong when printing