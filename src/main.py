from autosched import sched_enum
from visitor import PrintConfigVisitor

schedules = sched_enum(['a','b','c','d'])
printer = PrintConfigVisitor()

for schedule in schedules:
    schedule.accept(printer)
    print('-----------')