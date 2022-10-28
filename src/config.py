# Config class definition
# This is a representation of schedule
class Config:
    def __init__(self, expr):
        print('Creating config with', expr)
        self.expr = expr # computation
        self.fus = False # False -> unfused; True -> fused
        self.pro = None  # schedule for producer
        self.con = None  # schedule for consumer

    def subconfig(self, pro, con, fus):
        # assigning subschedules
        self.fus = fus
        self.pro = pro
        self.con = con
