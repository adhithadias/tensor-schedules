from config import Config

class Visitor:
    def __str__(self):
        return self.__class__.__name__

    
class PrintConfigVisitor(Visitor):
    def __init__(self):
        self.tabs = 0
    
    def visit(self, config):
        print('\t'*self.tabs, '|', config.expr, 'fused:', config.fused)
        self.tabs += 1
        if (config.prod != None): self.visit(config.prod)
        if (config.cons != None): self.visit(config.cons)
        self.tabs -= 1


