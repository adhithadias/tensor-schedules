from src.autosched import sched_enum
from src.config import Config

ignore_unfused = True

# retrieve complexity of a given tensor schedule 
def retrieve_complexity(schedule=Config) -> str:
  complexity = ""
  if (len(schedule.input_idx_order) > 0 and type(schedule.input_idx_order[-1]) == list) or not schedule.fused:
    producer = retrieve_complexity(schedule.input_idx_order[-2])
    consumer = retrieve_complexity(schedule.input_idx_order[-1])
    if len(producer) > 0 and len(consumer) > 0:
      complexity += "*".join(schedule.input_idx_order[0:-2]) + "*"
      complexity += "(" + producer + "+"
      return complexity + consumer + ")"
    elif len(producer) > 0:
      return "*".join(schedule.input_idx_order[0:-2]) + "*(" + producer + ")"
    elif len(consumer) > 0:
      return "*".join(schedule.input_idx_order[0:-2]) + "*(" + consumer + ")"
    else:
      return "*".join(schedule.input_idx_order[0:-2])
  else:
    return "*".join(schedule.input_idx_order)

def retrieve_all_complexities(schedules = [Config]):
  complexities = []
  for schedule in schedules: 
    if schedule.fused:
      complexities.append(retrieve_complexity(schedule))
    # else:
    #   complexities.append(retrieve_complexity(schedule))
      
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