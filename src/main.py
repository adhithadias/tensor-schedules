from src.autosched import sched_enum
from src.visitor import PrintConfigVisitor

schedules = []
test = 2

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
        'B': [],
        'C': [],
        'D': [],
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
    schedules = sched_enum('X', ['A','B','C'], accesses['X'], accesses)
else:
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    accesses = {
        'A': ['l', 'm', 'n'],
        'B': ['i', 'j', 'k'],
        'C': ['i', 'l'],
        'D': ['j', 'm'],
        'E': ['k', 'n']
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i'), ('k','j'), ('k','i')],
        'B': [],
        'C': [],
        'D': [],
        'E': []
    }
    sched_enum('A', ['B','C','D','E'], accesses['A'], accesses, tensor_idx_order_constraints, schedules)


printer = PrintConfigVisitor(accesses)

print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
print(len(schedules))
print('/**************************************************************************/')
print('/********************** PRINTING SCHEDULES ********************************/')
print('/**************************************************************************/')

# for schedule in schedules:
#     schedule.accept(printer)
#     print('-----------')

#     # all the schedules with fused:True must be given to SparseLNR
#     # all the schedules with fused:False must be given to TACO