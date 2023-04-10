import pytest
from src.autosched import unfused, fused, sched_enum, get_schedules, get_schedules_unfused
from src.visitor import PrintConfigVisitor
from src.config import Config
from src.util import define_data_layout

def test_autoschedule1():
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    
    accesses = {
        'A': ('l', 'm', 'n'),
        'B': ('i', 'j', 'k'),
        'C': ('i', 'l'),
        'D': ('j', 'm'),
        'E': ('k', 'n')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    results = []
    output = 'A'
    expr = ('B', 'C', 'D','E')
    output_idx_order = ['j','k','m','n']
    
    results = get_schedules_unfused('A', ('l','m','n'), expr, accesses, ('i','j','k','l','m','n'), tensor_idx_order_constraints, 0, len(expr), 1)
    print('number of all the results:', len(results))
    printer = PrintConfigVisitor(accesses)
    # for i, schedule in enumerate(results):
    #     # if ('l' in schedule.input_idx_order and ('j','k','m','n') in schedule.input_idx_order):
    #     #     schedule.accept(printer)
    #     #     print('-----------')
    #     # if ('l' in schedule.input_idx_order and ('i','j','k') in schedule.input_idx_order):
    #     #     schedule.accept(printer)
    #     #     print('-----------')
    #     schedule.accept(printer)
    #     # if i % 1000 == 0:
    #     #     schedule.accept(printer)
    #     #     print('-----------')


def test_autoschedule():
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    
    accesses = {
        'A': ('l', 'm', 'n'),
        'B': ('i', 'j', 'k'),
        'C': ('i', 'l'),
        'D': ('j', 'm'),
        'E': ('k', 'n')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    results = []
    output = 'A'
    expr = ('B', 'C', 'D','E')
    output_idx_order = ['j','k','m','n']
    
    results = get_schedules('A', ('l','m','n'), expr, accesses, ('i','j','k','l','m','n'), tensor_idx_order_constraints, 0, len(expr), 1)
    print('number of all the fused results:', len(results))
    printer = PrintConfigVisitor(accesses)
    # for i, schedule in enumerate(results):
    #     if ('l' in schedule.input_idx_order and ('j','k','m','n') in schedule.input_idx_order):
    #         schedule.accept(printer)
    #         print('-----------')
    #     if ('l' in schedule.input_idx_order and ('i','j','k') in schedule.input_idx_order):
    #         schedule.accept(printer)
    #         print('-----------')
    #     # schedule.accept(printer)
    #     # if i % 1000 == 0:
    #     #     schedule.accept(printer)
    #     #     print('-----------')

def test_autosched1():
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    
    accesses = {
        'A': ('l', 'm', 'n'),
        'B': ('i', 'j', 'k'),
        'C': ('i', 'l'),
        'D': ('j', 'm'),
        'E': ('k', 'n')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    results = []
    output = 'A_'
    expr = ['D','E']
    output_idx_order = ['j','k','m','n']
    sched_enum(output, expr, output_idx_order, accesses, tensor_idx_order_constraints, results)
    
    print('number of configs:', len(results))
    
    printer = PrintConfigVisitor(accesses)
    for schedule in results:
        schedule.accept(printer)
        print('-----------')
        
    for i in range(1, len(expr)):
        # Now break the expression into smaller ones
        pre_expr, post_expr = expr[:i], expr[i:]
        print('pre_expr:', pre_expr, 'post_expr:', post_expr)
        
        pre_ind, post_ind = define_data_layout(output_idx_order, pre_expr, post_expr, accesses)
        
        print('pre_ind:', pre_ind, 'post_ind:', post_ind)
        
        pre_sched, post_sched = [], []
        sched_enum("_" + output, pre_expr, pre_ind, accesses, tensor_idx_order_constraints, pre_sched)
        sched_enum(output + "_", post_expr, post_ind, accesses, tensor_idx_order_constraints, post_sched)
        
        print('pre_sched_len:', len(pre_sched), 'post_sched_len:', len(post_sched))
        
        for schedule in pre_sched:
            schedule.accept(printer)
            print('-----------')
            
        for schedule in post_sched:
            schedule.accept(printer)
            print('-----------')
    

def test_autosched_unfused1():
    # B(j,k)*C(k,l)*D(l,m)
    expr = ['B','C','D']
    output_index_order = ['j','m']
    prod_config = Config('_X', ['B'], output_idx_order=['j','k'], input_idx_order=['j','k'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['m','l','k'],fused=True)

    unfused_scheds = []
    unfused('X', expr, output_index_order, prod_config, cons_config, unfused_scheds)

    # output idx has 3 indices and there are 6 permutations
    # among them, so 6 schedules should be returned
    assert len(unfused_scheds) == 6

    for sched in unfused_scheds:
        assert ['j','m'] == sched.output_idx_order
        assert ['B','C','D'] == sched.expr
        assert False == sched.fused
        assert set(['j','k','m']) == set(sched.input_idx_order)


def test_autosched_unfused2():
    # A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config('_X', ['A','B'], output_idx_order=['i','k'], input_idx_order=['i','j','k'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['k','l','m'], fused=True)

    unfused_scheds = []
    unfused('X', expr, output_index_order, prod_config, cons_config, unfused_scheds)

    # output idx has 3 indices and there are 6 permutations
    # among them, so 6 schedules should be returned
    assert len(unfused_scheds) == 6

    for sched in unfused_scheds:
        assert ['i','m'] == sched.output_idx_order
        assert ['A','B','C','D'] == sched.expr
        assert False == sched.fused
        assert set(['i','k','m']) == set(sched.input_idx_order)

def test_autosched_fused1():
    # X(j,m) = B(j,k)*C(k,l)*D(l,m)
    expr = ['B','C','D']
    output_index_order = ['j','m']
    prod_config = Config('_X', ['B'], output_idx_order=['j','k'], input_idx_order=['j','k'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['m','l','k'],fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['j', ['k'], ['m','l','k']] == sched.input_idx_order

def test_autosched_fused2():
    # X(j,m) = B(j,k)*C(k,l)*D(l,m)
    expr = ['B','C','D']
    output_index_order = ['j','m']
    prod_config = Config('_X', ['B'], output_idx_order=['j','k'], input_idx_order=['j','k'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['j', 'k', [], ['m','l']] == sched.input_idx_order

def test_autosched_fused3():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config('_X', ['A','B'], output_idx_order=['i','k'], input_idx_order=['i','j','k'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', ['j','k'], ['k','m','l']] == sched.input_idx_order

def test_autosched_fused4():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config('_X', ['A','B'], output_idx_order=['i','k'], input_idx_order=['i','k','j'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', 'k', ['j'], ['m','l']] == sched.input_idx_order


def test_autosched_fused4():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config('_X', ['A','B'], output_idx_order=['i','k'], input_idx_order=['k','i','j'], fused=True)
    cons_config = Config('X_', ['C','D'], output_idx_order=['k','m'], input_idx_order=['k','m','l'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 3
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['k', 'i', ['j'], ['m', 'l']] == sched.input_idx_order or['k', ['i', 'j'], ['m', 'i', 'l']] == sched.input_idx_order or ['k', ['i', 'j'], ['m', 'l', 'i']] == sched.input_idx_order

def test_autosched_fused5():
    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    prod_config = Config('_X', ['A','B','C'], output_idx_order=['i','l'], input_idx_order=['i','j','k','l'], fused=True)
    cons_config = Config('X_', ['D'], output_idx_order=['l','m'], input_idx_order=['l','m'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', ['j','k','l'], ['l','m']] == sched.input_idx_order


def test_autosched_fused5():
    # X(i,l) = A(i,j)*B(j,k)*C(k,l)
    expr = ['A','B','C']
    output_index_order = ['i','l']
    prod_config0 = Config('_X', ['A','B'], output_idx_order=['i','k'], input_idx_order=['i','j','k'], fused=True)
    cons_config0 = Config('X_', ['C'], output_idx_order=['k','l'], input_idx_order=['k','l'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config0, cons_config0, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', ['j','k'], ['k','l']] == sched.input_idx_order


    # X(i,m) = A(i,j)*B(j,k)*C(k,l)*D(l,m)
    expr = ['A','B','C','D']
    output_index_order = ['i','m']
    # recursively using the previous fused schedule
    prod_config = fused_scheds[0]
    cons_config = Config('X_', ['D'], output_idx_order=['l','m'], input_idx_order=['l','m'], fused=True)

    fused_scheds = []
    fused('X', expr, output_index_order, prod_config, cons_config, True, fused_scheds)

    assert len(fused_scheds) == 1
    for sched in fused_scheds:
        assert True == sched.fused
        assert expr == sched.expr
        assert output_index_order == sched.output_idx_order
        assert ['i', [['j','k'],['k','l']], ['l','m']] == sched.input_idx_order