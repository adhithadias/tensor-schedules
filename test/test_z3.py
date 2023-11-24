import pytest
from z3 import Int, Solver, sat, unsat
# from src.util import union_list, get_input_idx_list
from src.config import Config
from src.prune import prune_using_z3

def test_z3_expr1():
    i = Int('i')
    j = Int('j')
    k = Int('k')
    l = Int('l')
    m = Int('m')
    jpos = Int('jpos')
    
    s = Solver()
    
    # it seems like we always need to give both lower and upper bounds for all
    # the variables to make it solve faster
    s.add(i > 500)
    s.add(j > 500)
    s.add(i < 1500)
    s.add(j < 1500)
    # s.add(i == 10000)
    # s.add(j == 10000)
    # s.add(k == 64)
    s.add(k >= 8)
    s.add(k <= 256)
    # s.add(l == 64)
    s.add(l >= 8)
    s.add(l <= 256)
    # s.add(m == 64)
    s.add(m >= 8)
    s.add(m <= 256)
    s.add(jpos >= 0)
    # let's say the sparsity of the matrix is going to be between 0.01 and 0.001
    s.add(100*i*jpos < i*j)
    s.add(i*j < 1000*i*jpos)
    
    # print(s)
    # print(s.check())
    
    s.push()
    s.add(m*k*l + m*j*k + m*jpos*i < i*jpos*k*l*m)
    print(s)
    val = s.check()
    print(val)
    assert val == sat
    if val == sat: print(s.model())
    s.pop()
    
    # print(s)
    # print(s.check())
    
    s.push()
    s.add(i*jpos*k*l*m <= m*k*l + m*j*k + m*jpos*i)
    print(s)
    val = s.check()
    print(val)
    assert val == unsat
    if (val == sat): print(s.model())
    s.pop()
    
    # print(s)
    # print(s.check())
 
