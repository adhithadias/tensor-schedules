import pandas as pd
from matplotlib import pyplot as plt
from itertools import cycle, islice
from argparse import ArgumentParser, RawTextHelpFormatter
from enum import Enum
from textwrap import wrap

class FontSize(Enum):
    SMALL_SIZE = 8
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 16
    
plt.rcParams.update({'font.size': FontSize.BIGGER_SIZE.value})

# Set the figure size

# plt.rcParams["figure.autolayout"] = True

parser = ArgumentParser(description='Stores multiple configurations into a json file specified by a configuration json file', usage="python3 -m src.main_store_json -f [configuration file(s)] [optional arguments]", formatter_class=RawTextHelpFormatter)
parser.add_argument('-t', '--test', help='test number', required=False, default=2, type=int)
parser.add_argument('-r', '--rotation', help='rotation of the tensors in x axis', required=False, default=0, type=int)
parser.add_argument('--directory', type=str, help='Path to taco directory')
args = vars(parser.parse_args())
test = args["test"]
rot = args["rotation"]
directory = args["directory"]

csv_directory = directory + "/tensor-schedules/csv_results/"

# Make a list of columns
columns = ['Dense Dimensions', 'SparseAuto;L=16', 'Cyclops;L=16', 'SparseAuto;L=32', 'Cyclops;L=32', 'SparseAuto;L=64', 'Cyclops;L=64', 'SparseAuto;L=128', 'Cyclops;L=128']

if test == 1:
    csv = f"{csv_directory}/ttmc_compare_nell2.csv"
    output = f"{directory}/tensor-schedules/plots/fig10/ttmc_compare_nell2.pdf"
    title = "SparseAuto vs. SpTTN-Cyclops on nell-2"
    plt.rcParams["figure.figsize"] = [6, 5]
    labels = ["M=16;N=16", "M=32;N=32", "M=64;N=64", "M=128;N=128"]
else:
    csv = f"{csv_directory}/ttmc_compare_flickr.csv"
    output = f"{directory}/tensor-schedules/plots/fig10/ttmc_compare_flickr.pdf"
    title = "SparseAuto vs. SpTTN-Cyclops on flickr"
    plt.rcParams["figure.figsize"] = [6, 4.7]
    labels = ["M=16;N=16", "M=32;N=32", "M=64;N=64"]


# Read a CSV file
df = pd.read_csv(csv, usecols=columns)

# my_colors =['orange', 'orange', 'red', 'red', 'darkolivegreen', 'darkolivegreen', 'blueviolet', 'blueviolet']
my_colors =['orange', 'red', 'darkolivegreen', 'blueviolet']
# my_colors = list(islice(cycle(['orange', 'orange', 'red', 'red', 'pink', 'pink', 'blueviolet', 'blueviolet']), None, len(df)))

# - solid, -- dashed, -. dashdot, : dotted
# line_style = ['--', ':', '--', ':', '--', ':', '--', ':']
line_style = ['--', ':', '-.', '-']
# line_style = list(islice(cycle(['-', '--']), None, len(df)))

df['L=16'] = df['Cyclops;L=16'] / df['SparseAuto;L=16']
df['L=32'] = df['Cyclops;L=32'] / df['SparseAuto;L=32']
df['L=64'] = df['Cyclops;L=64'] / df['SparseAuto;L=64']

if test == 1:
    df['L=128'] = df['Cyclops;L=128'] / df['SparseAuto;L=128']
    y_fields = ['L=16', 'L=32', 'L=64', 'L=128']
else:    
    df['L=128'] = df['Cyclops;L=128'] / df['SparseAuto;L=128']
    y_fields = ['L=16', 'L=32', 'L=64']

logy = False
# y_fields = ['SparseAuto;L=16', 'Cyclops;L=16', 'SparseAuto;L=32', 'Cyclops;L=32', 'SparseAuto;L=64', 'Cyclops;L=64', 'SparseAuto;L=128', 'Cyclops;L=128']
# logy = True

# Plot the lines
# fontsize = 8
df.plot(x='Dense Dimensions', y=y_fields, logy=logy, color=my_colors, style=line_style, linewidth=2, marker='x', markersize=7)

# if test == 1:
plt.axhline(y=1.0, color='black', linestyle='-', linewidth=2.0)

plt.xlabel("Dense Dimensions")
plt.ylabel("Speedup over\nSpTTN-Cyclops")
plt.title(title)

labels = [l.replace(';', '\n') for l in labels]
plt.xticks([i for i,_ in enumerate(labels)], labels, rotation=args["rotation"])

plt.savefig(output, bbox_inches='tight',dpi=100)
# plt.show()