from bitarray import bitarray
from functools import reduce
from z3 import Solver, And, Or, Not, sat, unsat
from src.config import Config


def get_loop_depth(schedule : Config) -> int :
    
    assert type(schedule.time_complexity['r']) == list
    assert type(schedule.time_complexity['a']) == list
    max_ : int = 0
    for complexity in schedule.time_complexity['r']:
        if (len(complexity) > max_) : max_ = len(complexity)
    
    for complexity in schedule.time_complexity['a']:
        if (len(complexity) > max_) : max_ = len(complexity)

    return max_

def get_mem_depth(memory_complexity : list) -> int :
    # assert type(memory_complexity) == list
    max_ : int = 0
    for complexity in memory_complexity:
        if (len(complexity) > max_) : max_ = len(complexity)
    
    return max_

def get_memory_depth(schedule : Config) -> int :
    
    assert type(schedule.memory_complexity) == list
    max_ : int = 0
    for complexity in schedule.memory_complexity:
        if (len(complexity) > max_) : max_ = len(complexity)
    
    return max_

def prune_using_depth(schedules : list) -> list:
    results = []
    complexities = set()
    pruned_array = bitarray(len(schedules))
    pruned_array.setall(0)
    
    n = len(schedules)
    
    for i, s1 in enumerate(schedules):
        
        if (pruned_array[i]):
            continue
        
        s1_time_depth = get_loop_depth(s1)
        s1_memory_depth = get_memory_depth(s1)
        
        # we have seen the same complexities before
        if (s1_time_depth, s1_memory_depth) in complexities:
            results.append(s1)
            continue
        
        for j, s2 in enumerate(schedules):
            
            if ((i * n + j) % 100000 == 0): print(i, j, s1, s2, flush = True)
            
            if (pruned_array[j]):
                continue
            
            s2_time_depth = get_loop_depth(s2)
            s2_memory_depth = get_memory_depth(s2)
            
            # s2 schedule is better than s1 schedule, we can prune s1 schedule
            if ((s1_time_depth >= s2_time_depth and s1_memory_depth > s2_memory_depth)
                or
                (s1_time_depth > s2_time_depth and s1_memory_depth >= s2_memory_depth)):
                pruned_array[i] = True
                break
            
            # s1 schedule is better than s2 schedule, we can prune s2 schedule
            if ((s1_time_depth <= s2_time_depth and s1_memory_depth < s2_memory_depth)
                or
                (s1_time_depth < s2_time_depth and s1_memory_depth <= s2_memory_depth)):
                pruned_array[j] = True
                continue
            
        if (not pruned_array[i]):
            results.append(s1)
            complexities.add((s1_time_depth, s1_memory_depth))
            
    return results

def prune_using_memory_depth(schedules : set, memory_depth_thresh : int) -> list:
    n = len(schedules)
    print('pruninng', n, 'schedules using memory depth', memory_depth_thresh, flush = True)
    results = []
    
    for i, s1 in enumerate(schedules):
        s1_memory_depth = get_memory_depth(s1)
        
        if (s1_memory_depth > memory_depth_thresh):
            continue
        
        results.append(s1)
        
    print('pruned', n - len(results), 'schedules', flush = True)
    return results

            
def get_time_memory_z3_complexity(time_complexity : list, memory_complexity : list, z3_variables : dict) -> tuple:
    
    tc0 = reduce(lambda x,y: x + y, [reduce(lambda x,y: x * y, [z3_variables[idx + 'pos'*setc[idx]] for idx in setc.keys()], 1) for setc in time_complexity['r']], 0)
    tc1 = reduce(lambda x,y: x + y, [reduce(lambda x,y: x * y, [z3_variables[idx + 'pos'*setc[idx]] for idx in setc.keys()], 1) for setc in time_complexity['a']], 0)
    tc = tc0 + tc1
        
    mc = reduce(lambda x,y: x + y, [reduce(lambda x,y: x * y, [z3_variables[idx] for idx in setc], 1) for setc in memory_complexity], 0)
    
    return (tc, mc)

def get_z3_complexity(config : Config, z3_variables : dict) -> tuple:
    if (config.z3_time_complexity is not None): return (config.z3_time_complexity, config.z3_memory_complexity)
    
    (t, m) = get_time_memory_z3_complexity(config.time_complexity, config.memory_complexity, z3_variables)
    config.z3_time_complexity = t
    config.z3_memory_complexity = m
    return (t,m)
    

def prune_using_z3(schedules : list, z3_variables : dict, z3_constraints : list) -> list:
    s = Solver()
    
    for constraint in z3_constraints:
        s.add(constraint)
        
    n = len(schedules)
        
    results = []
    pruned_array = bitarray(n)
    pruned_array.setall(0)
    
    for i, s1 in enumerate(schedules):
        if (pruned_array[i]):
            continue
        
        # s1 = schedules[i]
        (s1_time_complexity, s1_memory_complexity) = get_z3_complexity(s1, z3_variables)
        
        for j, s2 in enumerate(schedules):
            
            if ((i * n + j) % 1000 == 0): print(i, j, s1, s2, flush = True)
            
            if (pruned_array[j]):
                continue
    
            # s2 = schedules[i]
            (s2_time_complexity, s2_memory_complexity) = get_z3_complexity(s2, z3_variables)
            
            c1 = s1_time_complexity >= s2_time_complexity
            c2 = s1_memory_complexity > s2_memory_complexity
            c3 = s1_time_complexity > s2_time_complexity
            c4 = s1_memory_complexity >= s2_memory_complexity
            
            s.push()
            s.add(Or(And(c1, c2), And(c3, c4)))
            condition = s.check() # this should be sat to remove s1
            # if this is sat, it means that s1 is worse than s2, we can possibly remove s1
            # there is a indices values set such that s2 is better than s1
            s.pop()
            
            s.push()
            s.add(Or(And(Not(c1), Not(c2)), And(Not(c3), Not(c4))))
            # is there a set of values for indices such that s2 is worse that s1?
            # if this returns unsat, it means that for all values of indices, s2 is better than s1
            # then we can remove s1 for sure
            inverse_condition = s.check() # this should be unsat to remove s1
            s.pop()
            
            # if conditon is sat and inverse_condition is sat, we cannot remove s1, because there is a set of values for indices such that s1 is better than s2
            # and another set of values for indices such that s2 is better than s1
            
            # if condition is unsat and inverse_condition is unsat, it means both of them are equal (equally good)
            
            # if condition is sat and inverse_condition is unsat, it means that s1 is worse than s2, we can remove s1
            if (condition == sat and inverse_condition == unsat):
                pruned_array[i] = True
                break
            
            # if condition is unsat and inverse_condition is sat, it means that s2 is worse than s1, we can remove s2
            if (condition == unsat and inverse_condition == sat):
                pruned_array[j] = True
                continue

        if (not pruned_array[i]):
            results.append(schedules[i])
            
    return results
        
def compute_time_complexity_runtime(expressions, dimensions=dict):
    add_expr = 0
        
    for expression in expressions:
        mult_expr = 0
        for inner_expr in expression:
            # new_expr = None
            # if type(inner_expr) == str:
            #     new_expr = self.total_indices["all"][inner_expr]
            # else:
            new_expr = dimensions[inner_expr]
                
            if mult_expr == 0: mult_expr = new_expr
            else: mult_expr = mult_expr * new_expr
        add_expr += mult_expr
    
    return add_expr


def prune_time_runtime(schedule_list=list, dimensions=dict):
    result_array = []
    pruned_array = bitarray(len(schedule_list))
    pruned_array.setall(0)
    
    for group_num1, group1 in enumerate(schedule_list):
        if pruned_array[group_num1]: continue
        config1_loops = []
        
        # get groups of expressions for group 1
        for expr in (group1[0].time_complexity['r'] + group1[0].time_complexity['a']):
            config1_loops.append([key for key in expr.keys()])
        group1_time = compute_time_complexity_runtime(config1_loops, dimensions)
        
        for group_num2, group2 in enumerate(schedule_list):
            if group_num1 == group_num2: continue
            if pruned_array[group_num2]: continue
            config2_loops = []
            for expr in (group2[0].time_complexity['r'] + group2[0].time_complexity['a']):
                config2_loops.append([key for key in expr.keys()])
            group2_time = compute_time_complexity_runtime(config2_loops, dimensions)
            
            if group1_time > group2_time: pruned_array[group_num1] = 1
            elif group1_time < group2_time: pruned_array[group_num2] = 1
            
        if (not pruned_array[group_num1]):
            result_array.append(group1)
    
    return result_array