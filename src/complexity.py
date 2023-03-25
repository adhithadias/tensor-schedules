from src.autosched import sched_enum
from src.config import Config

# retrieve complexity of a given tensor schedule
def retrieve_fused_complexity(schedule=[]) -> str:
  complexity = ""
  if len(schedule) > 0 and type(schedule[-1]) == list:
    producer = retrieve_fused_complexity(schedule[-2])
    consumer = retrieve_fused_complexity(schedule[-1])
    if len(schedule[0:-2]) > 0:
      complexity += "*".join(schedule[0:-2]) + "*"
    if len(producer) > 0 and len(consumer) > 0:
      complexity += "(" + producer + "+" + consumer + ")"
      return complexity
    elif len(producer) > 0:
      return complexity + "(" + producer + ")"
    elif len(consumer) > 0:
      return complexity + "(" + consumer + ")"
    else:
      # return "*".join(schedule[0:-2])
      return ""
  elif len(schedule) <= 0:
    return ""
  else:
    return "*".join(schedule)



# retrieve complexity of a given tensor schedule 
def retrieve_complexity(schedule=Config) -> str:
  complexity = ""
  # check if fused loop
  if len(schedule.input_idx_order) > 0 and type(schedule.input_idx_order[-1]) == list:
    producer = retrieve_fused_complexity(schedule.input_idx_order[-2])
    consumer = retrieve_fused_complexity(schedule.input_idx_order[-1])
    if len(schedule.input_idx_order[0:-2]) > 0:
      complexity += "*".join(schedule.input_idx_order[0:-2]) + "*"
    if len(producer) > 0 and len(consumer) > 0:
      complexity += "(" + producer + "+" + consumer + ")"
      return complexity
    elif len(producer) > 0:
      return complexity + "(" + producer + ")"
    elif len(consumer) > 0:
      return complexity + "(" + consumer + ")"
    else:
      # return "*".join(schedule.input_idx_order[0:-2])
      return ""
  elif len(schedule.input_idx_order) <= 0:
    return ""
  else:
    return "*".join(schedule.input_idx_order)

def retrieve_all_complexities(schedules = [Config]):
  complexities = []
  for schedule in schedules: 
    if schedule.fused:
      complexities.append(retrieve_complexity(schedule))
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