import pytest
from src.file_storing import read_json
from src.util import Baskets

def test_baskets():
    json_file = "test_schedules/test2_without_z3_pruning.json"
    pruned_schedules = read_json(json_file)
    
    baskets = Baskets(pruned_schedules)
    
    # assert 0 == len(pruned_schedules)
    print(f'# of pruned_schedules: {len(pruned_schedules)}')