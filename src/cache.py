from src.visitor import Visitor
from src.basket import Baskets
from src.config import Config
# from src.visitor import PrintConfigVisitor

class CacheComplexityVisitor(Visitor):
    def __init__(self, tensor_accesses: dict, original_index_order: list):
        self.cache_complexity = []
        self.order = []
        self.tensor_accesses = tensor_accesses
        self.original_index_order = original_index_order

    def visit(self, config : Config):
        
        for key in config.temporary:
            config.temporary[key] = [idx for idx in self.original_index_order if idx in config.temporary]
        
        self.tensor_accesses.update(config.temporary)
              
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
            
            accessed_tensors_in_comp = list(config.expr)
            accessed_tensors_in_comp.append(config.output)
            
            # do the config calculation here
            last_index = config.input_idx_order[-1]
            # print('last_index', last_index, self.tensor_accesses)
            for i, tensor in enumerate(accessed_tensors_in_comp):
                
                # # temporary is saved with the config at generation.
                # # removing the TODO
                # if tensor not in self.tensor_accesses:
                #     # if the tensor is not in tensor_accesses, that means it is a temporary tensor, we will focus on this later
                #     continue
                
                if last_index not in self.tensor_accesses[tensor]:
                    # index is not in the tensor, it's accessed again and again, therefore there is no cache cost
                    pass
                elif last_index == self.tensor_accesses[tensor][-1]:
                    # index is the last index of the tensor, therefore there is good spatial locality. Hence, there is no cost
                    pass
                else:
                    # now the last_index is in the tensor_accesses but it is not the last index in the tensor access index list. So we add all the indices after the last_index to the complexity set
                    last_index_index = self.tensor_accesses[tensor].index(last_index)
                    # print('adding for tensor', self.tensor_accesses[tensor])
                    # get all the indices after the last_index_index
                    values_after_last_idx_idx = self.tensor_accesses[tensor][last_index_index+1:]
                    complexity.append(values_after_last_idx_idx)
                  
            accessed_tensors_in_comp.pop()
            self.cache_complexity.extend(complexity)
            
        self.tensor_accesses = {k: v for k, v in self.tensor_accesses.items() if k not in config.temporary}

def add_cache_locality(accesses, baskets):
    assert type(baskets) == Baskets
    assert type(accesses) == dict
    
    for i, (_, _, basket_list) in enumerate(baskets.get_baskets()):
        for j, config  in enumerate(basket_list):
            cacheVisitor = CacheComplexityVisitor(accesses, config.original_idx_perm)
            config.accept(cacheVisitor)
            
            # if (i == 1):
            #     printer = PrintConfigVisitor(accesses)
            #     config.accept(printer)
            
            config.cache_complexity = cacheVisitor.cache_complexity
            
            # if (i == 1):
            #     print(accesses)
            #     # print(config)
            #     print(config.cache_complexity)
            #     print('----------')