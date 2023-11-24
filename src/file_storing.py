from src.config import Config
from src.visitor import PrintDictVisitor, WriteBasketsVisitor
import sys
import json
from src.basket import Baskets

def store_json(tensor_accesses:dict, config_list:list, filename:str):
    assert len(config_list) > 0
    # assert type(config_list[0]) == Config
    
    printer = PrintDictVisitor(tensor_accesses)
    
    for i, config in enumerate(config_list):
        # for config in group:
        #     config.group = i
        config.accept(printer)

        
    printer.output_to_file(filename)
    
def store_baskets_to_json(tensor_accesses:dict, baskets:Baskets, filename:str):
    assert len(baskets) > 0
    assert type(baskets) == Baskets
    assert type(baskets[0][2][0]) == Config
    
    printer = WriteBasketsVisitor(tensor_accesses, baskets)
    
    for i, basket in enumerate(baskets.get_baskets()):
        for config in basket[2]:
            config.acceptn(printer, i)
        
    printer.output_to_file(filename)
    
def lists_to_tuples(in_list:list):
    out_list = []
    for item in in_list:
        if type(item) != list: out_list.append(item)
        else: out_list.append(lists_to_tuples(item))
    return tuple(out_list)
    
def get_config(schedule: dict) -> Config:
    new_config = Config(
      output=schedule["output_tensor"],
      expr=lists_to_tuples(schedule["input_tensors"]),
      output_idx_order=lists_to_tuples(schedule["output_idx_order"]),
      input_idx_order=lists_to_tuples(schedule["input_idx_order"]),
      fused=schedule["fused"],
      prod_on_left=schedule["prod_on_left"]
    )
    
    new_config.time_complexity = schedule["time_complexity"]
    new_config.memory_complexity = [tuple(lst) for lst in schedule["memory_complexity"]]
    new_config.original_idx_perm = schedule["original_idx_perm"]
    new_config.temporary = schedule["temporary"]
    new_config.cache_complexity = schedule["cache_complexity"] if "cache_complexity" in schedule else []
    # new_config.group = schedule["group"]
    
    if schedule["producer"]: 
        new_config.prod = get_config(schedule["producer"])
    else:
        new_config.prod = None
    if schedule["consumer"]: 
        new_config.cons = get_config(schedule["consumer"])
    else:
        new_config.cons = None
    
    return new_config

def read_json(filename:str, with_accesses = False) -> list:
    try:
        fileptr = open(filename, "r")
    except OSError:
        print("Invalid JSON file for reading", file=sys.stderr)
        return []

    new_dict = json.load(fileptr)
    fileptr.close()
    
    # for key, value in new_dict["idx_order_constraints"].items():
    #     new_dict["idx_order_constraints"][key] = [tuple(lst) for lst in value]
    
    config_list = []
    
    for schedule in new_dict["schedules"]:
        config_list.append(get_config(schedule))
    
    # printer = PrintConfigVisitor(new_dict["accesses"])    
    # for config in config_list:
    #     config.accept(printer)
    
    if (with_accesses):
        return config_list, new_dict["accesses"]
    
    return config_list


def read_baskets_from_json(filename:str) -> list:
    try:
        fileptr = open(filename, "r")
    except OSError:
        print("Invalid JSON file for reading. filename: ", filename, file=sys.stderr)
        return []

    new_dict = json.load(fileptr)
    fileptr.close()
    
    # for key, value in new_dict["idx_order_constraints"].items():
    #     new_dict["idx_order_constraints"][key] = [tuple(lst) for lst in value]
    
    baskets = []
    
    for i, basket in enumerate(new_dict["baskets"]):
        config_list = []
        for schedule in basket["schedules"]:
            config_list.append(get_config(schedule))
        baskets.append((basket["tc"], basket["mc"], config_list))
    
    # printer = PrintConfigVisitor(new_dict["accesses"])    
    # for config in config_list:
    #     config.accept(printer)
    
    return Baskets(baskets), new_dict["accesses"]