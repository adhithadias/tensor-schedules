from autosched import sched_enum
from visitor import PrintConfigVisitor

# X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m)
accesses = {
    'X': ['i', 'm'],
    'A': ['i', 'j'],
    'B': ['j', 'k'],
    'C': ['k', 'l'],
    'D': ['l', 'm']
}
schedules = sched_enum(['A','B','C','D'], accesses)
printer = PrintConfigVisitor()

for schedule in schedules:
    schedule.accept(printer)
    print('-----------')

    # all the schedules with fused:True must be given to SparseLNR
    # all the schedules with fused:False must be given to TACO