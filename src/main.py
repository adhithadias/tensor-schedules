from src.autosched import sched_enum
from src.visitor import PrintConfigVisitor
from src.prune import prune_using_depth

schedules = []
test = 4

if test == 0:
    # X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m)
    accesses = {
        'X': ['i', 'm'],
        'A': ['i', 'j'],
        'B': ['j', 'k'],
        'C': ['k', 'l'],
        'D': ['l', 'm']
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i')],
        # 'B': [],
        # 'C': [],
        # 'D': [],
    }
    sched_enum('X', ['A','B','C','D'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)
elif test == 1:
    # X(i,l) = A(i,j) * B(j,k) * C(k,l)
    accesses = {
        'X': ['i', 'l'],
        'A': ['i', 'j'],
        'B': ['j', 'k'],
        'C': ['k', 'l']
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i')],
        # 'B': [],
        # 'C': [],
        # 'D': [],
    }
    sched_enum('X', ['A','B','C'], accesses['X'], accesses, tensor_idx_order_constraints, schedules)
elif test == 2: # Tensor contraction
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    accesses = {
        'A': ['l', 'm', 'n'],
        'B': ['i', 'j', 'k'],
        'C': ['i', 'l'],
        'D': ['j', 'm'],
        'E': ['k', 'n']
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    sched_enum('A', ['B','C','D','E'], accesses['A'], accesses, tensor_idx_order_constraints, schedules)
elif test == 3: # <SDDMM, SpMM>
    # A(i,l) = B(i,j) * C(i,k) * D(j,k) * E(j,l)
    accesses = {
        'A': ['i', 'l'],
        'B': ['i', 'j'],
        'C': ['i', 'k'],
        'D': ['j', 'k'],
        'E': ['j', 'l']
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    sched_enum('A', ['B','C','D','E'], accesses['A'], accesses, tensor_idx_order_constraints, schedules)
elif test == 4: # <SDDMM, SpMM, GEMM>
    # A(i,m) = B(i,j) * C(i,k) * D(j,k) * E(j,l) * F(l,m)
    accesses = {
        'A': ['i', 'm'],
        'B': ['i', 'j'],
        'C': ['i', 'k'],
        'D': ['j', 'k'],
        'E': ['j', 'l'],
        'F': ['l', 'm']
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    sched_enum('A', ['B','C','D','E', 'F'], accesses['A'], accesses, tensor_idx_order_constraints, schedules)
elif test == 5:
    # X(i,l,m) = A(i,j,k) * B(j,l) * C(k,m)
    accesses = {
        'X': ['i', 'l', 'm'],
        'A': ['i', 'j', 'k'],
        'B': ['j', 'l'],
        'C': ['k', 'm']
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i'), ('k','j'), ('k','i')],
        # 'X': [('j')],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    sched_enum('A', ['B','C','D','E'], accesses['A'], accesses, tensor_idx_order_constraints, schedules)

printer = PrintConfigVisitor(accesses)

print('\n\n\n\n\n\n\n')
print(len(schedules))

print('\n\n\n\n\n\n\n')
pruned_schedules = prune_using_depth(schedules)
print(len(pruned_schedules))

print('/**************************************************************************/')
print('/********************** PRINTING SCHEDULES ********************************/')
print('/**************************************************************************/')

# for schedule in pruned_schedules:
#     schedule.accept(printer)
#     print('-----------')

#     # all the schedules with fused:True must be given to SparseLNR
#     # all the schedules with fused:False must be given to TACO