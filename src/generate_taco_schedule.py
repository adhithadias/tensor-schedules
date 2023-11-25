from src.config import Config
from src.visitor import Visitor
import regex as re
from copy import deepcopy

class GenerateScheduleVisitor(Visitor):
    
    def __init__(self, tensor_accesses: dict):
        self.tabs = 0
        self.tensor_accesses = tensor_accesses
        self.transformed_schedule = []
        self.path = []
        self.paths = {}
        
    def visit(self, config):
        
        if (config == None):
            return
        
        path = "{" + ','.join(self.path) + "}"
        path_vector_name = 'path_' + ''.join(self.path)
        loop_order = "{" + ','.join(config.original_idx_perm) + "}"
        
        reorder = ".reorder(" + path_vector_name + ", " + loop_order + ")"
        
        if (len(config.original_idx_perm) > 1):
            if path not in self.paths: self.paths[path] = path_vector_name
            self.transformed_schedule.append(reorder)
        
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
            ', fsd: ' + str(config.fused) + 
            ", pol: " + str(config.prod_on_left) + 
            ", oip: " + str(config.original_idx_perm) + 
            ", expr: " + str(config.expr) +
            ", pol: " + str(config.prod_on_left) +
            ", temp: " + str(config.temporary),
            '| lp_ord:', config.input_idx_order, '|', config.time_complexity, ',', config.memory_complexity, flush = True)
        self.tabs += 1
        
        if (config.prod != None and config.cons != None):
            split_location = len(config.prod.expr)
            t = "true" if config.prod_on_left else "false"
            loopfuse = f'.loopfuse({str(split_location)}, {t}, {path_vector_name})'
            self.transformed_schedule.append(loopfuse)
            
            self.path.append("0")
            self.visit(config.prod)
            self.path.pop()
            self.path.append("1")
            self.visit(config.cons)
            self.path.pop()
        
        # if (config.prod != None):
        #     self.visit(config.prod)
        # if (config.cons != None):
        #     self.visit(config.cons)
        self.tabs -= 1
        
class UnfusedConfigToTacoVisitor(Visitor):
    def __init__(self, test_name: str, tensor_accesses: dict, original_index_order: list, test_file: str = None):
        self.test_name = test_name
        self.tensor_accesses = deepcopy(tensor_accesses)
        self.original_index_order = original_index_order
        self.test_file = test_file
        self.schedules = []
        self.paths = []
        self.expr_definitions = []
        self.outputs = []
        self.assignments = []
        
    def write_to_file(self, p: bool = False):
        assert self.test_file != None
        
        try:
            f = open(self.test_file, "r+")
        except OSError:
            print("Could not open/read file:", self.test_file, flush = True)
            return
        except TypeError:
            print("Could not open/read file:", self.test_file, flush = True)
            return
        
        text = self.wrap_in_block(self.get_combined_schedule())
        exec = self.wrap_in_execute_block(self.get_execute_commands())
        self.text = text
        self.exec = exec
        
        if (p):
            print(text)
            print(exec)
        
        file_contents = f.read()
        regex = r'/\* BEGIN ' + f'{self.test_name}' + r' TEST \*/[\s\S\n]+/\* END ' + f'{self.test_name}' + r' TEST \*/'
        match_regex = re.compile(regex)
        
        execute_regex = r'/\* BEGIN ' + f'{self.test_name}_execute' + r' TEST \*/[\s\S\n]+/\* END ' + f'{self.test_name}_execute' + r' TEST \*/'
        exec_match_regex = re.compile(execute_regex)
        
        # substitute text for match_regex in the file
        self.original_file_contents = file_contents
        file_contents = match_regex.sub(text, file_contents)
        file_contents = exec_match_regex.sub(exec, file_contents)
        
        f.seek(0)
        f.write(file_contents)
        f.truncate()
        f.close()
        
        
    def get_combined_schedule(self):
        result = ""
        
        # combine path maps
        path_map = {}
        for pm in self.paths:
            for key in pm:
                if (key not in path_map):
                    path_map[key] = pm[key]
                else:
                    assert path_map[key] == pm[key]
                    
        result += '\n' + self.get_vector_declaration(path_map) + '\n'
        
        for i in range(len(self.assignments) - 1):
            temporary_indices = self.tensor_accesses[self.outputs[i]]
            text = f'\tTensor<double> {self.outputs[i]}("{self.outputs[i]}", {{{", ".join([c.upper() for c in temporary_indices])}}}, Format{{{", ".join(["Dense" for _ in range(len(temporary_indices))])}}});\n'
            text += f'\t{self.assignments[i]};\n\tIndexStmt stmt_{self.outputs[i]} = {self.outputs[i]}.getAssignment().concretize();\n'
            
            text += f'\tstmt_{self.outputs[i]} = stmt_{self.outputs[i]}\n'
            text += ''.join(['\t\t' + s + '\n' for s in self.schedules[i]]) + '\t\t;\n'
            text += f'\tstmt_{self.outputs[i]} = stmt_{self.outputs[i]}.concretize();\n'
            text += f'\t{self.outputs[i]}.compile(stmt_{self.outputs[i]});\n'
            text += f'\t{self.outputs[i]}.assemble();\n\n'
            result += text
            
        text = f'\t{self.assignments[-1]};\n\tIndexStmt stmt = {self.outputs[-1]}.getAssignment().concretize();\n'
            
        text += f'\tstmt = stmt\n'
        text += ''.join(['\t\t' + s + '\n' for s in self.schedules[-1]]) + '\t\t;\n'
        result += text
        
        return result
    
    def get_execute_commands(self):
        result = ""
        
        for i in range(len(self.outputs) - 1):
            result += f'\t\t{self.outputs[i]}.compute(stmt_{self.outputs[i]});\n'
            
        result += f'\t\t{self.outputs[-1]}.compute(stmt);\n'
        
        return result
        
    def get_vector_declaration(self, paths: dict):
        return ''.join(["\tvector<int> " + paths[key] + " = " + key + ";\n" for key in paths])  
        
    def set_tensor_accesses(self, tensor_accesses: dict):
        self.tensor_accesses = deepcopy(tensor_accesses)
        
    def wrap_in_block(self, text):
        return f'/* BEGIN {self.test_name} TEST */\n' + text + f'\t/* END {self.test_name} TEST */'
        
    def wrap_in_execute_block(self, text):
        return f'/* BEGIN {self.test_name}_execute TEST */\n' + text + f'\t\t/* END {self.test_name}_execute TEST */'
            
    def visit(self, config):
        
        for key in config.temporary:
            if (key not in self.tensor_accesses):
                config.temporary[key] = [idx for idx in self.original_index_order if idx in config.temporary[key]]
                self.tensor_accesses.update(config.temporary)
        
        if (config.fused == 1):
            tctt = TransformConfigToTaco(config, self.test_name, self.tensor_accesses)
            
            schedule, paths = tctt.convert_config()
            self.assignments.append(tctt.get_assignment())
            self.outputs.append(tctt.get_output())
            self.schedules.append(schedule)
            self.paths.append(paths)
            self.expr_definitions.append(tctt.get_expression())
            
        elif (config.fused == 0):
            assert config.prod != None and config.cons != None
            
            self.visit(config.prod)
            self.visit(config.cons)
            
            config.fused = 1
            config.expr = [config.prod.output, config.cons.output]
            config.prod = None
            config.cons = None
            
            self.visit(config)
        elif (config.fused == 2):
            assert config.prod != None and config.cons != None
            self.visit(config.prod)
            self.visit(config.cons)
            
        # self.tensor_accesses = {k: v for k, v in self.tensor_accesses.items() if k not in config.temporary}
        
        config = None

class TransformConfigToTaco:
    def __init__(self, config: Config, test_name: str, tensor_accesses: dict = None):
        
        self.config = config
        self.test_name = test_name
        self.tensor_accesses = tensor_accesses
        self.print_string = []
        
    def gen_taco_code(self):
        schedule, paths = self.convert_config()
        expr_definition = self.get_expression()
        
        text = expr_definition + "\n"
        text += self.get_vector_declaration(paths)
        text += "\n\tstmt=stmt\n"
        text += ''.join(['\t\t' + s + '\n' for s in schedule]) + "\t\t;\n\n"
        
        print(schedule)
        
        text = f'/* BEGIN {self.test_name} TEST */\n' + text + f'\t/* END {self.test_name} TEST */'
        print(text)
        return text
        
    def get_vector_declaration(self, paths: dict):
        return ''.join(["\tvector<int> " + paths[key] + " = " + key + ";\n" for key in paths])
        
    # this function handles fused schedules
    def convert_config(self):
        assert self.config.fused == 1
                
        # handle the case where non-fused configs are passed to this class
        # GenerateScheduleVisitor currently only handles fused configs
        visitor = GenerateScheduleVisitor(self.tensor_accesses)
        visitor.visit(self.config)
        
        return visitor.transformed_schedule, visitor.paths
    
    def get_output(self):
        return self.config.output

    def get_assignment(self):
        result = "" + self.config.output + "(" + ", ".join([idx for idx in self.config.output_idx_order]) + ") = "
        
        result += ' * '.join([tensor + "(" + ", ".join([idx for idx in self.tensor_accesses[tensor]]) + ")" for tensor in self.config.expr])
        
        return result
            
    def get_expression(self):
        assert self.config.fused == 1
        print(self.tensor_accesses)
        
        result = "\n\t" + self.config.output + "(" + ", ".join([idx for idx in self.config.output_idx_order]) + ") = "
        
        result += ' * '.join([tensor + "(" + ", ".join([idx for idx in self.tensor_accesses[tensor]]) + ")" for tensor in self.config.expr])
                
        result += ";\n"
        result += "\tIndexStmt stmt = " + self.config.output + ".getAssignment().concretize();\n\tstd::cout << stmt << endl;\n"        
        
        return result
    
