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
            tensor_contraction += tensor + \
                "(" + ','.join(self.tensor_accesses[tensor]) + ")"
            if (i != len(config.expr)-1):
                tensor_contraction += "*"

        print('\t'*self.tabs, '|',
              output, '=',
              tensor_contraction,
              ', fused: ' + str(config.fused) + ", pol: " +
              str(config.prod_on_left),
              '| loop_order:', config.input_idx_order)
        self.tabs += 1
        if (config.prod != None):
            self.visit(config.prod)
        if (config.cons != None):
            self.visit(config.cons)
        self.tabs -= 1


class GetComplexityVisitor(Visitor):
    def __init__(self, tensor_accesses: dict) -> None:
        self.tensor_accesses = tensor_accesses

    def retrieve_time_complexity(self, schedule=[]) -> str:
        complexity = ""
        if len(schedule) > 0 and type(schedule[-1]) == list:
            producer = self.retrieve_time_complexity(schedule[-2])
            consumer = self.retrieve_time_complexity(schedule[-1])
            if len(schedule[0:-2]) > 0:
                complexity += "*".join(schedule[0:-2]) + "*"
            if len(producer) > 0 and len(consumer) > 0:
                complexity += "(" + producer + "+" + consumer + ")"
                return complexity
            elif len(producer) > 0:
                return complexity + "(" + producer + ")"
            elif len(consumer) > 0:
                return complexity + "(" + consumer + ")"
            else:
                # return "*".join(schedule[0:-2])
                return ""
        elif len(schedule) <= 0:
            return ""
        else:
            return "*".join(schedule)

    # retrieve complexity of a given tensor schedule
    # def retrieve_complexity(schedule: Config) -> str:
    #     complexity = ""
    #     # check if fused loop
    #     if len(schedule.input_idx_order) > 0 and type(schedule.input_idx_order[-1]) == list:
    #         producer = retrieve_fused_complexity(schedule.input_idx_order[-2])
    #         consumer = retrieve_fused_complexity(schedule.input_idx_order[-1])
    #         if len(schedule.input_idx_order[0:-2]) > 0:
    #             complexity += "*".join(schedule.input_idx_order[0:-2]) + "*"
    #         if len(producer) > 0 and len(consumer) > 0:
    #             complexity += "(" + producer + "+" + consumer + ")"
    #             return complexity
    #         elif len(producer) > 0:
    #             return complexity + "(" + producer + ")"
    #         elif len(consumer) > 0:
    #             return complexity + "(" + consumer + ")"
    #         else:
    #             # return "*".join(schedule.input_idx_order[0:-2])
    #             return ""
    #     elif len(schedule.input_idx_order) <= 0:
    #         return ""
    #     else:
    #         return "*".join(schedule.input_idx_order)
    
    def retrieve_space_complexity(self, config:Config) -> str:
        complexity = ""
        

    def visit(self, config: Config):
        config.set_time_complexity(self.retrieve_time_complexity(config))
        config.set_space_complexity(self.retrieve_space_complexity(config))
