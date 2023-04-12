from src.config import Config
from src.prune import get_mem_depth
from src.util import *
import itertools
			
# Producing a config of unfused schedules
# Input -> Two configs; Output -> One config
def unfused(output: str, expr, output_index_order, prod_config, cons_config, unfused_schedules):
    '''
    get prod_config.output_idx_order and cons_config.output_idx_order
    prod_config.output_idx_order * cons_config.output_idx_order defines 
    the input_idx_order for unfused schedules
    '''
    prod_output_idx_order = prod_config.output_idx_order
    cons_output_idx_order = cons_config.output_idx_order
    idx_set = set(prod_output_idx_order) | set(cons_output_idx_order)
    idxes = list(idx_set)
    idx_perms = list(itertools.permutations(idxes))
    
    time_complexity = {}
    time_complexity['r'] = [{idx: 0 for idx in idx_set}]
    additional_complexity = []
    if 'r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None : additional_complexity.extend(prod_config.time_complexity['r'])
    if 'a' in prod_config.time_complexity and prod_config.time_complexity['a'] is not None: additional_complexity.extend(prod_config.time_complexity['a'])
    if 'r' in cons_config.time_complexity and cons_config.time_complexity['r'] is not None: additional_complexity.extend(cons_config.time_complexity['r'])
    if 'a' in cons_config.time_complexity and cons_config.time_complexity['a'] is not None: additional_complexity.extend(cons_config.time_complexity['a'])
    time_complexity['a'] = additional_complexity
    
    memory_complexity = []
    memory_complexity.append(set(prod_config.output_idx_order))
    memory_complexity.append(set(cons_config.output_idx_order))
    if prod_config.memory_complexity is not None: memory_complexity.extend(prod_config.memory_complexity)
    if cons_config.memory_complexity is not None: memory_complexity.extend(cons_config.memory_complexity)
    
    if (get_mem_depth(memory_complexity) > 2): return

    # unfused_schedules = []
    for idx_perm in idx_perms:
        unfus = Config(output, expr, output_idx_order = output_index_order, input_idx_order = idx_perm, fused = False)
        unfus.subconfig(prod_config, cons_config, False)
        unfus.time_complexity = time_complexity
        unfus.memory_complexity = memory_complexity
        unfused_schedules.append(unfus)
    # return unfused_schedules
    
def partially_fused():
    pass
	
# Producing a config of fused schedules
# Input -> Two configs; Output -> One config
def fused(output: str, expr, output_idx_order, prod_config, cons_config, prod_on_left, fused_scheds, tensor_idx_order_constraints = {}):
    i = 0
    # add additional indices in output_idx_order to cons_config.input_idx_order
    # because that defines all the loops in the final computation
    cons_config_input_idx_order = get_idxes_in_config(cons_config.input_idx_order)
    # output_idx_order is a linear list of indices without branches
    # cons_config.input_idx_order can contain branches
    idx_only_in_output = [idx for idx in output_idx_order if idx not in cons_config_input_idx_order]
    # now these indices can be added to different locations in cons_config.input_idx_order
    # up to the point branching happens if there are any

    # find the point where branching happens, if there is branching
    # ['i', 'j', ['k'], ['l']]
    # linear_list = ['i', 'j']; post_list = [['k'], ['l']]
    linear_list, post_list = get_idxes_up_to_branching_point(cons_config.input_idx_order)
    
    # now if, let's say 'm', 'n' is only in the output_idx_order (simply output)
    # get_all_permutations will return all the permutations of the linear list by adding permutations 'm' and 'n' at different locations
    # it will use a worklist algorithm to add 'm' to linear_list = ['i','j'] and then add 'n' to linear_lists = ['m','i','j'], ['i','m','j'], ['i','j','m']
    perms = get_all_permutations(idx_only_in_output, linear_list)
    
    # TODO - check if adding this here is correct
    perms = [perms for perms in perms if is_valid_idx_perm(perms, tensor_idx_order_constraints, cons_config.expr, output)]
    
    perms = append_list_to_list_of_lists(perms, post_list)

    # fused_scheds = []

    for cons_order in perms:

        i = 0
        common_loops_found = False
        for i in range(max(len(prod_config.input_idx_order), len(cons_order))):
            if (i < min(len(prod_config.input_idx_order), len(cons_order)) and 
                isinstance(prod_config.input_idx_order[i], str) and 
                isinstance(cons_order[i], str) and
                prod_config.input_idx_order[i] == cons_order[i]):
                common_loops_found = True
                continue
            else:
                i += 1
                break

        # continue for the next order if no common indices are found
        # TODO - consider the case where there are no common indices and there is only 1 tensor in the cons config
        if not common_loops_found:
            # scheduling space grows exponentially if we add these schedules to the list
            # X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m) example 3000+ without grows to 8000+ with
            # in_idx_order = [[], [prod_config.input_idx_order, cons_order]]
            # unfus = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = in_idx_order, fused = True, prod_on_left = prod_on_left)
            # unfus.subconfig(prod_config, cons_config, True)
            # fused_scheds.append(unfus)
            continue

        # break doesn't increase the i count while continue does increase
        # handle the case where there are no common indices added i+=1
        # to the break case and splicing the arrays at i-1 location

        common_loops = prod_config.input_idx_order[:i-1]
        prod_loops = prod_config.input_idx_order[i-1:]
        cons_loops = cons_order[i-1:]
        
        # the amount of additional memory is a direct function of the indices shared by the producer and the consumer
        # we just have to collect indices in the producer and consumer and find the intersection
        prod_loops_set = get_idxes_in_config(prod_loops)
        cons_loops_set = get_idxes_in_config(cons_loops)
        mem_complexity = []
        memory_complexity = prod_loops_set.intersection(cons_loops_set)
        if (len(memory_complexity) > 0): mem_complexity.append(memory_complexity)
        if prod_config.memory_complexity is not None: mem_complexity.extend(prod_config.memory_complexity)
        if cons_config.memory_complexity is not None: mem_complexity.extend(cons_config.memory_complexity)
        
        # the time complexity is a function of common loops, prod_loops and cons_loops
        time_complexity = {}
        relevant = []
        additional = []
        common_idx_for_complexity = get_time_complexity(common_loops, expr, tensor_idx_order_constraints)
        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
            for tcomp in prod_config.time_complexity['r']:
                tcomp = {key: tcomp[key] for key in tcomp.keys() if (key not in common_loops)}
                # tcomp = tcomp - common_idx_for_complexity - set(common_loops)
                if (len(tcomp) > 0): relevant.append({**tcomp, **common_idx_for_complexity})
            # relevant.extend(prod_config.time_complexity['r'])
        if ('a' in prod_config.time_complexity and prod_config.time_complexity['a'] is not None):
            additional.extend(prod_config.time_complexity['a'])
        if ('r' in cons_config.time_complexity and cons_config.time_complexity['r'] is not None):
            for tcomp in cons_config.time_complexity['r']:
                tcomp = {key: tcomp[key] for key in tcomp.keys() if (key not in common_loops)}
                indices_not_already_in = {key: 0 for key in memory_complexity if (key not in tcomp.keys() and key not in common_loops)}
                if (len(tcomp) > 0): relevant.append({**tcomp, **common_idx_for_complexity, **indices_not_already_in})
            # relevant.extend(cons_config.time_complexity['r'])
        if ('a' in cons_config.time_complexity and cons_config.time_complexity['a'] is not None):
            additional.extend(cons_config.time_complexity['a'])
        time_complexity['r'] = relevant
        time_complexity['a'] = additional

        in_idx_order = []
        in_idx_order.extend(common_loops)
        in_idx_order.extend([prod_loops, cons_loops])

        fus = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = in_idx_order, fused = True, prod_on_left = prod_on_left)
        fus.subconfig(prod_config, cons_config, True)
        fus.memory_complexity = mem_complexity
        fus.time_complexity = time_complexity
        fused_scheds.append(fus)

    # return fused_scheds


def get_placeholder_configs(output: str, output_idx_order: list, expr: list, tensor_accesses: dict, loop_order: list, tensor_idx_order_constraints: dict, start : int, end : int) -> list:

    # print('get_schedules', output, output_idx_order, expr, tensor_accesses, loop_order, tensor_idx_order_constraints, start, end, flush=True)
    # itertools returns a list of tuples
    idx_perms = list(itertools.permutations(loop_order))
    idx_perms = [tuple(idx_perm) for idx_perm in idx_perms if is_valid_idx_perm(idx_perm, tensor_idx_order_constraints, expr, output)]
    # print('lenth of permutations:', len(idx_perms), flush=True)
    
    scheds = []
    for i, idx_perm in enumerate(idx_perms):
        # print('---', flush=True)
        # print(idx_perm, flush=True)
        time_complexity = {}
        time_complexity['r'] = [get_time_complexity(set(idx_perm), expr, tensor_idx_order_constraints)]
        time_complexity['a'] = []
        memory_complexity = []
        
        # perfectly linear loop order is considered as fused = True
        nconf = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = idx_perm, fused = True)
        nconf.time_complexity = time_complexity
        nconf.memory_complexity = memory_complexity
        scheds.append(nconf)
        
    return scheds


def get_schedules(output: str, output_idx_order: tuple, expr: tuple, tensor_accesses: dict, loop_order: tuple, tensor_idx_order_constraints: dict, start : int, end : int, depth : int, cache : dict, bigger_cache : dict, is_print = False) -> set:
    
    if ((output, output_idx_order, loop_order, expr) in cache):
        print('found in bigger cache', (output, output_idx_order, loop_order, expr), flush=True)
        return bigger_cache[(output, output_idx_order, loop_order, expr)]
        
    if is_print: print(loop_order, end='', flush=True)
    if (len(loop_order) == 0): return set()
    
    if is_print: print(depth, end='', flush=True)
    print('get_schedules', output, output_idx_order, loop_order, expr, tensor_accesses, tensor_idx_order_constraints, start, end, flush=True)
    # itertools returns a list of tuples
    idx_perms = list(itertools.permutations(loop_order))
    # print(loop_order, len(idx_perms), flush=True)
    idx_perms = [idx_perm for idx_perm in idx_perms if is_valid_idx_perm(idx_perm, tensor_idx_order_constraints, expr, output)]
    
    if is_print: print (len(idx_perms))
    
    # print('lenth of permutations:', len(idx_perms), flush=True)
    
    scheds = set()
    for i, idx_perm in enumerate(idx_perms):
        
        if ((output, output_idx_order, idx_perm, expr) in cache):
            print('found in cache', (output, output_idx_order, idx_perm, expr), flush=True)
            local_scheds = cache[(output, output_idx_order, idx_perm, expr)]
            scheds.update(local_scheds)
            # for local_sched in local_scheds:
            #     if (local_sched not in scheds): scheds.add(local_sched)
            continue
        
        local_scheds = set()
        print('---', flush=True)
        print(idx_perm, flush=True)
        time_complexity = {}
        time_complexity['r'] = [get_time_complexity(set(idx_perm), expr, tensor_idx_order_constraints)]
        time_complexity['a'] = []
        memory_complexity = []
        
        # perfectly linear loop order is considered as fused = True
        nconf = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = idx_perm, fused = True)
        nconf.time_complexity = time_complexity
        nconf.memory_complexity = memory_complexity
        if (nconf not in scheds): scheds.add(nconf)
        if (nconf not in local_scheds): local_scheds.add(nconf)
        
        if (len(expr) <= 2 or len(loop_order) == 1):
            cache[(output, output_idx_order, idx_perm, expr)] = local_scheds
            continue
        
        for i in range(start + 1, end):
            # Now break the expression into smaller ones
            pre_expr, post_expr = expr[:i], expr[i:]
            print('pre_expr, post_expr:', pre_expr, post_expr, flush=True)
            
            # get the list of schedules for pre and post expr
            # TODO - need to pass the output indexes to both sched_enum calls
            # since this is a sub module
            pre_ind, post_ind = define_data_layout(output_idx_order, pre_expr, post_expr, tensor_accesses)
            print('producer and consumer indices:', pre_ind, post_ind, flush=True)
            idx_prod_list = get_input_idx_list(pre_expr, tensor_accesses)
            
            temporary = ("_" * depth) + output
            tensor_accesses[temporary] = pre_ind
            # print((str("_"*depth+output)), post_expr, flush=True)
            new_post_expr = tuple([temporary]) + post_expr
            # print(new_post_expr, flush=True)
            print('input_expr_breakdown:', pre_expr, new_post_expr, flush=True)
            idx_cons_list = get_input_idx_list(new_post_expr, tensor_accesses)
            
            prod_idx_order = [idx for idx in idx_perm if idx in idx_prod_list]
            cons_idx_order = [idx for idx in idx_perm if idx in idx_cons_list]
            
            print('producer and consumer idx order:', prod_idx_order, cons_idx_order, flush=True)
            
            i = 0
            for (prod_idx, cons_idx) in zip(prod_idx_order, cons_idx_order):
                if (prod_idx == cons_idx):
                    i += 1
                else:
                    break
                    
            if (i != 0): # some loops can be fused
                print('fused')
                common_loops = tuple(prod_idx_order[:i])
                prod_loops = tuple(prod_idx_order[i:])
                cons_loops = tuple(cons_idx_order[i:])
                
                # print("fusible loops:", common_loops, prod_loops, cons_loops, flush=True)
                new_prod_output_indices = tuple([idx for idx in pre_ind if idx not in common_loops])
                new_cons_output_indices = tuple([idx for idx in output_idx_order if idx not in common_loops])
                new_tensor_accesses = {key: tuple([idx for idx in tensor_accesses[key] if idx not in common_loops]) for key in tensor_accesses.keys()}
                new_tensor_accesses[temporary] = new_prod_output_indices
                
                # prod_configs = get_placeholder_configs(temporary, new_prod_output_indices, pre_expr, new_tensor_accesses, prod_loops, tensor_idx_order_constraints, 0, len(pre_expr))
                prod_configs = get_schedules(temporary, new_prod_output_indices, pre_expr, new_tensor_accesses, prod_loops, tensor_idx_order_constraints, 0, len(pre_expr), depth + 1, cache, bigger_cache)
                # cons_configs = get_placeholder_configs(output, new_cons_output_indices, new_post_expr, new_tensor_accesses, cons_loops, tensor_idx_order_constraints, 1, len(new_post_expr))
                cons_configs = get_schedules(output, new_cons_output_indices, new_post_expr, new_tensor_accesses, cons_loops, tensor_idx_order_constraints, 1, len(new_post_expr), depth + 1, cache, bigger_cache)
                # print('new configs:', new_prod_output_indices, new_cons_output_indices, new_tensor_accesses)
                
                shared_loops = set(prod_loops).intersection(set(cons_loops))
                for j, prod_config in enumerate(prod_configs):
                    for k, cons_config in enumerate(cons_configs):
                        input_idx_order = common_loops + (prod_config.input_idx_order, cons_config.input_idx_order)
                        
                        # input_idx_order.extend(common_loops)
                        # input_idx_order.extend([prod_config.input_idx_order, cons_config.input_idx_order])
                        nconf = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = input_idx_order, fused = True)
                        # nconf.time_complexity = time_complexity
                        nconf.memory_complexity = [shared_loops]
                        nconf.memory_complexity.extend(prod_config.memory_complexity)
                        nconf.memory_complexity.extend(cons_config.memory_complexity)
                        
                        # print(prod_config.time_complexity)
                        time_complexity = {}
                        tr = []
                        ta = []
                        common_idx_for_complexity = get_time_complexity(common_loops, expr, tensor_idx_order_constraints)
                        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
                            for tc in prod_config.time_complexity['r']:
                                # print(tc)
                                tr.append({**tc, **common_idx_for_complexity})
                        if ('r' in cons_config.time_complexity and cons_config.time_complexity['r'] is not None): 
                            for tc in cons_config.time_complexity['r']:
                                tr.append({**tc, **common_idx_for_complexity})
                        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
                            for tc in prod_config.time_complexity['a']:
                                ta.extend(tc)
                        if ('a' in cons_config.time_complexity and cons_config.time_complexity['a'] is not None):
                            for tc in cons_config.time_complexity['a']:
                                ta.extend(tc)
                            
                        time_complexity['r'] = tr
                        time_complexity['a'] = ta
                        nconf.time_complexity = time_complexity
                        
                        nconf.subconfig(prod_config, cons_config, fused=True)
                        
                        if (nconf not in scheds): scheds.add(nconf)
                        if (nconf not in local_scheds): local_scheds.add(nconf)
                 
            # adding else part does not terminate the program       
            else:
                # print('unfused')
                prod_loops = tuple(prod_idx_order)
                cons_loops = tuple(cons_idx_order)
                new_tensor_accesses = {key: tuple([idx for idx in tensor_accesses[key]]) for key in tensor_accesses.keys()}
                new_tensor_accesses[temporary] = pre_ind
                
                # print('-->', prod_loops, cons_loops, new_tensor_accesses, flush=True)
                
                prod_configs = get_schedules(temporary, pre_ind, pre_expr, new_tensor_accesses, prod_loops, tensor_idx_order_constraints, 0, len(pre_expr), depth + 1, cache, bigger_cache)
                cons_configs = get_schedules(output, output_idx_order, new_post_expr, new_tensor_accesses, cons_loops, tensor_idx_order_constraints, 1, len(new_post_expr), depth + 1, cache, bigger_cache)
                
                # print('-->', prod_configs, cons_configs, flush=True)
                shared_loops = set(prod_loops).intersection(set(cons_loops))
                for k, cons_config in enumerate(cons_configs):
                    for j, prod_config in enumerate(prod_configs):
                        input_idx_order = (prod_config.input_idx_order, cons_config.input_idx_order) # no common loops here because it is not fused
                        
                        # input_idx_order.extend(common_loops)
                        # input_idx_order.extend([prod_config.input_idx_order, cons_config.input_idx_order])
                        nconf = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = input_idx_order, fused = False)
                        # nconf.time_complexity = time_complexity
                        nconf.memory_complexity = [shared_loops]
                        nconf.memory_complexity.extend(prod_config.memory_complexity)
                        nconf.memory_complexity.extend(cons_config.memory_complexity)
                        # nconf.memory_complexity.extend(cons_config.memory_complexity)
                        
                        time_complexity = {}
                        tr = []
                        ta = []
                        # common_idx_for_complexity = get_time_complexity(common_loops, expr, tensor_idx_order_constraints)
                        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
                            for tc in prod_config.time_complexity['r']:
                                # print(tc)
                                tr.append({**tc})
                        if ('r' in cons_config.time_complexity and cons_config.time_complexity['r'] is not None): 
                            for tc in cons_config.time_complexity['r']:
                                tr.append({**tc})
                        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
                            for tc in prod_config.time_complexity['a']:
                                ta.extend(tc)
                        if ('a' in cons_config.time_complexity and cons_config.time_complexity['a'] is not None):
                            for tc in cons_config.time_complexity['a']:
                                ta.extend(tc)
                            
                        time_complexity['r'] = tr
                        time_complexity['a'] = ta
                        nconf.time_complexity = time_complexity
                        
                        nconf.subconfig(prod_config, cons_config, fused=False)
                        if (nconf not in scheds): scheds.add(nconf)
                        if (nconf not in local_scheds): local_scheds.add(nconf)
            
            tensor_accesses.pop(temporary)
            
            idx_prod_list = get_input_idx_list(post_expr, tensor_accesses)
            
            temporary = (depth * "_") + output
            tensor_accesses[temporary] = post_ind
            new_pre_expr = pre_expr + tuple([temporary])
            idx_cons_list = get_input_idx_list(new_pre_expr, tensor_accesses)
            
            prod_idx_order = [idx for idx in idx_perm if idx in idx_prod_list]
            cons_idx_order = [idx for idx in idx_perm if idx in idx_cons_list]
            
            i = 0
            for (prod_idx, cons_idx) in zip(prod_idx_order, cons_idx_order):
                if (prod_idx == cons_idx):
                    i += 1
                else:
                    break
                
            if (i != 0): # some loops can be fused
                common_loops = tuple(prod_idx_order[:i])
                prod_loops = tuple(prod_idx_order[i:])
                cons_loops = tuple(cons_idx_order[i:])
                
                # print("fusible loops:", common_loops, prod_loops, cons_loops, flush=True)
                new_prod_output_indices = tuple([idx for idx in post_ind if idx not in common_loops])
                new_cons_output_indices = tuple([idx for idx in output_idx_order if idx not in common_loops])
                new_tensor_accesses = {key: tuple([idx for idx in tensor_accesses[key] if idx not in common_loops]) for key in tensor_accesses.keys()}
                new_tensor_accesses[temporary] = new_prod_output_indices
                
                # prod_configs = get_placeholder_configs(temporary, new_prod_output_indices, pre_expr, new_tensor_accesses, prod_loops, tensor_idx_order_constraints, 0, len(pre_expr))
                prod_configs = get_schedules(temporary, new_prod_output_indices, post_expr, new_tensor_accesses, prod_loops, tensor_idx_order_constraints, 0, len(pre_expr), depth + 1, cache, bigger_cache)
                # cons_configs = get_placeholder_configs(output, new_cons_output_indices, new_post_expr, new_tensor_accesses, cons_loops, tensor_idx_order_constraints, 1, len(new_post_expr))
                cons_configs = get_schedules(output, new_cons_output_indices, new_pre_expr, new_tensor_accesses, cons_loops, tensor_idx_order_constraints, 0, len(new_post_expr)-1, depth + 1, cache, bigger_cache)
                # print('new configs:', new_prod_output_indices, new_cons_output_indices, new_tensor_accesses)
                
                shared_loops = set(prod_loops).intersection(set(cons_loops))
                for j, prod_config in enumerate(prod_configs):
                    for k, cons_config in enumerate(cons_configs):
                        input_idx_order = common_loops + (prod_config.input_idx_order, cons_config.input_idx_order)
                        
                        # input_idx_order.extend(common_loops)
                        # input_idx_order.extend([prod_config.input_idx_order, cons_config.input_idx_order])
                        nconf = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = input_idx_order, fused = True)
                        # nconf.time_complexity = time_complexity
                        nconf.memory_complexity = [shared_loops]
                        nconf.memory_complexity.extend(prod_config.memory_complexity)
                        nconf.memory_complexity.extend(cons_config.memory_complexity)
                        
                        time_complexity = {}
                        tr = []
                        ta = []
                        common_idx_for_complexity = get_time_complexity(common_loops, expr, tensor_idx_order_constraints)
                        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
                            for tc in prod_config.time_complexity['r']:
                                # print(tc)
                                tr.append({**tc, **common_idx_for_complexity})
                        if ('r' in cons_config.time_complexity and cons_config.time_complexity['r'] is not None): 
                            for tc in cons_config.time_complexity['r']:
                                tr.append({**tc, **common_idx_for_complexity})
                        if ('r' in prod_config.time_complexity and prod_config.time_complexity['r'] is not None): 
                            for tc in prod_config.time_complexity['a']:
                                ta.extend(tc)
                        if ('a' in cons_config.time_complexity and cons_config.time_complexity['a'] is not None):
                            for tc in cons_config.time_complexity['a']:
                                ta.extend(tc)
                            
                        time_complexity['r'] = tr
                        time_complexity['a'] = ta
                        nconf.time_complexity = time_complexity

                        nconf.subconfig(prod_config, cons_config, fused=True)
                        if (nconf not in scheds): scheds.add(nconf)
                        if (nconf not in local_scheds): local_scheds.add(nconf)
                        
            tensor_accesses.pop(temporary)
                
            # else: # none of the loops can be fused
                # print("unfusible", flush=True)
          
        # cache the output
        # output, output_idx_order, idx_perm, expr
        cache[(output, output_idx_order, idx_perm, expr)] = local_scheds
        
    for i, idx_perm in enumerate(idx_perms):
        bigger_cache[(output, output_idx_order, idx_perm, expr)] = scheds    
    # if is_print: print('num scheds: ', len(scheds), flush=True)
    return scheds

def get_schedules_unfused(output: str, output_idx_order: tuple, expr: tuple, tensor_accesses: dict, loop_order: tuple, tensor_idx_order_constraints: dict, depth : int = 0) -> list:
    
    # print('get_schedules: ', expr)
    # get the fused schedules
    schedules = get_schedules(output, output_idx_order, expr, tensor_accesses, loop_order, tensor_idx_order_constraints, 0, len(expr), depth)
    # schedules = list(schedules)
    # print('done with fused schedules count: ', len(schedules), flush=True)
    
    # for sched in schedules:
    #     print(sched)
    
    if (len(expr) <= 2):
        return schedules
    
    for i in range(1, len(expr)):
        pre_expr, post_expr = expr[:i], expr[i:]
        pre_output, post_output = define_data_layout(output_idx_order, pre_expr, post_expr, tensor_accesses)
        
        pre_loops = get_input_idx_list(pre_expr, tensor_accesses)
        post_loops = get_input_idx_list(post_expr, tensor_accesses)
        
        # print('producer1 schedules: ', pre_output, pre_expr, flush=True)
        producer1_schedules = get_schedules_unfused('0'*depth+output, pre_output, pre_expr, tensor_accesses, pre_loops, tensor_idx_order_constraints, depth + 1)
        # print('number of producer1 schedules: ', len(producer1_schedules), flush=True)
        
        # print('producer2 schedules: ', post_output, post_expr, tensor_accesses, post_loops, tensor_idx_order_constraints, flush=True)
        producer2_schedules = get_schedules_unfused(output+'0'*depth, post_output, post_expr, tensor_accesses, post_loops, tensor_idx_order_constraints, depth + 1)
        # print('number of producer2 schedules: ', len(producer2_schedules), flush=True)
        
        for j, s1 in enumerate(producer1_schedules):
            for k, s2 in enumerate(producer2_schedules):
                
                loop_indices = tuple(set(pre_output + post_output + output_idx_order))
                idx_perms = list(itertools.permutations(loop_indices))
                idx_perms = [idx_perm for idx_perm in idx_perms if is_valid_idx_perm(idx_perm, tensor_idx_order_constraints, expr, output)]
                for idx_perm in idx_perms:
                    unfused = Config(output, expr, output_idx_order, idx_perm, False)
                    unfused.subconfig(s1, s2, False)
                    
                    time_complexity = {}
                    time_complexity['r'] = [{idx: 0 for idx in idx_perm}]
                    ta = []
                    if ('a' in s1.time_complexity and s1.time_complexity['a'] is not None): 
                        ta.extend(s1.time_complexity['a'])
                    if ('a' in s2.time_complexity and s2.time_complexity['a'] is not None): 
                        ta.extend(s2.time_complexity['a'])
                    if ('r' in s1.time_complexity and s1.time_complexity['r'] is not None): 
                        ta.extend(s1.time_complexity['r'])
                    if ('r' in s2.time_complexity and s2.time_complexity['r'] is not None): 
                        ta.extend(s2.time_complexity['r'])
                    time_complexity['a'] = ta
                    unfused.time_complexity = time_complexity
                    
                    memory_complexity = [pre_output, post_output]
                    memory_complexity.extend(s1.memory_complexity)
                    memory_complexity.extend(s2.memory_complexity)
                    unfused.memory_complexity = memory_complexity
                    
                    if not (unfused in schedules): 
                        schedules.add(unfused)
                        
    return schedules
        

# TODO (paper) - proof reorder and tensor breakdown is equal to 
# tensor breakdown and reordering smaller tensor contractions

# TODO (paper) - we will use the 2nd method and give a proof in the paper
# that they cover the entirity of the scheduling space

# Schedule enumeration
# Input -> A tensor expression; Output -> list of configs
def sched_enum(output: str, expr: list, output_idx_order: list, tensor_accesses: dict, tensor_idx_order_constraints: dict, scheds: list) -> list:
    # Input is the expression or computation
    # This is something like [A, B, C, D]
    assert isinstance(output, str)
    assert all(isinstance(output_idx, str) for output_idx in output_idx_order)
    assert all(isinstance(tensor_var, str) for tensor_var in expr)

    # Output is a list of schedule configs
    idx_set = get_input_idx_list(expr, tensor_accesses)
    idx_perms = list(itertools.permutations(idx_set))
    # print(".:", expr, "p_n: ", len(idx_perms))

    # remove idx_perms that violates the tensor_idx_order_constraints
    idx_perms = [idx_perm for idx_perm in idx_perms if is_valid_idx_perm(idx_perm, tensor_idx_order_constraints, expr, output)]
    # print(".:", expr, "p_n: ", len(idx_perms))
    
    # time complexity is completely dependent on the perfectly nested linear loop list
    # iterate through tensor_idx_order_constraints and check if index is in the input_idx_order
    time_complexity = {}
    time_complexity['r'] = [get_time_complexity(idx_set, expr, tensor_idx_order_constraints)]
    time_complexity['a'] = []
    memory_complexity = []

    # scheds = []
    for input_idx_order in idx_perms:
        # perfectly linear loop order is considered as fused = True
        nconf = Config(output, expr, output_idx_order = output_idx_order, input_idx_order = list(input_idx_order), fused = True)
        nconf.time_complexity = time_complexity
        nconf.memory_complexity = memory_complexity
        scheds.append(nconf)

    # The base condition
    if len(expr) <= 2:
        return scheds

    print("output:", output, "expr:", expr, "p_n: ", len(idx_perms), flush=True)
    for i in range(1, len(expr)):
        # Now break the expression into smaller ones
        pre_expr, post_expr = expr[:i], expr[i:]

        # get the list of schedules for pre and post expr
        # TODO - need to pass the output indexes to both sched_enum calls
        # since this is a sub module 
        pre_ind, post_ind = define_data_layout(output_idx_order, pre_expr, post_expr, tensor_accesses)

        pre_sched, post_sched = [], []
        sched_enum("_" + output, pre_expr, pre_ind, tensor_accesses, tensor_idx_order_constraints, pre_sched)
        sched_enum(output + "_", post_expr, post_ind, tensor_accesses, tensor_idx_order_constraints, post_sched)

        n_post_sched = len(post_sched)
        print("output:", output, str(output_idx_order), "expr:", expr, "sched_size", len(scheds), flush = True)
        print("creating fused and unfused schedules. pre_sched: ", len(pre_sched), " post_sched: ", len(post_sched), flush = True)
        # create all possible schedules
        for i, s1 in enumerate(pre_sched):
            for j, s2 in enumerate(post_sched):
                s1 = pre_sched[i]
                s2 = post_sched[j]
                # print("s1:", s1, "s2:", s2)
                if ((i * n_post_sched + j) % 10000 == 0): print(i, j, "s1:", s1, "s2:", s2, flush = True)
                # create unfused schedule
                # fused = False schedules are created here
                unfused(output, expr, output_idx_order, s1, s2, scheds)
                # scheds.extend(x)
                
                # TODO - add partially fused schedules
                # T1 = A*B and T2 = C | T1 = A and T2 = B*C
                # T1 or T2 has only one input, then we completely ignore it and generate the output loop order
                # this is not captured in unfused schedules because we always use intermediate tensors to save output
                # when the single input is sparse (even if it is dense), we can remove the intermediate tensor and save memory by directly using
                # the input to generate the output
                partially_fused()
                
                # create fused schedules
                # is it fusible?
                fused(output, expr, output_idx_order, s1, s2, True, scheds, tensor_idx_order_constraints) # s1 producer, s2 consumer
                # scheds.extend(y)
                fused(output, expr, output_idx_order, s2, s1, False, scheds, tensor_idx_order_constraints) # s2 producer, s1 consumer
                # scheds.extend(z)
        print("fused and unfused schedules created", flush = True)
    
    #return all schedules
    # return scheds


