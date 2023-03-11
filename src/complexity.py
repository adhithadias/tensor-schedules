from src.autosched import sched_enum
from src.config import Config

# retrieve complexity of a given tensor schedule 
def retrieve_complexity(schedule=[]) -> str:
  complexity = ""
  if len(schedule) > 0 and type(schedule[-1]) == list:
    producer = retrieve_complexity(schedule[-2])
    consumer = retrieve_complexity(schedule[-1])
    if len(producer) > 0 and len(consumer) > 0:
      complexity += "*".join(schedule[0:-2]) + "*"
      complexity += "(" + producer + "+"
      return complexity + consumer + ")"
    elif len(producer) > 0:
      return "*".join(schedule[0:-2]) + "*(" + producer + ")"
    elif len(consumer) > 0:
      return "*".join(schedule[0:-2]) + "*(" + consumer + ")"
    else:
      return "*".join(schedule[0:-2])
  else:
    return "*".join(schedule)

def retrieve_all_complexities(schedules = [Config]):
  complexities = []
  for schedule in schedules: 
    complexities.append(retrieve_complexity(schedule.input_idx_order))
  return complexities

accesses = {
    'X': ['i', 'm'],
    'A': ['i', 'j'],
    'B': ['j', 'k'],
    'C': ['k', 'l'],
    'D': ['l', 'm']
}
schedules = sched_enum(['A', 'B', 'C', 'D'], accesses['X'], accesses)
print(retrieve_all_complexities(schedules))
# print(retrieve_complexity(['i', ['j','k'], ['l', 'k']]))