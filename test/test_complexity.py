import pytest
from src.util import get_time_complexity
from src.config import Config

def test_time_complexity1():
    idx_perm = ['j', 'i', 'k', 'l', 'm']
    tensor_idx_order_constraints = {
        'A': [('j', 'i'), ('k','j'), ('k','i')], # A(i,j,k) is CSF so we pass in (j,i) here as a constraint
        'B': [],
        'C': [],
        'D': [],
        'X': []
    }
    input_tensors = ['A', 'B', 'C', 'D']
    output = 'X'
    
    time_complexity = get_time_complexity(idx_perm, input_tensors, tensor_idx_order_constraints)
    assert len(time_complexity) == 5
    assert 'j' in time_complexity and time_complexity['j'] == 1
    assert 'k' in time_complexity and time_complexity['k'] == 1
    assert 'i' in time_complexity and time_complexity['i'] == 0
    assert 'l' in time_complexity and time_complexity['l'] == 0
    assert 'm' in time_complexity and time_complexity['m'] == 0
    print(time_complexity)
    
    
def test_time_complexity2():
    idx_perm = ['j', 'i', 'k', 'l', 'm']
    tensor_idx_order_constraints = {
        'A': [('j', 'i')], # A(i,j,k) is CSF so we pass in (j,i) here as a constraint
        'B': [],
        'C': [],
        'D': [],
        'X': []
    }
    input_tensors = ['A', 'B', 'C', 'D']
    output = 'X'
    
    time_complexity = get_time_complexity(idx_perm, input_tensors, tensor_idx_order_constraints)
    assert len(time_complexity) == 5
    assert 'j' in time_complexity and time_complexity['j'] == 1
    assert 'k' in time_complexity and time_complexity['k'] == 0
    assert 'i' in time_complexity and time_complexity['i'] == 0
    assert 'l' in time_complexity and time_complexity['l'] == 0
    assert 'm' in time_complexity and time_complexity['m'] == 0
    print(time_complexity)

