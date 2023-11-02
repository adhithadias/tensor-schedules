from argparse import ArgumentParser, RawTextHelpFormatter
from z3 import Int
from src.visitor import PrintConfigVisitor
from src.util import Baskets, get_simplified_complexity
from src.config import Config
from src.prune import prune_using_z3, prune_using_loop_depth, prune_baskets_using_z3
from src.file_storing import store_json, store_baskets_to_json, read_json, read_baskets_from_json, lists_to_tuples
from time import time

from scipy.io import mmread

# reads and runs the configurations after performing z3


schedules = []
# 2 A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n) - tensor contraction
# 3 A(i,l) = B(i,j) * C(i,k) * D(j,k) * E(j,l) - <SDDMM, SpMM>
# 4 A(i,m) = B(i,j) * C(i,k) * D(j,k) * E(j,l) * F(l,m) - <SDDMM, SpMM, GEMM>
# 5 A(i,l,m) = B(i,j,k) * C(j,l) * D(k,m) - <SpTTM, TTM>

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-c', '--configuration', default=0, help='configuration number', type=int)


args = vars(parser.parse_args())
test = args["test"]
configuration = args["configuration"]

print(test, configuration, type(test), type(configuration))

if test == 0:
    # X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m)
    accesses = {
        'X': ('i', 'm'),
        'A': ('i', 'j'),
        'B': ('j', 'k'),
        'C': ('k', 'l'),
        'D': ('l', 'm')
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i')],
        # 'B': [],
        # 'C': [],
        # 'D': [],
    }

elif test == 1:
    # X(i,l) = A(i,j) * B(j,k) * C(k,l)
    accesses = {
        'X': ('i', 'l'),
        'A': ('i', 'j'),
        'B': ('j', 'k'),
        'C': ('k', 'l')
    }
    tensor_idx_order_constraints = {
        'A': [('j', 'i')],
        # 'B': [],
        # 'C': [],
        # 'D': [],
    }

elif test == 2: # Tensor contraction
    # A(l,m,n) = B(i,j,k) * C(i,l) * D(j,m) * E(k,n)
    accesses = {
        'A': ('l', 'm', 'n'),
        'B': ('i', 'j', 'k'),
        'C': ('i', 'l'),
        'D': ('j', 'm'),
        'E': ('k', 'n')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    cache = {}

elif test == 3: # <SDDMM, SpMM>
    # A(i,l) = B(i,j) * C(i,k) * D(j,k) * E(j,l)
    accesses = {
        'A': ('i', 'l'),
        'B': ('i', 'j'),
        'C': ('i', 'k'),
        'D': ('j', 'k'),
        'E': ('j', 'l')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    tensor_expression = ('B','C','D','E')
    cache = {}
    
elif test == 4: # <SDDMM, SpMM, GEMM>
    # A(i,m) = B(i,j) * C(i,k) * D(j,k) * E(j,l) * F(l,m)
    accesses = {
        'A': ('i', 'm'),
        'B': ('i', 'j'),
        'C': ('i', 'k'),
        'D': ('j', 'k'),
        'E': ('j', 'l'),
        'F': ('l', 'm')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i')],
        # 'C': [],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    tensor_expression = ('B','C','D','E','F')
    cache = {}

elif test == 5:
    # A(i,l,m) = B(i,j,k) * C(j,l) * D(k,m)
    accesses = {
        'A': ('i', 'l', 'm'),
        'B': ('i', 'j', 'k'),
        'C': ('j', 'l'),
        'D': ('k', 'm')
    }
    tensor_idx_order_constraints = {
        'B': [('j', 'i'), ('k','j'), ('k','i')],
        # 'X': [('j')],
        # 'D': [],
        # 'E': [],
        # 'A': []
    }
    tensor_expression = ('B','C','D')

printer = PrintConfigVisitor(accesses)

depth_pruned_schedules = read_json(f'test{test}_without_z3_pruning.json')

i = Int('i')
j = Int('j')
k = Int('k')
l = Int('l')
m = Int('m')
n = Int('n')
jpos = Int('jpos')
kpos = Int('kpos')

z3_variables = {'i': i, 'j': j, 'k': k, 'l': l, 'm': m, 'n': n, 'jpos': jpos, 'kpos': kpos}
z3_constraints = []

if (test == 2 and configuration == 0):
    z3_constraints = [i >= 5000, i <= 15000, j >= 5000, j <= 15000, 
                    k == 2, l >= 8, l <= 256, m == 10000, n >= 8, n <= 256,
                    jpos >= 0, kpos >= 0,
                    100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
                    i * j * k < 1000 * i * jpos * kpos]  # 0.001 * i*j < i*jpos
elif (test == 2 and configuration == 1):
    z3_constraints = [i == 165000, j == 9000, 
                    k == 1000, l == 16, m == 16, n == 16,
                    jpos >= 0, kpos >= 0,
                    100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
                    i * j * k < 1000 * i * jpos * kpos]  # 0.001 * i*j < i*jpos
elif (test ==2 and configuration == 2):
    z3_constraints = [i >= 5000, i <= 15000, j >= 5000, j <= 15000, 
                    k >= 5000, k <= 15000, l >= 8, l <= 256, m >= 8, m <= 256, n >= 8, n <= 256,
                    jpos >= 0, kpos >= 0,
                    100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
                    i * j * k < 1000 * i * jpos * kpos]  # 0.001 * i*j < i*jpos
elif (test == 3 or test == 4):
    # z3_constraints = [i >= 5000, i <= 15000, j >= 5000, j <= 15000, 
    #                 k >= 8, k <= 256, l >= 8, l <= 256, jpos >= 0,
    #                 m >= 8, m <=256,
    #                 100 * i * jpos < i * j,   # i*jpos < 0.01 * i*j
    #                 i * j < 1000 * i * jpos]  # 0.001 * i*j < i*jpos
    z3_constraints = [i >= 2500, i <= 5560000, j >= 2500, j <= 5560000, 
                    k == 16, l == 16, jpos >= 3, jpos <= 218,
                    m == 16]
    # can pass additional constraints here like limit additional memory
elif (test == 5):
    z3_constraints = [i >= 5000, i <= 15000, j >= 5000, j <= 15000, 
                    k >= 8, k <= 256, l >= 8, l <= 256, m >= 8, m <= 256,
                    jpos >= 0, kpos >= 0,
                    100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
                    i * j * k < 1000 * i * jpos * kpos]  # 0.001 * i*j < i*jpos


baskets = Baskets(depth_pruned_schedules)
z3_pruned_baskets = Baskets(prune_baskets_using_z3(baskets, z3_variables, z3_constraints))
print('number of baskets after z3 pruning:', len(z3_pruned_baskets), flush = True)
    
store_baskets_to_json(accesses, z3_pruned_baskets, f'test{test}_with_z3_pruning.json')
read_configs = read_baskets_from_json(f'test{test}_with_z3_pruning.json')

assert len(read_configs) == len(z3_pruned_baskets)
# print("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    
ALLOWED_ELEMENT_SIZE = 2621440 # 50% of the LLC
# final_constraints = {'i': 1800, 'j': 800, 'k': 1000, 'l': 64, 'm': 16, 'n': 32, 'jpos': 253, 'kpos': 253}
# final_constraints = {'i': 1800, 'j': 1600, 'k': 2000, 'l': 64, 'm': 16, 'n': 32, 'jpos': 253, 'kpos': 253}
# final_constraints = {'i': 320000, 'j': 2820000, 'k': 1600000, 'l': 64, 'm': 64, 'n': 64, 'jpos': 19, 'kpos': 19} # test 2, flickr-3d

final_constraints = {'i': 165000, 'j': 11000, 'k': 2, 'l': 64, 'm': 64, 'n': 64, 'jpos': 12, 'kpos': 13} # test 2, vast

final_constraints = {'i': 2900000, 'j': 2140000, 'k': 25500000, 'l': 64, 'm': 64, 'n': 64, 'jpos': 7, 'kpos': 7}

# final_constraints = {"i": 1000000, "j": 1000000, "k": 1, "l": 1, "m": 16, "jpos": 3}

tstart = time()
best_time, best_memory, best_schedules = read_configs.filter_with_final_constraints(final_constraints, ALLOWED_ELEMENT_SIZE)
tend = time()

print('best time:', best_time, ', best memory:', best_memory, ', time: ', best_schedules[0], ', mem:', best_schedules[1], ', #:', len(best_schedules[2]), flush = True)
print('time taken:', (tend - tstart)*1000, 'ms', flush = True)
# best_schedule.accept(printer)

store_json(accesses, best_schedules[2], f'test{test}_best_schedule.json')


#     # all the schedules with fused:True must be given to SparseLNR
#     # all the schedules with fused:False must be given to TACO