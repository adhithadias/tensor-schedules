from src.config import Config
from src.autosched import sched_enum
from random import randint
from z3 import *
from src.visitor import PrintConfigVisitor
from bitarray import bitarray
import json
import re

min_dense = 10
max_dense = 1000
min_sparse = 0
max_sparse = 500
count = {
    "unsat,unsat": 0,
    "unsat,sat": 0,
    "sat,unsat": 0,
    "sat,sat": 0
}

max_capture_expr_len = 5

z3_num = "(?:0\\.[0-9]+)|(?:[1-9]+[0-9]*(?:(?:\\.[0-9]+)?))|(?:0)"
z3_var = "(?:[a-zA-Z_][a-zA-Z_0-9]*)"
extra_expr1 = "".join(
    [f'\\s*(?:(?P<op{num}_expr1>[\\*/\\+-])\\s*(?P<var_num{num+1}_expr1>{z3_var}|{z3_num})\\s*)?' for num in range(max_capture_expr_len)])
extra_expr2 = "".join(
    [f'\\s*(?:(?P<op{num}_expr2>[\\*/\\+-])\\s*(?P<var_num{num+1}_expr2>{z3_var}|{z3_num})\\s*)?' for num in range(max_capture_expr_len)])
z3_expr1 = f'(?P<var_num0_expr1>{z3_var}|{z3_num})' + extra_expr1
z3_expr2 = f'(?P<var_num0_expr2>{z3_var}|{z3_num})' + extra_expr2

constraint_types = {
    ">": f'((?:{z3_expr1})\\s*\\>\\s*(?:{z3_expr2}))',
    ">=": f'((?:{z3_expr1})\\s*\\>=\\s*(?:{z3_expr2}))',
    "<": f'((?:{z3_expr1})\\s*\\<\\s*(?:{z3_expr2}))',
    "<=": f'((?:{z3_expr1})\\s*\\<=\\s*(?:{z3_expr2}))'
}
          
        

class Solver_Config:
    def __init__(self, tensor_accesses: dict, tensor_idx_order_constraints: dict, z3_constraints: None) -> None:
        """Generates a solver configuration

        Args:
            tensor_accesses (dict): tensor and their corresponding indices
            tensor_idx_order_constraints (dict): index order constraints to establish sparsity
            z3_constraints (list[str]): optional z3 constraints. Must be a list. Defaults to None.
        """
        
        constraints = []
        # [x] change to account for sparse tensors
        self.solver = Solver()

        # list of all indices separated by dense/sparse
        self.total_indices = {
            "dense": {},
            "sparse": {},
            "all": {}
        }
    
        # get dense set of indices
        dense_set = set(index for indexes in tensor_accesses.values()
                        for index in indexes)

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
        
        # initializes all indices together
        self.total_indices["all"] = {
            **self.total_indices["dense"], **self.total_indices["sparse"]}
    
        if z3_constraints != None:
            # adds minimum and maximum constraints for dense
            for index in self.total_indices["dense"].values():
                # print(index > min_dense)
                self.solver.add(index > min_dense, index < max_dense)

            # adds minimum and maximum constraints for sparse
            for index in self.total_indices["sparse"].values():
                self.solver.add(index > min_sparse, index < max_sparse)

            # add sparse constraints
            for key in self.total_indices["sparse"].keys():
                self.solver.add(
                    self.total_indices["sparse"][key] < self.total_indices["dense"][key[0:-3]])
        else:
            z3_constraints = self.parse_z3_constraints(z3_constraints)
            self.solver.add(z3_constraints)

        # saves solver backtracking point
        self.solver.push()

    def parse_z3_constraints(self, constraint_list: list):
      z3_constraints = []
      for constraint in constraint_list:
        for constraint_type, reg_exp in constraint_types.items():
          if re.fullmatch(reg_exp, constraint):
            expr_dict = re.fullmatch(reg_exp, constraint).groupdict()
            excess_terms = []
            for key, value in expr_dict.items():
              if value == None:
                excess_terms.append(key)
            for term in excess_terms:
              del expr_dict[term]
            left_expr = [value for key,value in expr_dict.items() if key[-1] == '1']
            right_expr = [value for key,value in expr_dict.items() if key[-1] == '2']
            left_z3_expr = self.get_single_side_z3_expr(left_expr)
            right_z3_expr = self.get_single_side_z3_expr(right_expr)
            
            if constraint_type == '>':
                full_z3_expr = left_z3_expr > right_z3_expr
            elif constraint_type == '>=':
                full_z3_expr = left_z3_expr >= right_z3_expr
            elif constraint_type == '<':
                full_z3_expr = left_z3_expr < right_z3_expr
            elif constraint_type == '<=':
                full_z3_expr = left_z3_expr <= right_z3_expr
            
            z3_constraints.append(full_z3_expr)
      return z3_constraints

    def __get_float_int(self, num):
        try:
            return int(num)
        except:
            return float(num)

# TODO make this better with order of operations
    def get_single_side_z3_expr(self, expr):
        z3_expr = None
        if expr[0] in self.total_indices["all"].keys(): z3_expr = self.total_indices["all"][expr[0]]
        else: 
            z3_expr = self.__get_float_int(expr[0])
        for index in range(1, len(expr), 2):
            temp_z3_expr = None
            if expr[index + 1] in self.total_indices["all"].keys():
                temp_z3_expr = self.total_indices["all"][expr[index + 1]]
            else:
                temp_z3_expr = self.__get_float_int(expr[index + 1])

            if expr[index] == '*':
                z3_expr = z3_expr * temp_z3_expr
            elif expr[index] == '+':
                z3_expr = z3_expr + temp_z3_expr
            elif expr[index] == '-':
                z3_expr = z3_expr-+ temp_z3_expr
            elif expr[index] == '/':
                z3_expr = z3_expr / temp_z3_expr
        return z3_expr
    
    def get_z3_expr(self, complexity: list):
        add_expr = None
        for expr in complexity:
            if(type(expr) != set and type(expr) != list):
                return None
            mult_expr = None
            for index in expr:
            
                if(mult_expr == None):
                    mult_expr = self.total_indices["all"][index]
                else:
                    mult_expr = mult_expr * self.total_indices["all"][index]
            if mult_expr == None: continue
            elif add_expr == None: add_expr = mult_expr
            else: add_expr = add_expr + mult_expr
        return add_expr

    def compare_schedules(self, config_1: Config, config_2: Config) -> int:
        # get complexities if not already gotten for given config
        if(config_1.z3_time_complexity == None):
            time_complexity_1 = self.get_z3_expr(config_1.time_complexity['r'])
            time_complexity_2 = self.get_z3_expr(config_1.time_complexity['a'])
            if(time_complexity_1 != None and time_complexity_2 != None):
                config_1.z3_time_complexity = time_complexity_1 + time_complexity_2
            elif time_complexity_1 != None:
                config_1.z3_time_complexity = time_complexity_1
            elif time_complexity_2 != None:
                config_1.z3_time_complexity = time_complexity_2
            else:
                config_1.z3_time_complexity = 0
        if(config_2.z3_time_complexity == None):
            time_complexity_1 = self.get_z3_expr(config_2.time_complexity['r'])
            time_complexity_2 = self.get_z3_expr(config_2.time_complexity['a'])
            if(time_complexity_1 != None and time_complexity_2 != None):
                config_2.z3_time_complexity = time_complexity_1 + time_complexity_2
            elif time_complexity_1 != None:
                config_2.z3_time_complexity = time_complexity_1
            elif time_complexity_2 != None:
                config_2.z3_time_complexity = time_complexity_2
            else:
                config_2.z3_time_complexity = 0
        if(config_1.z3_memory_complexity == None):
            memory_complexity = self.get_z3_expr(config_1.memory_complexity)
            if(memory_complexity != None):
                config_1.z3_memory_complexity = memory_complexity
            else:
                config_1.z3_memory_complexity = 0
                
        if(config_2.z3_memory_complexity == None):
            memory_complexity = self.get_z3_expr(config_2.memory_complexity)
            if(memory_complexity != None):
                config_2.z3_memory_complexity = memory_complexity
            else:
                config_2.z3_memory_complexity = 0

        # # check if config 1 time complexity better than config 2
        # self.solver.add(config_1.z3_time_complexity >=
        #                 config_2.z3_time_complexity)
        # condition1 = self.solver.check()
        # self.solver.pop()
        # self.solver.push()

        # # check if config 2 time complexity better than config 1
        # self.solver.add(config_1.z3_time_complexity <
        #                 config_2.z3_time_complexity)
        # condition2 = self.solver.check()
        # self.solver.pop()
        # self.solver.push()

        # if condition1 == unsat and condition2 == sat:
        #     count['unsat,sat'] += 1
        # elif condition1 == sat and condition2 == unsat:
        #     count['sat,unsat'] += 1
        # else:
        #     count['sat,sat'] += 1

        c1 = config_1.z3_time_complexity >= config_2.z3_time_complexity
        c2 = config_1.z3_memory_complexity > config_2.z3_memory_complexity
        c3 = config_1.z3_time_complexity > config_2.z3_time_complexity
        c4 = config_1.z3_memory_complexity >= config_2.z3_memory_complexity

        # check if config 1 memory complexity better than config 2
        # self.solver.add(config_1.z3_memory_complexity >= config_2.z3_memory_complexity)
        # condition1 = self.solver.check()
        # self.solver.pop()
        self.solver.add(Or(And(c1, c2), And(c3, c4)))
        condition = self.solver.check()
        self.solver.pop()
        self.solver.push()
        
        self.solver.push()
        self.solver.add(Or(And(Not(c1), Not(c2)), And(Not(c3), Not(c4))))
        inverse_condition = self.solver.check()  # this should be unsat to remove s1
        self.solver.pop()

        # check if config 2 memory complexity better than config 1
        # self.solver.add(config_1.z3_memory_complexity <
        #                 config_2.z3_memory_complexity)
        # condition2 = self.solver.check()
        # self.solver.pop()
        self.solver.push()
        # if condition1 == unsat and condition2 == sat:
        #     count['unsat,sat'] += 1
        # elif condition1 == sat and condition2 == unsat:
        #     count['sat,unsat'] += 1
        # else:
        #     count['sat,sat'] += 1
        
        # if condition is sat and inverse_condition is unsat, it means that s1 is worse than s2, we can remove s1
        if condition == sat and inverse_condition == unsat:
            return 1
        # if condition is unsat and inverse_condition is sat, it means that s2 is worse than s1, we can remove s2
        elif condition == unsat and inverse_condition == sat:
            return -1
        else:
            return 0

    def get_loop_depth(self, schedule: Config) -> int:
        assert type(schedule.time_complexity['r']) == list
        assert type(schedule.time_complexity['a']) == list
        max_: int = 0
        for complexity in schedule.time_complexity['r']:
            if (len(complexity) > max_):
                max_ = len(complexity)

        for complexity in schedule.time_complexity['a']:
            if (len(complexity) > max_):
                max_ = len(complexity)

        return max_


    def get_memory_depth(self, schedule: Config) -> int:
        assert type(schedule.memory_complexity) == list
        max_: int = 0
        for complexity in schedule.memory_complexity:
            if (len(complexity) > max_):
                max_ = len(complexity)

        return max_
          
    def prune_using_depth(self, schedules: list) -> list:
        results = []
        complexities = set()
        pruned_array = bitarray(len(schedules))
        pruned_array.setall(0)

        for i,s1 in enumerate(schedules):
            if (pruned_array[i]):
                continue

            s1_time_depth = self.get_loop_depth(s1)
            s1_memory_depth = self.get_memory_depth(s1)

            # we have seen the same complexities before
            if (s1_time_depth, s1_memory_depth) in complexities:
                results.append(s1)
                continue

            for j, s2 in enumerate(schedules):
                if (pruned_array[j]):
                    continue
                s2_time_depth = self.get_loop_depth(s2)
                s2_memory_depth = self.get_memory_depth(s2)

                # s2 schedule is better than s1 schedule, we can prune s1 schedule
                if ((s1_time_depth >= s2_time_depth and s1_memory_depth > s2_memory_depth)
                    or (s1_time_depth > s2_time_depth and s1_memory_depth >= s2_memory_depth)):
                    pruned_array[i] = True
                    break

                # s1 schedule is better than s2 schedule, we can prune s2 schedule
                if ((s1_time_depth <= s2_time_depth and s1_memory_depth < s2_memory_depth)
                    or (s1_time_depth < s2_time_depth and s1_memory_depth <= s2_memory_depth)):
                    pruned_array[j] = True
                    continue

            if (not pruned_array[i]):
                results.append(s1)
                complexities.add((s1_time_depth, s1_memory_depth))
        return results  
    
    def prune_using_memory_depth(self, schedules : set, memory_depth_thresh : int) -> list:
        n = len(schedules)
        print('pruning', n, 'schedules using memory depth', memory_depth_thresh, flush = True)
        results = []
        
        for i, s1 in enumerate(schedules):
            s1_memory_depth = self.get_memory_depth(s1)
            
            if (s1_memory_depth > memory_depth_thresh):
                continue
            
            results.append(s1)
            
        print('pruned', n - len(results), 'schedules', flush = True)
        return results
    
    def prune_schedules(self, schedule_list=list):
        result_array = []
        pruned_array = bitarray(len(schedule_list))
        pruned_array.setall(0)
        for i, s1 in enumerate(schedule_list):
            if pruned_array[i]:
                continue
            for j, s2 in enumerate(schedule_list):  #TODO check if can change schedules to schedules[i:]
                if (pruned_array[j]):
                    continue
                compar = self.compare_schedules(s1,s2)
                
                if compar == 1:
                    pruned_array[j] = True
                elif compar == -1:
                    pruned_array[i] = True
                    break
            if not pruned_array[i]:
                result_array.append(s1)
        return result_array

if __name__ == "__main__":
    schedules = []
    # accesses = {
    #     'X': ['i', 'm'],
    #     'A': ['i', 'j'],
    #     'B': ['j', 'k'],
    #     'C': ['k', 'l'],
    #     'D': ['l', 'm']
    # }
    # tensor_idx_order_constraints = {
    #     'A': [('j', 'i')],
    #     # 'B': [],
    #     # 'C': [],
    #     # 'D': [],
    # }
    # sched_enum('X', ['A','B','C'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)

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
    sched_enum('X', ['A', 'B', 'C', 'D'], accesses['X'],
              accesses, tensor_idx_order_constraints, schedules)

    solver = Solver_Config(accesses, tensor_idx_order_constraints)
    # print(solver.get_z3_expr([{'i', 'k', 'jpos'}, {'l', 'i', 'jpos'}]))

    schedules = solver.prune_using_depth(schedules)
    schedules = solver.prune_schedules(schedules)

    print('\n\n\n\n\n\n\n')
    print(len(schedules))

    print('\n\n\n\n\n\n\n')

    print('/**************************************************************************/')
    print('/********************** PRINTING SCHEDULES ********************************/')
    print('/**************************************************************************/')

    printer = PrintConfigVisitor(accesses)
    for schedule in schedules:
        schedule.accept(printer)
        print('-----------')

    # for sched in range(len(schedules) - 1):
        # solver.compare_schedules(schedules[randint(0, len(schedules) - 1)], schedules[randint(0, len(schedules) - 1)])
        # solver.compare_schedules(schedules[sched], schedules[sched + 1])
