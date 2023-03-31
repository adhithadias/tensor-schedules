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
    assert 'jpos' in time_complexity
    assert 'kpos' in time_complexity
    assert 'i' in time_complexity
    assert 'l' in time_complexity
    assert 'm' in time_complexity
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
    assert 'jpos' in time_complexity
    assert 'k' in time_complexity
    assert 'i' in time_complexity
    assert 'l' in time_complexity
    assert 'm' in time_complexity
    print(time_complexity)

