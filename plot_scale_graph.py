import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal
from itertools import cycle, islice
from argparse import ArgumentParser, RawTextHelpFormatter
from enum import Enum
import numpy as np
from matplotlib.pyplot import xticks

CSV_RESULTS = "csv_results/"
PLOTS_DIR = "plots/"

class FontSize(Enum):
    SMALL_SIZE = 8
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 16
plt.rcParams.update({'font.size': FontSize.BIGGER_SIZE.value})
# plt.rcParams['legend.title_fontsize'] = 'xx-large'

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-r', '--rotation', help='rotation of the tensors in x axis', required=False, default=0, type=int)
parser.add_argument('-d', '--directory', help='directory tensor-schedules', required=False, default='.', type=str)
args = vars(parser.parse_args())
test = args["test"]
rot = args["rotation"]
directory = args["directory"]

if (test == 1):
    f1 = f'{directory}/csv_results/scaletest_sddmm_spmm_webbase-1M.mtx_scaling.csv'
    f2 = f'{directory}/csv_results/scaletest_sddmm_spmm_gemm_webbase-1M.mtx_scaling.csv'
    output_file = f'{directory}/plots/webase-scaling.pdf'
    sa1 = 'SparseAuto: Kernel ①'
    taco1 = 'TACO: Kernel ①'
    sa2 = 'SparseAuto: Kernel ②'
    taco2 = 'TACO: Kernel ②'
    ylim = (0,100)
else:
    f1 = f'{directory}/csv_results/scaletest_spttm_ttm_darpa1998.tns_scaling.csv'
    f2 = f'{directory}/csv_results/scaletest_mttkrp_gemm_darpa1998.tns_scaling.csv'
    output_file = f'{directory}/plots/darpa-scaling.pdf'
    sa1 = 'SparseAuto: Kernel ⑥'
    taco1 = 'TACO: Kernel ⑥'
    sa2 = 'SparseAuto: Kernel ⑧'
    taco2 = 'TACO: Kernel ⑧'
    ylim = (0,36)
    
data_file1 = f1
data_file2 = f2

# threads,default_median,default_stddev,sparseauto_median,sparseauto_stddev
df1 = pd.read_csv(data_file1, header=0, names=['threads', 'default_median', 'default_stddev', 'sparseauto_median', 'sparseauto_stddev', 'speedup'])
df2 = pd.read_csv(data_file2, header=0, names=['threads', 'default_median', 'default_stddev', 'sparseauto_median', 'sparseauto_stddev', 'speedup'])

print(df1)
print(df2)

val1 = df1['default_median'][0]
val2 = df2['default_median'][0]

print(val1)
print(val2)

# ①②③④⑤⑥⑦⑧⑨
df1[sa1] = val1 / df1['sparseauto_median']
df1[taco1] = val1 / df1['default_median']
df1[sa2] = val2 / df2['sparseauto_median']
df1[taco2] = val2 / df2['default_median']
df1['threads'] = df1['threads'].astype(str)

# df1['SparseAuto <SDDMM,SpMM>'] = val1 / df1['sparseauto_median']
# df1['TACO <SDDMM,SpMM>'] = val1 / df1['default_median']
# df1['SparseAuto <SDDMM,SpMM,GEMM>'] = val2 / df2['sparseauto_median']
# df1['TACO <SDDMM,SpMM,GEMM>'] = val2 / df2['default_median']
# df1['threads'] = df1['threads'].astype(str)

print(df1)

# 'c', 'tab:pink', 'green', 'mediumorchid'
df1.plot(x = 'threads', y = [sa1, taco1, sa2, taco2], linestyle='-', marker='o', color = ['purple', 'violet', 'darkgreen', 'limegreen'], secondary_y=False, ylim = ylim, rot = rot, ylabel = "Speedup", xlabel = "$ Threads", legend = False)
# df1.plot(x = 'threads', y = ['SparseAuto <SDDMM,SpMM>', 'TACO <SDDMM,SpMM>', 'SparseAuto <SDDMM,SpMM,GEMM>', 'TACO <SDDMM,SpMM,GEMM>'], linestyle='-', marker='o', color = ['c', 'tab:pink', 'green', 'mediumorchid'], secondary_y=False, rot = rot, ylabel = "Speedup", xlabel = "$ Threads", legend = False)

plt.xlabel("# Threads")
plt.ylabel('Speedup over\nTACO-serial Execution')

# plt.legend(bbox_to_anchor=(1.1, 1.05))
plt.legend(prop={'size': 14})

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y')
# ax.spines['bottom'].set_visible(False)
# ax.spines['left'].set_visible(False)

plt.savefig(output_file, bbox_inches='tight',dpi=100)