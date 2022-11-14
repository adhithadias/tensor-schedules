import pytest
from src.util import copy_and_insert

def test_copy_and_insert():
    print()
    a = [[1, 10, 3], [4, 5, 6]]
    b = copy_and_insert(a, 0, 1)

    print(a)
    print(b)

    assert b == [1, [1, 10, 3], [4, 5, 6]]