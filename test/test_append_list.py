import pytest
from src.util import append_list_to_list_of_lists

def test_append_list():

    a = [['a', 'b'], ['a']]
    b = [['a'], [['a'], ['a', 'b']]]

    l = append_list_to_list_of_lists(a, b)

    print(l)


test_append_list()