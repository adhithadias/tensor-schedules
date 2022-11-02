from config import Config
			
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

# Schedule enumeration
# Input -> A tensor expression; Output -> list of configs
def sched_enum(expr):
    # Input is the expression or computation
    # This is something like [A, B, C, D]

    print(expr)

    # The base condition
    if len(expr) <= 2:
        return [Config(expr)]

    # Output is a list of schedule configs
    scheds = [Config(expr)]

    for i in range(1, len(expr)-1):
        # Now break the expression into smaller ones
        pre_expr, post_expr = expr[:i], expr[i:]
        print(pre_expr, post_expr)

        # get the list of schedules for pre and post expr
        pre_sched = sched_enum(pre_expr)
        post_sched = sched_enum(post_expr)

        # create all possible schedules
        for s1 in pre_sched:
            for s2 in post_sched:
                # create unfused schedule
                x = unfused(expr, s1, s2)
                scheds.append(x)
                # create fused schedules
                y = fused(expr, s1, s2) # s1 producer
                scheds.append(y)
                z = fused(expr, s2, s1) # s2 producer
                scheds.append(z)
    
    #return all schedules
    return scheds


