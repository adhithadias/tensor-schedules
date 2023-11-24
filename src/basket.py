from src.util import complexities_equal, get_simplified_complexity, get_simplified_cache

class Baskets:
    baskets = []
    
    def __init__(self, schedules):
        if (len(schedules) == 0): return
        
        if (type(schedules[0]) == tuple):
            self.baskets = schedules
            return
        
        for schedule in schedules:
            # print(schedule)
            added = False
            tc = schedule.time_complexity["r"] + schedule.time_complexity["a"]
            mc = schedule.memory_complexity
            # print("tc mc", tc, mc)
            for btc, mbc, list in self.baskets:
                if (complexities_equal(tc, btc, mc, mbc)):
                    added = True
                    list.append(schedule)
                    break

            if not added:  
                self.baskets.append((tc, mc, [schedule]))

        print(f"{len(self.baskets)} baskets created")
        for i, (tc, mc, list) in enumerate(self.baskets):
            print(f'basket {i}: {tc} {mc} {len(list)}')
            
    def __getitem__(self, index):
        return self.baskets[index]
        
    def __len__(self):
        return len(self.baskets)
        
    def get_baskets(self):
        return self.baskets
    
    
    def filter_with_final_constraints(self, final_constraints, allowed_element_size):
        best_time = -1
        best_memory = -1
        best_schedules = None

        for i, s1 in enumerate(self.baskets) :
            
            (t,m) = get_simplified_complexity(s1[0], s1[1], final_constraints)
            # print(t, m)
            if ((best_schedules == None or t < best_time or (t == best_time and m < best_memory)) and m < allowed_element_size):
                best_time = t
                best_memory = m
                best_schedules = s1
        
        best_cache = -1
        schedules = []
        # cache pruning
        for i, s1 in enumerate(best_schedules[2]):
            
            print('cache complexity', s1.cache_complexity)
            t = get_simplified_cache(s1.cache_complexity, final_constraints)
            print('t: ', t)
            if (best_cache == -1 or t == best_cache) : 
                best_cache = t
                schedules.append(s1)
            elif (t < best_cache) :
                best_cache = t 
                schedules = [s1]
                
        print('selected schedules #: ', len(schedules))
        
        return best_time, best_memory, (best_schedules[0], best_schedules[1], schedules)