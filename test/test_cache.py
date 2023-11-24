import pytest
from src.file_storing import read_baskets_from_json, read_json
from src.cache import add_cache_locality
from src.util import remove_duplicates

def test_cache():
    json_file = "test_schedules/test4_with_z3_pruning.json"
    baskets, tensor_accesses = read_baskets_from_json(json_file)
    
    # assert 0 == len(pruned_schedules)
    print(f'# of pruned_schedules: {len(baskets)}')
    
    add_cache_locality(tensor_accesses, baskets)
     

def test_remove_duplicates():
    json_file = "test_schedules/test3_without_z3_pruning.json"
    
    schedules = read_json(json_file)
    print('initial schedules: ', len(schedules))
    
    schedules = remove_duplicates(schedules)
    print('pruned schedules: ', len(schedules))