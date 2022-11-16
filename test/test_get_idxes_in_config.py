import pytest
from src.util import get_idxes_in_config, get_idxes_up_to_branching_point

def test_get_idx_in_config():
    l = ['j', ['k'], ['m', 'l', 'k']]
    s = get_idxes_in_config(l)

    assert s == set(['j','k','l','m'])


def test_get_idxes_up_to_branching_point1():
    l = ['m','l','k']
    l_linear, l_branched = get_idxes_up_to_branching_point(l)
    assert l == l_linear
    assert [] == l_branched

def test_get_idxes_up_to_branching_point2():
    l = ['m','l',['k']]
    l_linear, l_branched = get_idxes_up_to_branching_point(l)
    assert ['m','l'] == l_linear
    assert [['k']] == l_branched

def test_get_idxes_up_to_branching_point3():
    l = ['m',[]]
    l_linear, l_branched = get_idxes_up_to_branching_point(l)
    assert ['m'] == l_linear
    assert [[]] == l_branched

def test_get_idxes_up_to_branching_point4():
    l = ['m',[],[]]
    l_linear, l_branched = get_idxes_up_to_branching_point(l)
    assert ['m'] == l_linear
    assert [[],[]] == l_branched