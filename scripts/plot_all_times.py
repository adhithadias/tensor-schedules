import pandas as pd
import matplotlib.pyplot as plt
from argparse import ArgumentParser, RawTextHelpFormatter
from enum import Enum
import numpy as np

MAX_VALUE = 10000

class FontSize(Enum):
    SMALL_SIZE = 8
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 16
    
plt.rcParams.update({'font.size': FontSize.BIGGER_SIZE.value})

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-r', '--rotation', help='rotation of the tensors in x axis', required=False, default=45, type=int)
parser.add_argument('-d', '--directory', help='directory', required=True, default='.', type=str)
parser.add_argument('-e', '--dimension', help='dimension', required=False, default=64, type=int)
args = vars(parser.parse_args())
test = args["test"]
rot = args["rotation"]
directory = args["directory"]
dimension = args["dimension"]

if (test == 1):
    data_file = f'{directory}/tensor-schedules/csv_results/test8_all_schedules_{dimension}x{dimension}.csv'
    output_file = f'{directory}/tensor-schedules/plots/fig11/test8_all_schedules_64x64.pdf'
elif (test == 2):
    data_file = f'{directory}/tensor-schedules/csv_results/test8_all_schedules_{dimension}x{dimension}.csv'
    output_file = f'{directory}/tensor-schedules/plots/fig11/test8_all_schedules_128x128.pdf'
else:
    assert False

num_values = 3
column_headers = [f'{i}' for i in range(num_values)]
column_headers = ["Time 1", "Time 2", "Time 3", "Median", "Std", "Config", "Stmt", "Schedule"]

df = pd.read_csv(data_file, header=0, names=column_headers)

for i in ['Time 1', 'Time 2', 'Time 3']:
    col = f'{i}'
    df.loc[df[f'{i}'] == 0 , f'{i}'] = MAX_VALUE
    df.loc[df[f'{i}'] > MAX_VALUE, f'{i}'] = MAX_VALUE

df['Time'] = df[['Time 1', 'Time 2', 'Time 3']].min(axis=1)
df['Schedule'] = [i for i in range(len(df))]
print(df)

mask = np.column_stack([df["Config"].str.contains(r"\('i', 'k', \('j',\), \('l',\)\)", na=False) for _ in df])
sparseauto_index = np.nonzero(mask.any(axis=1))

mask = np.column_stack([df["Config"].str.contains(r"\('i', 'l', 'j', 'k'\)", na=False) for _ in df])
default_index = np.nonzero(mask.any(axis=1))

our_schedule_idx = sparseauto_index[0][0]
taco_default_schedule_idx = default_index[0][0]

df = df.sort_values('Time')
# df['Schedule'] = [i for i in range(len(df))]
s_ours = df.loc[our_schedule_idx]['Schedule']
t_ours = df.loc[our_schedule_idx]['Time']
s_default = df.loc[taco_default_schedule_idx]['Schedule']
t_default = df.loc[taco_default_schedule_idx]['Time']
print(df.loc[our_schedule_idx]['Time'])
print(df)

fig = plt.figure()
ax = plt.gca()
plt.scatter(df['Schedule'], df['Time'], s=25, linewidths=0.22, marker='X', c='m')
plt.axhline(y=MAX_VALUE, color='maroon', linestyle='-')
plt.axhline(y=t_default, color='darkgoldenrod', linestyle='-')
plt.axhline(y=t_ours, color='darkolivegreen', linestyle='-')
plt.ylabel('Time (ms)')
# ax.get_xaxis().set_visible(False)
plt.xlabel('Schedules')
ax.set_yscale('log')
# ax.grid(axis='y', which='both')
ax.get_xaxis().set_tick_params(labelbottom=False)
# ax.set_xscale('log')

# df.plot.scatter(x='Schedule', y='Time', log=True)

plt.savefig(output_file, bbox_inches='tight')