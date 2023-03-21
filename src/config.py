# Config class definition
# This is a representation of schedule
class Config:
    def __init__(self, output, expr, output_idx_order = None, input_idx_order = None, fused = False, prod_on_left = None):
        # print('Creating config with', expr, 'fused', fused, 'output_idx_order', output_idx_order, 'input_idx_order', input_idx_order)
        self.output = output
        self.expr = expr # computation
        self.fused = fused # False -> unfused; True -> fused
        self.output_idx_order = output_idx_order
        self.input_idx_order = input_idx_order
        self.prod_on_left = prod_on_left
        self.prod = None  # Config schedule for producer
        self.cons = None  # Config schedule for consumer

    def subconfig(self, prod, cons, fused):
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