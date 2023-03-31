from bitarray import bitarray
from src.config import Config

def get_loop_depth(schedule : Config) -> int :
    
    assert type(schedule.time_complexity['r']) == list
    assert type(schedule.time_complexity['a']) == list
    max_ : int = 0
    for complexity in schedule.time_complexity['r']:
        if (len(complexity) > max_) : max_ = len(complexity)
    
    for complexity in schedule.time_complexity['a']:
        if (len(complexity) > max_) : max_ = len(complexity)

    return max_

def get_memory_depth(schedule : Config) -> int :
    
    assert type(schedule.memory_complexity) == list
    max_ : int = 0
    for complexity in schedule.memory_complexity:
        if (len(complexity) > max_) : max_ = len(complexity)
    
    return max_

def prune_using_depth(schedules : list) -> list:
    results = []
    complexities = set()
    pruned_array = bitarray(len(schedules))
    pruned_array.setall(0)
    
    for i in range(0, len(schedules)):
        
        if (pruned_array[i]):
            continue
        
        s1 = schedules[i]
        s1_time_depth = get_loop_depth(schedules[i])
        s1_memory_depth = get_memory_depth(schedules[i])
        
        # we have seen the same complexities before
        if (s1_time_depth, s1_memory_depth) in complexities:
            results.append(schedules[i])
            continue
        
        for j in range(0, len(schedules)):
            
            if (pruned_array[j]):
                continue
            
            s2 = schedules[j]
            s2_time_depth = get_loop_depth(schedules[j])
            s2_memory_depth = get_memory_depth(schedules[j])
            
            # s2 schedule is better than s1 schedule, we can prune s1 schedule
            if ((s1_time_depth >= s2_time_depth and s1_memory_depth > s2_memory_depth)
                or
                (s1_time_depth > s2_time_depth and s1_memory_depth >= s2_memory_depth)):
                pruned_array[i] = True
                break
            
            # s1 schedule is better than s2 schedule, we can prune s2 schedule
            if ((s1_time_depth <= s2_time_depth and s1_memory_depth < s2_memory_depth)
                or
                (s1_time_depth < s2_time_depth and s1_memory_depth <= s2_memory_depth)):
                pruned_array[j] = True
                continue
            
        if (not pruned_array[i]):
            results.append(schedules[i])
            complexities.add((s1_time_depth, s1_memory_depth))
            
    return results
            