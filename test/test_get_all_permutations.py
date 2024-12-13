import pytest
from src.util import get_all_combinations, get_all_permutations

def test_get_all_combinations1():
    a = ['i']
    b = ['j', 'k', 'l']

    l = get_all_combinations(a, b)

    assert l == [
        ['i', 'j', 'k', 'l'], ['j', 'i', 'k', 'l'],
        ['j', 'k', 'i', 'l'], ['j', 'k', 'l', 'i']
    ]

def test_get_all_combinations2():
    a = ['i', 'j']
    b = ['k', 'l']

    l = get_all_combinations(a, b)

    assert l == [
        # ['i', 'k', 'l'], ['k', 'i', 'l'], ['k', 'l', 'i'] by the first loop
        ['j', 'i', 'k', 'l'], ['i', 'j', 'k', 'l'], ['i', 'k', 'j', 'l'], ['i', 'k', 'l', 'j'],
        ['j', 'k', 'i', 'l'], ['k', 'j', 'i', 'l'], ['k', 'i', 'j', 'l'], ['k', 'i', 'l', 'j'], 
        ['j', 'k', 'l', 'i'], ['k', 'j', 'l', 'i'], ['k', 'l', 'j', 'i'], ['k', 'l', 'i', 'j']
    ]


def test_get_all_permutations1():
    a = ['i']
    b = ['j', 'k', 'l']

    l = get_all_permutations(a, b)

    assert l == [
        ['i', 'j', 'k', 'l'], ['j', 'i', 'k', 'l'],
        ['j', 'k', 'i', 'l'], ['j', 'k', 'l', 'i']
    ]
