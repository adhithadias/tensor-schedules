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

