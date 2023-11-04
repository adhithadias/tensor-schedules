from src.config import Config
import json
from copy import deepcopy
from src.util import Baskets

class Visitor:
    def __str__(self):
        return self.__class__.__name__


class PrintConfigVisitor(Visitor):
    def __init__(self, tensor_accesses: dict):
        self.tabs = 0
        self.tensor_accesses = tensor_accesses

    def visit(self, config):
        output = config.output + "(" + ','.join(config.output_idx_order) + ")"

        tensor_contraction = ""
        for i in range(len(config.expr)):
            tensor = config.expr[i]
            if tensor in self.tensor_accesses:
                tensor_contraction += tensor + "(" + ','.join(self.tensor_accesses[tensor]) + ")"
            else:
                tensor_contraction += tensor + "()"
            if (i != len(config.expr)-1):
                tensor_contraction += "*"

        print('\t'*self.tabs, '|', 
            output, '=',
            tensor_contraction, 
            ', fsd: ' + str(config.fused) + ", pol: " + str(config.prod_on_left),
            '| lp_ord:', config.input_idx_order, '|', config.time_complexity, ',', config.memory_complexity, flush = True)
        self.tabs += 1
        if (config.prod != None):
            self.visit(config.prod)
        if (config.cons != None):
            self.visit(config.cons)
        self.tabs -= 1

class PrintDictVisitor(Visitor):
    def __init__(self, tensor_accesses: dict):
        # self.tensor_accesses = tensor_accesses
        # temp_constraints = deepcopy(idx_order_constraints)
        
        # for key, value in temp_constraints.items():
        #     temp_constraints[key] = [list(tup) for tup in value]
        
        self.dict = {
            "schedules": [],
            "accesses": tensor_accesses,
            # "idx_order_constraints": temp_constraints
        }

    def get_dict(self, config:Config) -> dict:
        if config.prod == None: prod = None
        else: prod = self.get_dict(config.prod)
        if config.cons == None: cons = None
        else: cons = self.get_dict(config.cons)
        
        new_config_dict = {
            "output_tensor": config.output,
            "input_tensors": config.expr,
            "prod_on_left" : config.prod_on_left,
            "fused": config.fused,
            "input_idx_order": config.input_idx_order,
            "output_idx_order": config.output_idx_order,
            "producer": prod,
            "consumer": cons,
            "time_complexity": config.time_complexity,
            "memory_complexity": [list(tup) for tup in config.memory_complexity],
            "original_idx_perm": config.original_idx_perm,
            # "group": config.group
        }
        return new_config_dict
        
    def visit(self, config:Config):
        new_config_dict = self.get_dict(config)
        self.dict["schedules"].append(new_config_dict)
    
    def output_to_file(self, filename:str):
        fileptr = open(filename, "w")
        fileptr.write(json.dumps(self.dict, indent=2, separators=(',', ': '), sort_keys=False))
        fileptr.close()


class WriteBasketsVisitor(Visitor):
    def __init__(self, tensor_accesses: dict, baskets: Baskets):
        # self.tensor_accesses = tensor_accesses
        # temp_constraints = deepcopy(idx_order_constraints)
        
        # for key, value in temp_constraints.items():
        #     temp_constraints[key] = [list(tup) for tup in value]
        
        self.dict = {
            "baskets": [{"tc": tc, "mc": [list(tup) for tup in mc], "schedules": []} for tc, mc, _ in baskets],
            "accesses": tensor_accesses,
            # "idx_order_constraints": temp_constraints
        }

    def get_dict(self, config:Config) -> dict:
        if config.prod == None: prod = None
        else: prod = self.get_dict(config.prod)
        if config.cons == None: cons = None
        else: cons = self.get_dict(config.cons)
        
        new_config_dict = {
            "output_tensor": config.output,
            "input_tensors": config.expr,
            "prod_on_left" : config.prod_on_left,
            "fused": config.fused,
            "input_idx_order": config.input_idx_order,
            "output_idx_order": config.output_idx_order,
            "producer": prod,
            "consumer": cons,
            "time_complexity": config.time_complexity,
            "memory_complexity": [list(tup) for tup in config.memory_complexity],
            "original_idx_perm": config.original_idx_perm,
            "cache_expr": config.cache_expr
        }
        return new_config_dict
        
    def visit(self, config: Config, basket: int):
        new_config_dict = self.get_dict(config)
        self.dict["baskets"][basket]["schedules"].append(new_config_dict)
    
    def output_to_file(self, filename:str):
        fileptr = open(filename, "w")
        fileptr.write(json.dumps(self.dict, indent=2, separators=(',', ': '), sort_keys=False))
        fileptr.close()

# class GetComplexityVisitor(Visitor):
#     def __init__(self, tensor_accesses: dict) -> None:
#         self.tensor_accesses = tensor_accesses

#     def retrieve_time_complexity(self, schedule=[]) -> str:
#         complexity = ""
#         if len(schedule) > 0 and type(schedule[-1]) == list:
#             producer = self.retrieve_time_complexity(schedule[-2])
#             consumer = self.retrieve_time_complexity(schedule[-1])
#             if len(schedule[0:-2]) > 0:
#                 complexity += "*".join(schedule[0:-2]) + "*"
#             if len(producer) > 0 and len(consumer) > 0:
#                 complexity += "(" + producer + "+" + consumer + ")"
#                 return complexity
#             elif len(producer) > 0:
#                 return complexity + "(" + producer + ")"
#             elif len(consumer) > 0:
#                 return complexity + "(" + consumer + ")"
#             else:
#                 # return "*".join(schedule[0:-2])
#                 return ""
#         elif len(schedule) <= 0:
#             return ""
#         else:
#             return "*".join(schedule)

#     # retrieve complexity of a given tensor schedule
#     # def retrieve_complexity(schedule: Config) -> str:
#     #     complexity = ""
#     #     # check if fused loop
#     #     if len(schedule.input_idx_order) > 0 and type(schedule.input_idx_order[-1]) == list:
#     #         producer = retrieve_fused_complexity(schedule.input_idx_order[-2])
#     #         consumer = retrieve_fused_complexity(schedule.input_idx_order[-1])
#     #         if len(schedule.input_idx_order[0:-2]) > 0:
#     #             complexity += "*".join(schedule.input_idx_order[0:-2]) + "*"
#     #         if len(producer) > 0 and len(consumer) > 0:
#     #             complexity += "(" + producer + "+" + consumer + ")"
#     #             return complexity
#     #         elif len(producer) > 0:
#     #             return complexity + "(" + producer + ")"
#     #         elif len(consumer) > 0:
#     #             return complexity + "(" + consumer + ")"
#     #         else:
#     #             # return "*".join(schedule.input_idx_order[0:-2])
#     #             return ""
#     #     elif len(schedule.input_idx_order) <= 0:
#     #         return ""
#     #     else:
#     #         return "*".join(schedule.input_idx_order)
    
#     def retrieve_space_complexity(self, config:Config) -> str:
#         complexity = ""
        

    # def visit(self, config: Config):
    #     config.set_time_complexity(self.retrieve_time_complexity(config))
    #     config.set_space_complexity(self.retrieve_space_complexity(config))
