from config import Config
import itertools
			
# Producing a config of unfused schedules
# Input -> Two configs; Output -> One config
def unfused(expr, prod_config, cons_config):
    unfus = Config(expr)
    unfus.subconfig(prod_config, cons_config, False)
    return unfus
	
# Producing a config of fused schedules
# Input -> Two configs; Output -> One config
def fused(expr, prod_config, cons_config):
    fus = Config(expr)
    fus.subconfig(prod_config, cons_config, True)
    return fus

# TODO - proof reorder and tensor breakdown is equal to 
# tensor breakdown and reordering smaller tensor contractions

# TODO - we will use the 2nd method and give a proof in the paper
# that they cover the entirity of the scheduling space

# Schedule enumeration
# Input -> A tensor expression; Output -> list of configs
def sched_enum(expr, tensor_accesses):
    # Input is the expression or computation
    # This is something like [A, B, C, D]

    print(expr)
    # Output is a list of schedule configs
    idx_set = set()
        
    for tensor in expr:
        idxes = tensor_accesses[tensor]
        for idx in idxes:
            idx_set.add(idx)
        print(idxes)
    print('indices set:', idx_set)
    idx_set = list(idx_set)
    print('indices list:', idx_set)
    
    idx_perms = list(itertools.permutations(idx_set))
    print('permutation length:', len(idx_perms))
    print('permutations:', idx_perms)

    scheds = []
    for idx_perm in idx_perms:
        nconf = Config(expr)
        nconf.setidx(idx_perm)
        scheds.append(nconf)

    # The base condition
    if len(expr) <= 2:
        return scheds

    for i in range(1, len(expr)-1):
        # Now break the expression into smaller ones
        pre_expr, post_expr = expr[:i], expr[i:]
        print(pre_expr, post_expr)

        # get the list of schedules for pre and post expr
        pre_sched = sched_enum(pre_expr, tensor_accesses)
        post_sched = sched_enum(post_expr, tensor_accesses)

        # create all possible schedules
        for s1 in pre_sched:
            for s2 in post_sched:
                # create unfused schedule
                x = unfused(expr, s1, s2)
                scheds.append(x)
                # create fused schedules
                # is it fusible?
                y = fused(expr, s1, s2) # s1 producer
                scheds.append(y)
                z = fused(expr, s2, s1) # s2 producer
                scheds.append(z)
    
    #return all schedules
    return scheds


