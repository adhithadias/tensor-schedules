import pytest
from z3 import Int, Solver, sat, unsat, And, Or, Not
from src.config import Config
from src.prune import prune_using_depth, prune_using_z3, get_time_memory_z3_complexity, get_z3_complexity

def test_depth_prune():
    
    # A(i,l) = B(i,j)*C(i,k)*D(j,k)*E(j,l) , fsd: True, pol: True | lp_ord: ['i', 'j', ['k'], ['l']] | {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []} , []
    schedule1 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', ['k'], ['l']], fused = True, prod_on_left = True)
    schedule1.time_complexity = {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []}
    schedule1.memory_complexity = []
    
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m) , fused: True, pol: None | loop_order: ['k', 'm', 'i', 'j', 'l'] | [{'jpos', 'k', 'm', 'i', 'l'}] , []
    schedule2 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', 'k', 'l'], fused = True, prod_on_left = True)
    schedule2.time_complexity = {'r': [{'k', 'i', 'jpos', 'l'}], 'a': []}
    schedule2.memory_complexity = []
    
    schedules = [schedule1, schedule2]
    
    pruned_schedules = prune_using_depth(schedules)
    
    assert len(pruned_schedules) == 1
    assert schedule1 == pruned_schedules[0]
    
def test_get_time_memory_z3_complexity():
    i = Int('i')
    j = Int('j')
    k = Int('k')
    l = Int('l')
    m = Int('m')
    jpos = Int('jpos')
    z3_variables = {'i': i, 'j': j, 'k': k, 'l': l, 'm': m, 'jpos': jpos}
    
    s1_time_complexity = {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []}
    s1_memory_complexity = []
    
    s2_time_complexity = {'r': [{'k', 'i', 'jpos', 'l'}], 'a': []}
    s2_memory_complexity = []
    
    (s1_z3_time, s1_z3_memory) = get_time_memory_z3_complexity(s1_time_complexity, s1_memory_complexity, z3_variables)
    
    s = Solver()
    
    s.push()
    s.add(i*k*jpos + l*i*jpos == s1_z3_time)
    s.add(s1_z3_memory == 0)
    print(s)
    val = s.check()
    assert val == sat
    print(val)
    s.pop()
    
    s.push()
    s.add(i*jpos*k*l == s1_z3_time)
    s.add(s1_z3_memory == 0)
    print(s)
    val = s.check()
    assert val == sat
    print(val)
    s.pop()
    
def test_get_complexity():
    i = Int('i')
    j = Int('j')
    k = Int('k')
    l = Int('l')
    m = Int('m')
    jpos = Int('jpos')
    z3_variables = {'i': i, 'j': j, 'k': k, 'l': l, 'm': m, 'jpos': jpos}

    # A(i,l) = B(i,j)*C(i,k)*D(j,k)*E(j,l) , fsd: True, pol: True | lp_ord: ['i', 'j', ['k'], ['l']] | {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []} , []
    schedule1 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', ['k'], ['l']], fused = True, prod_on_left = True)
    schedule1.time_complexity = {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []}
    schedule1.memory_complexity = []
    
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m) , fused: True, pol: None | loop_order: ['k', 'm', 'i', 'j', 'l'] | [{'jpos', 'k', 'm', 'i', 'l'}] , []
    schedule2 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', 'k', 'l'], fused = True, prod_on_left = True)
    schedule2.time_complexity = {'r': [{'k', 'i', 'jpos', 'l'}], 'a': []}
    schedule2.memory_complexity = []
    
    (s1_z3_time, s1_z3_memory) = get_z3_complexity(schedule1, z3_variables)
    
    s = Solver()
    
    s.push()
    s.add(i*k*jpos + l*i*jpos == s1_z3_time)
    s.add(s1_z3_memory == 0)
    print(s)
    val = s.check()
    assert val == sat
    print(val)
    s.pop()
    
    s.push()
    s.add(i*jpos*k*l == s1_z3_time)
    s.add(s1_z3_memory == 0)
    print(s)
    val = s.check()
    assert val == sat
    print(val)
    s.pop()
    
def test_check_same_schedule_for_unsat():
    i = Int('i')
    j = Int('j')
    k = Int('k')
    l = Int('l')
    m = Int('m')
    jpos = Int('jpos')
    z3_variables = {'i': i, 'j': j, 'k': k, 'l': l, 'm': m, 'jpos': jpos}

    # A(i,l) = B(i,j)*C(i,k)*D(j,k)*E(j,l) , fsd: True, pol: True | lp_ord: ['i', 'j', ['k'], ['l']] | {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []} , []
    schedule1 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', ['k'], ['l']], fused = True, prod_on_left = True)
    schedule1.time_complexity = {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []}
    schedule1.memory_complexity = []
    
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m) , fused: True, pol: None | loop_order: ['k', 'm', 'i', 'j', 'l'] | [{'jpos', 'k', 'm', 'i', 'l'}] , []
    schedule2 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', ['k'], ['l']], fused = True, prod_on_left = True)
    schedule2.time_complexity = {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []}
    schedule2.memory_complexity = []
    
    (s1_z3_time, s1_z3_memory) = get_z3_complexity(schedule1, z3_variables)
    (s2_z3_time, s2_z3_memory) = get_z3_complexity(schedule2, z3_variables)
    
    s = Solver()
    
    c1 = s1_z3_time >= s2_z3_time
    c2 = s1_z3_memory > s2_z3_memory
    c3 = s1_z3_time > s2_z3_time
    c4 = s1_z3_memory >= s2_z3_memory
    
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
    
    assert condition == unsat
    assert inverse_condition == unsat
    

def test_z3_prune():
    i = Int('i')
    j = Int('j')
    k = Int('k')
    l = Int('l')
    m = Int('m')
    jpos = Int('jpos')

    z3_variables = {'i': i, 'j': j, 'k': k, 'l': l, 'm': m, 'jpos': jpos}
    z3_constraints = [i >= 5000, i <= 15000, j >= 5000, j <= 15000, 
                    k >= 8, k <= 256, l >= 8, l <= 256, jpos >= 0,
                    100 * i * jpos < i * j,   # i*jpos < 0.01 * i*j
                    i * j < 1000 * i * jpos]  # 0.001 * i*j < i*jpos
    # can pass additional constraints here like limit additional memory
    
    # A(i,l) = B(i,j)*C(i,k)*D(j,k)*E(j,l) , fsd: True, pol: True | lp_ord: ['i', 'j', ['k'], ['l']] | {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []} , []
    schedule1 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', ['k'], ['l']], fused = True, prod_on_left = True)
    schedule1.time_complexity = {'r': [{'k', 'i', 'jpos'}, {'l', 'i', 'jpos'}], 'a': []}
    schedule1.memory_complexity = []
    
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m) , fused: True, pol: None | loop_order: ['k', 'm', 'i', 'j', 'l'] | [{'jpos', 'k', 'm', 'i', 'l'}] , []
    schedule2 = Config('A', ['B','C', 'D', 'E'], output_idx_order = ['i','l'], input_idx_order = ['i', 'j', 'k', 'l'], fused = True, prod_on_left = True)
    schedule2.time_complexity = {'r': [{'k', 'i', 'jpos', 'l'}], 'a': []}
    schedule2.memory_complexity = []
    
    schedules = [schedule1, schedule2]
    
    prune_using_z3(schedules, z3_variables, z3_constraints)