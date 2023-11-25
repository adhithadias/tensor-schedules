import pytest
import regex as re
from src.file_storing import read_baskets_from_json, read_json
from src.generate_taco_schedule import TransformConfigToTaco, UnfusedConfigToTacoVisitor
from src.visitor import PrintConfigVisitor

def test_generate_schedules_1():
    
    json_file = "test_schedules/test3_with_z3_pruning.json"
    baskets, tensor_accesses = read_baskets_from_json(json_file)
    print(f'# of pruned_schedules: {len(baskets)}')
    test_name = "sddmm_spmm_real"
    file_name = "/home/min/a/kadhitha/workspace/my_taco/sparseLNR/test/tests-workspaces.cpp"
    
    for i, basket in enumerate(baskets.get_baskets()):
        for config in basket[2]:
            tf = TransformConfigToTaco(config, test_name, tensor_accesses)
            text = tf.gen_taco_code()
            
            f = open(file_name, "r+")
            file = f.read()
            
            regex = r'/\* BEGIN ' + f'{test_name}' + r' TEST \*/[\s\S\n]+/\* END ' + f'{test_name}' + r' TEST \*/'
            match_regex = re.compile(regex)
            
            # substitute text for match_regex in the file
            file = match_regex.sub(text, file)
            # print(l , '------', flush = True)
            
            f.seek(0)
            f.write(file)
            f.truncate()
            f.close()
                
    
def test_generate_schedules_2():
    
    json_file = "test_schedules/test2_with_z3_pruning.json"
    baskets, tensor_accesses = read_baskets_from_json(json_file)
    print(f'# of pruned_schedules: {len(baskets)}')
    test_name = "loopcontractfuse_real"
    file_name = "/home/min/a/kadhitha/workspace/my_taco/sparseLNR/test/tests-workspaces.cpp"
    
    for i, basket in enumerate(baskets.get_baskets()):
        for config in basket[2]:
            tf = TransformConfigToTaco(config, test_name, tensor_accesses)
            text = tf.gen_taco_code()
            
            f = open(file_name, "r+")
            file = f.read()
            
            regex = r'/\* BEGIN ' + f'{test_name}' + r' TEST \*/[\s\S\n]+/\* END ' + f'{test_name}' + r' TEST \*/'
            match_regex = re.compile(regex)
            
            # substitute text for match_regex in the file
            file = match_regex.sub(text, file)
            # print(l , '------', flush = True)
            
            f.seek(0)
            f.write(file)
            f.truncate()
            f.close()
            
            
def test_generate_schedules_3():
    
    json_file = "test_schedules/json_for_testing.json"
    baskets, tensor_accesses = read_baskets_from_json(json_file)
    print(f'# of pruned_schedules: {len(baskets)}')
    test_name = "spmm_gemm_real"
    file_name = "/home/min/a/kadhitha/workspace/my_taco/sparseLNR/test/tests-workspaces.cpp"
    
    for i, basket in enumerate(baskets.get_baskets()):
        for config in basket[2]:
        
            # pcv = PrintConfigVisitor(tensor_accesses)
            # pcv.visit(config)
            print(config, flush=True)
            
            if (config.fused != 0): continue
            
            tf = UnfusedConfigToTacoVisitor(test_name, tensor_accesses, config.original_idx_perm, file_name)
            # tf.set_tensor_accesses(tensor_accesses)
            tf.visit(config)
            print('--', flush=True)
            print(len(tf.schedules))
            print(tf.schedules)
            print(tf.paths)
            print(tf.expr_definitions)
            print(tf.outputs)
            print(tf.assignments)
            print('--', flush=True)
            
            tf.write_to_file(True)
            
            print('-----------------------------', flush=True)
            
            return