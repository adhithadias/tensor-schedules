from src.visitor import Visitor
from src.basket import Baskets
from src.config import Config

class CacheComplexityVisitor(Visitor):
    def __init__(self, tensor_accesses: dict):
        self.cache_complexity = []
        self.order = []
        self.tensor_accesses = tensor_accesses

    def visit(self, config : Config):        
        # if the config has a prod or cons, then we need to visit them
        if (config.prod != None and config.cons != None):
            # need to add the temporary to tensor_accesses, maybe a list of temporary tensors
            
            config.prod.accept(self)
            config.cons.accept(self)
            
            # remove the temporary tensor from the list
        elif (config.prod != None): config.prod.accept(self)
        elif (config.cons != None): config.cons.accept(self)
        else:
            # leaf of the config tree, we need to calculate the complexity and store it in the config
            '''
                config.output has the output tensor
                config.expr has the input tensors
            '''
            complexity = list()
            # do the config calculation here
            last_index = config.input_idx_order[-1]
            for i, tensor in enumerate(config.expr):
                if tensor not in self.tensor_accesses:
                    # if the tensor is not in tensor_accesses, that means it is a temporary tensor, we will focus on this later
                    # TODO - add temporary tensor cost
                    continue
                
                if last_index not in self.tensor_accesses[tensor]:
                    # index is not in the tensor, it's accessed again and again, therefore there is no cache cost
                    pass
                elif last_index == self.tensor_accesses[tensor][-1]:
                    # index is the last index of the tensor, therefore there is good spatial locality. Hence, there is no cost
                    pass
                else:
                    # now the last_index is in the tensor_accesses but it is not the last index in the tensor access index list. So we add all the indices after the last_index to the complexity set
                    last_index_index = self.tensor_accesses[tensor].index(last_index)
                    # get all the indices after the last_index_index
                    values_after_last_idx_idx = self.tensor_accesses[tensor][last_index_index+1:]
                    complexity.append(values_after_last_idx_idx)
                    
            self.cache_complexity.extend(complexity)

def add_cache_locality(accesses, baskets):
    assert type(baskets) == Baskets
    assert type(accesses) == dict
    
    for i, (_, _, basket_list) in enumerate(baskets.get_baskets()):
        for j, config  in enumerate(basket_list):
            cacheVisitor = CacheComplexityVisitor(accesses)
            config.accept(cacheVisitor)
            
            config.cache_complexity = cacheVisitor.cache_complexity
            print(accesses)
            print(config)
            print(config.cache_complexity)
            print('----------')