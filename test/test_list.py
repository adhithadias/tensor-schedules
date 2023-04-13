import pytest
from src.util import union_list, get_input_idx_list

def test_union_list():
    print()
    l1 = ['a','b','c']
    l2 = ['b','c','d']

    u = union_list(l1,l2)
    print(u)

    assert ['a', 'b', 'c', 'd'] == u


def test_get_input_idx_set():
    accesses = {
        'X': ('i', 'm'),
        'A': ('i', 'j'),
        'B': ('j', 'k'),
        'C': ('k', 'l'),
        'D': ('l', 'm')
    }

    l = get_input_idx_list(['A','B','C','D'], accesses)
    assert set(l) == set(['i','j','k','l','m'])
