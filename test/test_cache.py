import pytest
from src.file_storing import read_baskets_from_json
from src.cache import add_cache_locality

def test_cache():
    json_file = "test_schedules/test2_with_z3_pruning.json"
    baskets, tensor_accesses = read_baskets_from_json(json_file)
    
    # assert 0 == len(pruned_schedules)
    print(f'# of pruned_schedules: {len(baskets)}')
    
    
    add_cache_locality(tensor_accesses, baskets)
    