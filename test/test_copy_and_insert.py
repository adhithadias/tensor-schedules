import pytest
from src.util import copy_and_insert, deepcopy_and_insert

def test_copy_and_insert():
    a = [[1, 10, 3], [4, 5, 6]]
    b = copy_and_insert(a, 0, 1)

    assert b == [1, [1, 10, 3], [4, 5, 6]]
    a[0][1] = 100
    assert b == [1, [1, 100, 3], [4, 5, 6]]


def test_deepcopy_and_insert():
    a = [[1, 10, 3], [4, 5, 6]]
    b = deepcopy_and_insert(a, 0, 1)

    assert b == [1, [1, 10, 3], [4, 5, 6]]
    a[0][1] = 100
    assert b == [1, [1, 10, 3], [4, 5, 6]]