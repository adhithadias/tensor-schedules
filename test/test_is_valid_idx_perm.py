import pytest
import itertools
from src.util import is_valid_idx_perm

def test_check_is_valid_idx_perm():
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

    assert is_valid_idx_perm(['j', 'i', 'k', 'l', 'm'], tensor_idx_order_constraints, input_tensors, output) == False

    assert is_valid_idx_perm(['k', 'i', 'j', 'l', 'm'], tensor_idx_order_constraints, input_tensors, output) == False

def test_permute_idx_valid_count():
    idx = ['i', 'j', 'k']
    tensor_idx_order_constraints = {
        'A': [('j', 'i')], # A(i,j,k) is CSF so we pass in (j,i) here as a constraint
        'B': [],
        'C': [],
        'D': [],
        'X': []
    }
    input_tensors = ['A', 'B', 'C', 'D']
    output = 'X'

    perms = list(itertools.permutations(idx))
    assert len(perms) == 6

    valid_count = 0
    for perm in perms:
        if (is_valid_idx_perm(perm, tensor_idx_order_constraints, input_tensors, output)):
            valid_count += 1

    assert valid_count == 3