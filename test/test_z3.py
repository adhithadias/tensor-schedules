import pytest
from z3 import *
# from src.util import union_list, get_input_idx_list

def test_z3_expr1():
    i = Int('i')
    j = Int('j')
    k = Int('k')
    l = Int('l')
    m = Int('m')
    jpos = Int('jpos')
    
    s = Solver()
    
    s.add(i > 10)
    s.add(j > 10)
    s.add(k > 10)
    s.add(l > 10)
    s.add(m == 10)
    # s.add(i < 100)
    # s.add(j < 100)
    # s.add(k < 100)
    # s.add(l < 100)
    # s.add(m < 100)
    s.add(jpos >= 0)
    s.add(jpos < j)
    
    # print(s)
    # print(s.check())
    
    s.push()
    s.add(m*k*l + m*j*k + m*jpos*i < i*jpos*k*l*m)
    print(s)
    print(s.check())
    print(s.model())
    s.pop()
    
    # print(s)
    # print(s.check())
    
    s.push()
    s.add(i*jpos*k*l*m < m*k*l + m*j*k + m*jpos*i)
    print(s)
    val = s.check()
    print(val)
    # if (val == Z3_L_TRUE):
    print(s.model())
    # print(s.model())
    s.pop()
    
    # print(s)
    # print(s.check())
 