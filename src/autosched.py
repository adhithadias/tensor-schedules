from src.config import Config
from src.util import *
import itertools
			
# Producing a config of unfused schedules
# Input -> Two configs; Output -> One config
def unfused(expr, output_index_order, prod_config, cons_config):
    '''
    get prod_config.output_idx_order and cons_config.output_idx_order
    prod_config.output_idx_order * cons_config.output_idx_order defines 
    the input_idx_order for unfused schedules
    '''
    prod_output_idx_order = prod_config.output_idx_order
    cons_output_idx_order = cons_config.output_idx_order
    idxes = list(set(prod_output_idx_order) | set(cons_output_idx_order))
    idx_perms = list(itertools.permutations(idxes))

    unfused_schedules = []
    for idx_perm in idx_perms:
        unfus = Config(expr, output_idx_order = output_index_order, input_idx_order = idx_perm, fused = False)
        unfus.subconfig(prod_config, cons_config, False)
        unfused_schedules.append(unfus)
    return unfused_schedules
	
# Producing a config of fused schedules
# Input -> Two configs; Output -> One config
def fused(expr, output_idx_order, prod_config, cons_config):
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
    linear_list, post_list = get_idxes_up_to_branching_point(cons_config.input_idx_order)
    perms = get_all_permutations(idx_only_in_output, linear_list)
    perms = append_list_to_list_of_lists(perms, post_list)

    fused_scheds = []

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
        if not common_loops_found: continue 

        # break doesn't increase the i count while continue does increase
        # handle the case where there are no common indices added i+=1
        # to the break case and splicing the arrays at i-1 location

        common_loops = prod_config.input_idx_order[:i-1]
        prod_loops = prod_config.input_idx_order[i-1:]
        cons_loops = cons_order[i-1:]

        in_idx_order = []
        in_idx_order.extend(common_loops)
        in_idx_order.extend([prod_loops, cons_loops])

        fus = Config(expr, output_idx_order = output_idx_order, input_idx_order = in_idx_order, fused = True)
        fus.subconfig(prod_config, cons_config, True)
        fused_scheds.append(fus)

    return fused_scheds


# TODO (paper) - proof reorder and tensor breakdown is equal to 
# tensor breakdown and reordering smaller tensor contractions

# TODO (paper) - we will use the 2nd method and give a proof in the paper
# that they cover the entirity of the scheduling space

# Schedule enumeration
# Input -> A tensor expression; Output -> list of configs
def sched_enum(expr, output_idx_order, tensor_accesses):
    # Input is the expression or computation
    # This is something like [A, B, C, D]

    # Output is a list of schedule configs
    idx_set = get_input_idx_list(expr, tensor_accesses)
    idx_perms = list(itertools.permutations(idx_set))

    scheds = []
    for input_idx_order in idx_perms:
        nconf = Config(expr, output_idx_order = output_idx_order, input_idx_order = list(input_idx_order), fused = True)
        scheds.append(nconf)

    # The base condition
    if len(expr) <= 2:
        return scheds

    for i in range(1, len(expr)):
        # Now break the expression into smaller ones
        pre_expr, post_expr = expr[:i], expr[i:]

        # get the list of schedules for pre and post expr
        # TODO - need to pass the output indexes to both sched_enum calls
        # since this is a sub module 
        pre_ind, post_ind = define_data_layout(output_idx_order, pre_expr, post_expr, tensor_accesses)

        pre_sched = sched_enum(pre_expr, pre_ind, tensor_accesses)
        post_sched = sched_enum(post_expr, post_ind, tensor_accesses)

        # create all possible schedules
        for s1 in pre_sched:
            for s2 in post_sched:
                # create unfused schedule
                x = unfused(expr, output_idx_order, s1, s2)
                scheds.extend(x)
                
                # create fused schedules
                # is it fusible?
                y = fused(expr, output_idx_order, s1, s2) # s1 producer, s2 consumer
                scheds.extend(y)
                z = fused(expr, output_idx_order, s2, s1) # s2 producer, s1 consumer
                scheds.extend(z)
    
    #return all schedules
    return scheds


