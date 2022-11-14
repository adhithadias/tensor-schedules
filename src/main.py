from src.autosched import sched_enum
from src.visitor import PrintConfigVisitor

# X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m)
accesses = {
    'X': ['i', 'm'],
    'A': ['i', 'j'],
    'B': ['j', 'k'],
    'C': ['k', 'l'],
    'D': ['l', 'm']
}
schedules = sched_enum(['A','B','C','D'], accesses['X'], accesses)

# # X(i,l) = A(i,j) * B(j,k) * C(k,l)
# accesses = {
#     'X': ['i', 'l'],
#     'A': ['i', 'j'],
#     'B': ['j', 'k'],
#     'C': ['k', 'l']
# }
# schedules = sched_enum(['A','B','C'], accesses['X'], accesses)
printer = PrintConfigVisitor()

print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
print('/**************************************************************************/')
print('/********************** PRINTING SCHEDULES ********************************/')
print('/**************************************************************************/')

for schedule in schedules:
    schedule.accept(printer)
    print('-----------')

    # all the schedules with fused:True must be given to SparseLNR
    # all the schedules with fused:False must be given to TACO