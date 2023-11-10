from src.config import Config
from src.visitor import PrintDictVisitor, WriteBasketsVisitor
import sys
import json
from src.basket import Baskets
import re
import numpy as np

MAX_LINES = 100000

class Modify_Lines:
    # def __init__(self, file_name):
    #     try:
    #         fileptr = open(file_name, "r")
    #     except OSError:
    #         print("Invalid JSON file for reading", file=sys.stderr)
    #         return

    #     self.lines = fileptr.readlines(MAX_LINES)
    #     fileptr.close()
    
    def __init__(self, lines):
        self.lines = lines
        self.replace_point = 0    # represents location in lines array to begin searching for replacement
    
    @property
    def num_lines(self):
        return len(self.lines)
    
    @property
    def lines_subset(self):
        """Lines within self.lines that follow and include the replacement point (same length as index_subset)
        """
        return self.lines[self.replace_point:]
    
    @property
    def add_loc(self):
        """Location to add new line
        """
        if self.replace_point != self.num_lines: return self.replace_point + 1
        else: return self.replace_point
    
    @property
    def index_subset(self):
        return np.arange(self.replace_point, self.num_lines)
      
    @property
    def given_line(self):
        return self.lines[self.replace_point]
    
    def replace_between_headers(self, header, footer, replacement_text, move_replacement_point=False, include_headers=False):
        """Replaces text in between a header and a footer line

        Args:
            header (str): header to match
            footer (str): footer to match
            replacement_text (str|list): text to replace in between headers
            move_replacement_point (bool, optional): whether to move replacement location after. Defaults to False.
            include_headers (bool, optional): whether to include headers when replacing. Defaults to False.

        Returns:
            bool: returns if replacement is successful
        """
        
        # assert type(header_matched) == str or type(header_matched) == re.Pattern
        assert type(replacement_text) == str or type(replacement_text) == list
        if type(replacement_text) == str: replacement_text = [replacement_text]
        
        start_index = self.replace_point
        end_index = self.num_lines
        
        header_matched = False
        footer_matched = False
        for line, location in zip(self.lines_subset, self.index_subset):
            if re.search(header, line) and not header_matched:
                start_index = location
                header_matched = True
            
            elif re.search(footer, line) and header_matched:
                end_index = location
                footer_matched = True
                break
        
        if header_matched == False or footer_matched == False: return False
        if include_headers == True:
            start_index -= 1
            end_index += 1
            
        if move_replacement_point: self.move_replace_point(-self.replace_point + len(replacement_text) + start_index + 1)
        
            
        
        self.lines = self.lines[:start_index + 1] + replacement_text + self.lines[end_index:]
        return True
                

    def match_replacement_point(self, replace_point_pat, from_beginning=True):
        """Sets the line to begin searching for future replacements

        Args:
            replace_point_pat (str|re.Pattern): pattern that matches desired line
            from_beginning (bool): match replace point from beginning of lines array or from current replace point
        """
        # assert type(replace_point_pat) == str or type(replace_point_pat) == re.Pattern
        if type(replace_point_pat): replace_point_pat = re.compile(replace_point_pat)
        if from_beginning: 
            lines = self.lines
            indices = list(range(self.num_lines))
        else: 
            lines = self.lines_subset
            indices = self.index_subset
        
        for i, line in zip(indices, lines):
            if replace_point_pat.search(line):
            # re.search(replace_point_pat, line):
                self.replace_point = i
                return True
        return False
    
    def modify_line(self, line_pattern, replacement, move_replacement_point=False):
        for i, line in zip(self.index_subset, self.lines_subset):
            if re.search(line_pattern, line):
                self.lines[i] = re.sub(line_pattern, replacement, line)
                if move_replacement_point and self.num_lines != self.replace_point + 1: self.move_replace_point(1)
                return True
        
        return False
      
    def modify_lines(self, list_line_mods):
        """Modifies multiple lines sequentially

        Args:
            list_modifications (list[tuple]): list of (pattern, replacement) pairs
        
        Returns:
            True | list[tuple]: if all modifications are valid, returns true, else it returns the list of invalid modifications
        """
        invalid_lines = []
        for pair in list_line_mods:
            assert len(pair) == 2
            valid_line_mod = self.modify_line(list_line_mods[0], list_line_mods[1])
            if not valid_line_mod: invalid_lines.append(pair)
        if len(invalid_lines) == 0: return True
        else: return invalid_lines

    def move_replace_point(self, offset):
        """Moves replacement point by the specified offset

        Args:
            offset (int): offset lines
        """
        new_replace_point = self.replace_point + offset
        if new_replace_point < 0 or new_replace_point >= self.num_lines: return False
        
        self.replace_point = new_replace_point
        return True
    
    def add_line(self, line):
        """Adds a line at location after specified replacement point and moves replacement point up to this line

        Args:
            line (str): line to add
        """
        self.lines.insert(self.add_loc, line)
        return self.move_replace_point(1)
        
    def add_lines(self, lines):
        success = True
        for line in lines:
            success &= self.add_line(line)
    
    def remove_line(self, match=None):
        """Removes line at specified replacement point if match is found (or regardless if match is None)
        """
        # assert match == None or type(match) == str or type(match) == re.Pattern
        if match != None and not re.search(match, self.given_line):
            return False
        
        del self.lines[self.match_replacement_point]
        if self.match_replacement_point == self.num_lines: self.move_replace_point(-1)
        return True

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

def read_json(filename:str) -> list:
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