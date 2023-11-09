import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal
# import ArgumentParser
from argparse import ArgumentParser, RawTextHelpFormatter

CSV_RESULTS = ""
PLOTS_DIR = "plots/"

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-r', '--rotation', help='rotation of the tensors in x axis', required=False, default=45, type=int)
args = vars(parser.parse_args())
test = args["test"]
rot = args["rotation"]

if test  == 4:
    ax1_ylim = (1e0, 1e5)
    ax2_ylim = (30,160)
elif test == 2:
    ax1_ylim = (1e3, 1e6)
    ax2_ylim = (0, 100)
elif test == 3:
    ax1_ylim = (1, 1e5)
    ax2_ylim = (4, 9)
elif test == 5:
    ax1_ylim = (1e3, 1e5)
    ax2_ylim = (0, 3.5)
    
known_plot = test == 2 or test == 3 or test == 4 or test == 5

data_file = CSV_RESULTS + f'test{test}.csv'
output_file = PLOTS_DIR + f'plot{test}.png'
df = pd.read_csv(data_file, header=0, names=['Tensor', 'sparseShed', 'Runtime Standard Dev', 'default', 'Default runtime std', 'config'])

print(df)

df['Tensor'] = df['Tensor'].str.split('.').str[0]
df['Matrix/Tensor'] = df['Tensor']
df['TACO'] = df['default']
df.set_index('Matrix/Tensor', inplace=True)

df['speedup'] = df['default'] / df['sparseShed']
print(df)

# convert the std columns to an array
yerr = df[['Runtime Standard Dev', 'Default runtime std']].to_numpy().T

# print(yerr)
# array([[1, 5],
#        [3, 2]], dtype=int64)

fig, ax = plt.subplots()
ax2 = ax.twinx()
# df[['sparseShed', 'default']].plot(kind='bar', yerr=yerr, alpha=0.5, error_kw=dict(ecolor='k'), color=['r', 'b'])
if known_plot:
    df.plot(y = ['sparseShed', 'TACO'], ax = ax, kind='bar', yerr=yerr, error_kw=dict(ecolor='k'), log=True, rot = rot, ylim = ax1_ylim, ylabel = "Execution Time (ms)", legend = False)
else:
    df.plot(y = ['sparseShed', 'TACO'], ax = ax, kind='bar', yerr=yerr, error_kw=dict(ecolor='k'), log=True, rot = rot, ylabel = "Execution Time (ms)")

def format_e(n):
    a = '%1.1E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

# for p in ax.patches:
#     ax.annotate(format_e(Decimal(p.get_height())), (p.get_x() * 1.000, p.get_height() * 1.05 if p.get_height() < 5e4 else 5e4))

# plt.ylabel("Execution Time (ms)")
# plt.yscale("log")
# plt.legend(bbox_to_anchor=(1.0, 1.0))
# plt.title("Optimized Shedule vs Default Schedule")

if known_plot:
    df.plot(x = 'Tensor', y = ['speedup'], ax = ax2, linestyle='-', marker='o', color = 'black', secondary_y=True, rot = rot, ylim = ax2_ylim, ylabel = "Speedup", xlabel = "Matrix/Tensor", legend = False)
else:
    df.plot(x = 'Tensor', y = ['speedup'], ax = ax2, linestyle='-', marker='o', color = 'black', secondary_y=True, rot = rot, ylabel = "Speedup", xlabel = "Matrix/Tensor")
# plt.ylabel("speedup")

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.right_ax.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc='best', ncol = 3)

# plt.xticks(rotation=45, ha='right')
plt.xlabel("Matrix/Tensor")
# plt.legend('lower right')   

# ax2.set_ylim(40, 160)

# plt.legend(bbox_to_anchor=(1.0, 1.0))

# plt.legend("upper center")
# ax.legend('upper center')
# ax2.legend([ax.get_lines(), ax2.get_lines()],\
#            ['A','B','C'], bbox_to_anchor=(1.5, 0.5))

# plt.show()
# df['speedup'].plot(kind='line', marker='d', secondary_y=True)
# plt.yscale("log")
plt.savefig(output_file, bbox_inches='tight',dpi=100)