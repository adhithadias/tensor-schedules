# Config class definition
# This is a representation of schedule
class Config:
    def __init__(self, expr):
        print('Creating config with', expr)
        self.expr = expr # computation
        self.fused = False # False -> unfused; True -> fused
        self.prod = None  # schedule for producer
        self.cons = None  # schedule for consumer
        self.idx_pattern = None

    def subconfig(self, prod, cons, fused):
        # assigning subschedules
        self.fused = fused
        self.prod = prod
        self.cons = cons
        self.idx_pattern = None

    def setidx(self, idx_pattern):
        self.idx_pattern = idx_pattern

    def accept(self, visitor):
        visitor.visit(self)