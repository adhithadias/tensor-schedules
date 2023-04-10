import pytest
from src.autosched import define_data_layout

def test_checkdl():
    print()
    accesses = {
        'X': ['i', 'm'],
        'A': ['i', 'j'],
        'B': ['j', 'k'],
        'C': ['k', 'l'],
        'D': ['l', 'm']
    }

    pre_expr = ['A']
    post_expr = ['B','C','D']
    pre_inds, post_inds = define_data_layout(accesses['X'], pre_expr, post_expr, accesses)
    assert set(['i','j']) == set(pre_inds)
    assert set(['j','m']) == set(post_inds)

    pre_expr = ['A','B']
    post_expr = ['C','D']
    pre_inds, post_inds = define_data_layout(accesses['X'], pre_expr, post_expr, accesses)
    assert set(['i','k']) == set(pre_inds)
    assert set(['k','m']) == set(post_inds)

    pre_expr = ['A','B','C']
    post_expr = ['D']
    pre_inds, post_inds = define_data_layout(accesses['X'], pre_expr, post_expr, accesses)
    assert set(['i','l']) == set(pre_inds)
    assert set(['l','m']) == set(post_inds)
    
    
def test_check_data_layout():
    print()
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    accesses = {
        'A': ['l', 'm', 'n'],
        'B': ['i', 'j', 'k'],
        'C': ['i', 'l'],
        'D': ['j', 'm'],
        'E': ['k', 'n']
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    pre_expr = ['B', 'C']
    post_expr = ['D', 'E']
    pre_inds, post_inds = define_data_layout(accesses['A'], pre_expr, post_expr, accesses)
    assert set(['l', 'j', 'k']) == set(pre_inds)
    assert set(['j', 'k', 'm', 'n']) == set(post_inds)
    
    pre_expr = ['D']
    post_expr = ['E']
    pre_inds, post_inds = define_data_layout(['j', 'k', 'm', 'n'], pre_expr, post_expr, accesses)
    assert set(['j','m']) == set(pre_inds)
    assert set(['k','n']) == set(post_inds)

    # TODO check if these indices population is correct
    pre_expr = ['B']
    post_expr = ['C','D','E']
    pre_inds, post_inds = define_data_layout(accesses['A'], pre_expr, post_expr, accesses)
    assert set(['i', 'j', 'k']) == set(pre_inds)
    assert set(['i', 'j', 'k', 'l', 'm', 'n']) == set(post_inds)

    # TODO check if these indices population is correct
    pre_expr = ['B','C','D']
    post_expr = ['E']
    pre_inds, post_inds = define_data_layout(accesses['A'], pre_expr, post_expr, accesses)   
    assert set(['l', 'm', 'k']) == set(pre_inds)
    assert set(['k', 'n']) == set(post_inds)

