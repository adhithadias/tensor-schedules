import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle, islice
from argparse import ArgumentParser, RawTextHelpFormatter
from enum import Enum
import numpy as np

CSV_RESULTS = "csv_results/"
PLOTS_DIR = "plots/"
NAME = 'SparseAuto'
NAME2 = 'SpAuto-Parallel'

class FontSize(Enum):
    SMALL_SIZE = 8
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14
    
plt.rcParams.update({'font.size': FontSize.BIGGER_SIZE.value})

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-r', '--rotation', help='rotation of the tensors in x axis', required=False, default=45, type=int)
parser.add_argument('--directory', type=str, help='Path to taco directory')
args = vars(parser.parse_args())
test = args["test"]
rot = args["rotation"]
dir = args.directory

if test == 2:
    ax1_ylim = (1e2, 1e7)
    ax2_ylim = (0, 120)
    bar_width = 0.5
elif test == 3:
    ax1_ylim = (1, 2e5)
    ax2_ylim = (0, 12)
    bar_width = 0.7
elif test  == 4:
    ax1_ylim = (1e0, 1e6)
    ax2_ylim = (1,200)
    bar_width = 0.7
elif test == 5:
    ax1_ylim = (1e2, 1e5)
    ax2_ylim = (0, 8)
    bar_width = 0.5
elif test == 6:
    ax1_ylim = (1e2, 1e5)
    ax2_ylim = (0, 7)
    bar_width = 0.5
elif test == 7:
    ax1_ylim = (1e0, 1e6)
    ax2_ylim = (0, 25)
    bar_width = 0.7
elif test == 8:
    ax1_ylim = (1e0, 5e5)
    ax2_ylim = (0, 16)
    bar_width = 0.7
elif test == 9:
    ax1_ylim = (1e2, 5e6)
    ax2_ylim = (8, 22)
    bar_width = 0.5
    
known_plot = test == 9 or test == 8 or test == 7 or test == 2 or test == 3 or \
    test == 4 or test == 5 or test == 6

# data_file = CSV_RESULTS + f'test{test}.csv'
data_file = f"{dir}/tensor-schedules/csv_results/test{test}.csv"
# data_file_parallel = CSV_RESULTS + f'test{test}_parallel.csv'
data_file_parallel = f"{dir}/tensor-schedules/csv_results/test{test}_parallel.csv"
# output_file = PLOTS_DIR + f'plot{test}.png' # plots/plotX.png
output_file = f"{dir}/tensor-schedules/plots/fig8/test{test}.png"
if (test != 6):
    df_parallel = pd.read_csv(data_file_parallel, header=0, names=['Tensor', 'sparseShed', 'Runtime Standard Dev', 'default', 'Default runtime std', 'config'])
df = pd.read_csv(data_file, header=0, names=['Tensor', 'sparseShed', 'Runtime Standard Dev', 'default', 'Default runtime std', 'config'])
df = df.drop(columns=['config'])

df[NAME] = df['sparseShed']
if (test == 6): df[NAME2] = np.nan
else: df[NAME2] = df_parallel['sparseShed']

df['Tensor'] = df['Tensor'].str.split('.').str[0]
df['Tensor'] = df['Tensor'].str.slice(0,10)
df['Matrix/Tensor'] = df['Tensor']
if (test != 6):
    df_parallel['dataset'] = df_parallel['Tensor'].str.split('.').str[0]
    df_parallel['dataset'] = df_parallel['dataset'].str.slice(0,10)
    df_parallel['Matrix/Tensor'] = df_parallel['dataset']
df['TACO'] = df['default']

if (test == 6): df['TACO-Parallel'] = np.nan
else: df['TACO-Parallel'] = df_parallel['default']
df.set_index('Matrix/Tensor', inplace=True)

if (test != 6):
    df_parallel.set_index('dataset', inplace=True)

df['speedup'] = df['default'] / df['sparseShed']
df['spd-Parallel'] = df['TACO-Parallel'] / df[NAME2]
df['spd-Parallel'].clip(upper=ax2_ylim[1], inplace=True)

# remove from df if the row index is 'default'
# if (test != 7):
#     df = df[~(df.index.str.contains('bcsstk17') |
#         df.index.str.contains('mac_econ_f'))]
# else:
#     df = df[~(df.index.str.contains('mac_econ_f'))]
print(df)

if (test != 6):
    df['rstd10'] = df_parallel['Runtime Standard Dev']
    df['dstd10'] = df_parallel['Default runtime std']
else: 
    df['rstd10'] = np.nan
    df['dstd10'] = np.nan
# convert the std columns to an array
yerr = df[['Runtime Standard Dev', 'Default runtime std', 
           'rstd10', 'dstd10']].to_numpy().T

print(df)

fig, ax = plt.subplots()
ax2 = ax.twinx()

# plt.rcParams.update({'font.size': 22})
# plt.rc('axes', labelsize=BIGGER_SIZE)
# https://matplotlib.org/stable/gallery/color/named_colors.html
# df[['sparseShed', 'default']].plot(kind='bar', yerr=yerr, alpha=0.5, error_kw=dict(ecolor='k'), color=['r', 'b'])
my_colors = list(islice(cycle(['c', 'tab:pink', 'green', 'mediumorchid']), None, len(df)))
if known_plot and test != 6:
    df.plot(y = [NAME, 'TACO', NAME2, 'TACO-Parallel'], ax = ax, kind='bar', yerr=yerr, error_kw=dict(ecolor='k'), log=True, rot = rot, ylim = ax1_ylim, ylabel = "Execution Time (ms)", legend = False, color = my_colors, align='center', width=bar_width)
elif test == 6:
    df.plot(y = [NAME, 'TACO'], ax = ax, kind='bar', yerr=yerr, error_kw=dict(ecolor='k'), log=True, rot = rot, ylim = ax1_ylim, ylabel = "Execution Time (ms)", legend = False, color = my_colors, align='center', width=bar_width)
else:
    df.plot(y = [NAME, 'TACO', NAME2, 'TACO-Parallel'], ax = ax, kind='bar', yerr=yerr, error_kw=dict(ecolor='k'), log=True, rot = rot, ylabel = "Execution Time (ms)", legend = False, color = my_colors)

def format_e(n):
    a = '%1.1E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

if known_plot and test != 6:
    df.plot(x = 'Tensor', y = ['speedup', 'spd-Parallel'], ax = ax2, linestyle='-', marker='o', color = ['black','blue'], secondary_y=True, rot = rot, ylim = ax2_ylim, ylabel = "Speedup", xlabel = "Matrix/Tensor", legend = False)
elif test == 6:
    df.plot(x = 'Tensor', y = ['speedup'], ax = ax2, linestyle='-', marker='o', color = 'black', secondary_y=True, rot = rot, ylim = ax2_ylim, ylabel = "Speedup", xlabel = "Matrix/Tensor", legend = False)
else:
    df.plot(x = 'Tensor', y = ['speedup'], ax = ax2, linestyle='-', marker='o', color = 'black', secondary_y=True, rot = rot, ylabel = "Speedup", xlabel = "Matrix/Tensor", legend = False)
# plt.ylabel("speedup")

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.right_ax.get_legend_handles_labels()
legend = ax.legend(h1+h2, l1+l2, loc='best', ncol = 2)
# plt.setp(legend.get_title(),fontsize='xx-large')

ax2 = plt.gca()
# fig, ax = plt.subplots()
yticks = ax2.yaxis.get_major_ticks()
yticks[-1].set_visible(False)

if (test == 2):
    d = 0.010  # proportion of vertical to horizontal extent of the slanted line
    d_ = 0.005
    kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False, zorder=10)
    ax2.plot((1 - d, 1 + d), (0.95 - d, 0.95 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (0.93 - d, 0.93 + d), **kwargs)  # bottom-right diagonal
    kwargs.update(color='w')
    ax2.plot((1, 1), (0.94 - d_, 0.94 + d_), **kwargs)  # bottom-right diagonal


plt.xlabel("Matrix/Tensor")
plt.savefig(output_file, bbox_inches='tight',dpi=100)