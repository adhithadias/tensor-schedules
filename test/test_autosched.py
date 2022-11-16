import pytest
from src.autosched import unfused, fused
from src.config import Config

def test_autosched_unfused1():
    # B(j,k)*C(k,l)*D(l,m)
    expr = ['B','C','D']
    output_index_order = ['j','m']
    prod_config = Config(['B'], output_idx_order=['j','k'], input_idx_order=['j','k'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['m','l','k'],fused=True)

    scheds = unfused(expr, output_index_order, prod_config, cons_config)

    # output idx has 3 indices and there are 6 permutations
    # among them, so 6 schedules should be returned
    assert len(scheds) == 6

    for sched in scheds:
        assert ['j','m'] == sched.output_idx_order
        assert ['B','C','D'] == sched.expr
        assert False == sched.fused
        assert set(['j','k','m']) == set(sched.input_idx_order)


def test_autosched_unfused2():
    # A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config(['A','B'], output_idx_order=['i','k'], input_idx_order=['i','j','k'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['k','l','m'], fused=True)

    scheds = unfused(expr, output_index_order, prod_config, cons_config)

    # output idx has 3 indices and there are 6 permutations
    # among them, so 6 schedules should be returned
    assert len(scheds) == 6

    for sched in scheds:
        assert ['i','m'] == sched.output_idx_order
        assert ['A','B','C','D'] == sched.expr
        assert False == sched.fused
        assert set(['i','k','m']) == set(sched.input_idx_order)

def test_autosched_fused1():
    # X(j,m) = B(j,k)*C(k,l)*D(l,m)
    expr = ['B','C','D']
    output_index_order = ['j','m']
    prod_config = Config(['B'], output_idx_order=['j','k'], input_idx_order=['j','k'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['m','l','k'],fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['j', ['k'], ['m','l','k']] == sched.input_idx_order

def test_autosched_fused2():
    # X(j,m) = B(j,k)*C(k,l)*D(l,m)
    expr = ['B','C','D']
    output_index_order = ['j','m']
    prod_config = Config(['B'], output_idx_order=['j','k'], input_idx_order=['j','k'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['j', 'k', [], ['m','l']] == sched.input_idx_order

def test_autosched_fused3():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config(['A','B'], output_idx_order=['i','k'], input_idx_order=['i','j','k'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', ['j','k'], ['k','m','l']] == sched.input_idx_order

def test_autosched_fused4():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config(['A','B'], output_idx_order=['i','k'], input_idx_order=['i','k','j'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', 'k', ['j'], ['m','l']] == sched.input_idx_order


def test_autosched_fused4():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config(['A','B'], output_idx_order=['i','k'], input_idx_order=['k','i','j'], fused=True)
    cons_config = Config(['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 3
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['k', 'i', ['j'], ['m', 'l']] == sched.input_idx_order or['k', ['i', 'j'], ['m', 'i', 'l']] == sched.input_idx_order or ['k', ['i', 'j'], ['m', 'l', 'i']] == sched.input_idx_order

def test_autosched_fused5():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config(['A','B','C'], output_idx_order=['i','l'], input_idx_order=['i','j','k','l'], fused=True)
    cons_config = Config(['D'], output_idx_order=['l','m'], input_idx_order=['l','m'], fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', ['j','k','l'], ['l','m']] == sched.input_idx_order


def test_autosched_fused5():
    # X(i,l) = A(i,j)*B(j,k)*C(k,l)
    expr = ['A','B','C']
    output_index_order = ['i','l']
    prod_config0 = Config(['A','B'], output_idx_order=['i','k'], input_idx_order=['i','j','k'], fused=True)
    cons_config0 = Config(['C'], output_idx_order=['k','l'], input_idx_order=['k','l'], fused=True)

    scheds = fused(expr, output_index_order, prod_config0, cons_config0)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', ['j','k'], ['k','l']] == sched.input_idx_order


    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    # recursively using the previous fused schedule
    prod_config = scheds[0]
    cons_config = Config(['D'], output_idx_order=['l','m'], input_idx_order=['l','m'], fused=True)

    scheds = fused(expr, output_index_order, prod_config, cons_config)

    assert len(scheds) == 1
    for sched in scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', [['j','k'],['k','l']], ['l','m']] == sched.input_idx_order