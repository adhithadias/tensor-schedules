# Config class definition
# This is a representation of schedule
class Config:
    def __init__(self, expr):
        print('Creating config with', expr)
        self.expr = expr # computation
        self.fused = False # False -> unfused; True -> fused
        self.prod = None  # schedule for producer
        self.cons = None  # schedule for consumer

    def subconfig(self, prod, cons, fused):
        # assigning subschedules
        self.fused = fused
        self.prod = prod
        self.cons = cons

    def accept(self, visitor):
        visitor.visit(self)