import pytest
from src.util import get_idxes_in_config

def test_get_idx_in_config():
    l = ['j', ['k'], ['m', 'l', 'k']]
    s = get_idxes_in_config(l)

    assert s == set(['j','k','l','m'])