from z3 import *
# Config class definition
# This is a representation of schedule
# fused = 0: unfused, 1: fused, 2: partially fused
class Config:
    def __init__(self, output : str, expr : list, output_idx_order : tuple = None, input_idx_order : tuple = None, fused : int = 0, prod_on_left : bool = None):
        # print('Creating config with', expr, 'fused', fused, 'output_idx_order', output_idx_order, 'input_idx_order', input_idx_order)
        self.output = output
        self.expr = expr # computation
        self.fused = fused # False -> unfused; True -> fused
        self.output_idx_order = output_idx_order
        self.input_idx_order = input_idx_order
        self.prod_on_left = prod_on_left
        self.original_idx_perm = None
        self.prod = None  # Config schedule for producer
        self.cons = None  # Config schedule for consumer
        self.time_complexity = {}
        self.memory_complexity = {}
        
        self.z3_time_complexity = None
        self.z3_memory_complexity = None
        self.group = None

    def __str__(self):
        output = self.output + "(" + ','.join(self.output_idx_order) + ")"

        tensor_contraction = ""
        for i in range(len(self.expr)):
            tensor = self.expr[i]
            tensor_contraction += tensor
            if (i != len(self.expr)-1):
                tensor_contraction += "*"

        return output + "=" + tensor_contraction + ', fused: ' + str(self.fused) + ", pol: " + str(self.prod_on_left) + ' | loop_order:' + str(self.input_idx_order) + ' | time: ' + str(self.time_complexity) + ' | memory: ' + str(self.memory_complexity) + '|'

    def __eq__(self, other):
        if (other == None):
            return False
        return self.output == other.output and self.expr == other.expr and self.output_idx_order == other.output_idx_order and self.input_idx_order == other.input_idx_order and self.fused == other.fused and self.prod == self.prod and self.cons == self.cons

    def __hash__(self):
        return hash((self.output, self.output, self.output_idx_order, self.expr, self.input_idx_order, self.fused, self.prod, self.cons))

    def subconfig(self, prod, cons, fused = False):
        # assigning subschedules
        # print('Updating config with', self.expr, 'fused', fused, 'output_idx_order', self.output_idx_order, 'input_idx_order', self.input_idx_order, 'prod', prod, 'cons', cons)
        self.fused = fused
        self.prod = prod
        self.cons = cons

    def set_input_idx_order(self, input_idx_order):
        self.input_idx_order = input_idx_order

    def set_output_idx_order(self, output_idx_order):
        self.output_idx_order = output_idx_order

    def accept(self, visitor):
        visitor.visit(self)