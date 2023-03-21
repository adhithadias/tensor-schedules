from src.config import Config

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
            tensor_contraction += tensor + "(" + ','.join(self.tensor_accesses[tensor]) + ")"
            if (i != len(config.expr)-1):
                tensor_contraction += "*"

        print('\t'*self.tabs, '|', 
            output, '=',
            tensor_contraction, 
            ', fused: ' + str(config.fused) + ", pol: " + str(config.prod_on_left),
            '| loop_order:', config.input_idx_order)
        self.tabs += 1
        if (config.prod != None): self.visit(config.prod)
        if (config.cons != None): self.visit(config.cons)
        self.tabs -= 1
