import pandas as pd
import matplotlib.pyplot as plt
from argparse import ArgumentParser, RawTextHelpFormatter
from enum import Enum

MAX_VALUE = 10000

class FontSize(Enum):
    SMALL_SIZE = 8
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 16
    
plt.rcParams.update({'font.size': FontSize.BIGGER_SIZE.value})

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-r', '--rotation', help='rotation of the tensors in x axis', required=False, default=45, type=int)
args = vars(parser.parse_args())
test = args["test"]
rot = args["rotation"]

if (test == 1):
    data_file = f'test8_results_64x64.csv'
    output_file = f'plots/test8_all_schedules_64x64.pdf'
elif (test == 2):
    data_file = f'test8_results_128x128.csv'
    output_file = f'plots/test8_all_schedules_128x128.pdf'
else:
    assert False

num_values = 3
column_headers = [f'{i}' for i in range(num_values)]

df = pd.read_csv(data_file, header=0, names=column_headers)

for i in range(num_values):
    col = f'{i}'
    df.loc[df[f'{i}'] == 0 , f'{i}'] = MAX_VALUE
    df.loc[df[f'{i}'] > MAX_VALUE, f'{i}'] = MAX_VALUE

print(df)
df['Time'] = df[column_headers].min(axis=1)
df['Schedule'] = [i for i in range(len(df))]
print(df)

print(df.index.values)

df = df.sort_values('Time')
# df['Schedule'] = [i for i in range(len(df))]
s_ours = df.loc[68]['Schedule']
t_ours = df.loc[68]['Time']
s_default = df.loc[38]['Schedule']
t_default = df.loc[38]['Time']
print(df.loc[68]['Time'])
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