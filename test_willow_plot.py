import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import os

# add a parser to get the test name from the command line
parser = argparse.ArgumentParser()
parser.add_argument('--test-name', type=str, help='The test name to plot', required=True, choices=['spmm_gemm_real', 'spttm_spttm_real'])
parser.add_argument('--directory', type=str, help='Path to taco directory')
args = parser.parse_args()
tst = args.test_name

# dir = '/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/'
dir = args.directory

# tst = 'spmm_gemm_real'
# tst = 'spttm_spttm_real'

# create a directory in f"{dir}/pigeon if it does not exist
if not os.path.exists(f"{dir}/pigeon"):
    os.makedirs(f"{dir}/pigeon")

file = f'{dir}/pigeon/test_1_0.csv'
image_name = f'{dir}/plots/spttm-spttm-results.pdf'
figsize = (4, 6)

if tst == 'spmm_gemm_real':
    file = f'{dir}/pigeon/test_0_0.csv'
    image_name = f'{dir}/plots/spmm-gemm-results.pdf'
    figsize = (9, 6)

# Read the CSV file into a DataFrame
df = pd.read_csv(file)

# remove .mtx of .tns from the data column values
df['data'] = df['data'].apply(lambda x: x.split('.')[0]).apply(lambda x: x[:8])
# crop data column values to have a length of 10
# df['data'] = df['data'].apply(lambda x: x[:10])

# Remove the 'iter_1' column
df.drop(columns=['iter_1'], inplace=True)

# Calculate the median of iter_2, iter_3, and iter_4 values for each row
df['median_iter'] = df[['iter_2', 'iter_3', 'iter_4']].median(axis=1)

print(df)

# Group by 'test_name' and 'data', then pick the minimum value from 'median_iter' column for each group
min_median_values = df.groupby(['test_name', 'data'])['median_iter'].min()

# Reset index to make groupby results accessible as columns
min_median_values = min_median_values.reset_index()

print(min_median_values)

# Normalize the median_iter values within each 'data' group
min_median_values['normalized_median_iter'] = min_median_values.groupby('data')['median_iter'].transform(lambda x: x / x[min_median_values['test_name'] == tst].values)

# change spmm_gemm_real and spmm_gemm_willow to SparseAuto and Ahrens et al. [2021] in the test_name column
min_median_values['test_name'] = min_median_values['test_name'].replace('spmm_gemm_real', 'SparseAuto').replace('spttm_spttm_real', 'SparseAuto')
min_median_values['test_name'] = min_median_values['test_name'].replace('spmm_gemm_willow', 'Pigeon').replace('spttm_spttm_willow', 'Pigeon')

# Define custom colors for the bars
custom_palette = {'SparseAuto': 'c', 'Pigeon': 'tab:pink'}

# Plotting
plt.figure(figsize=figsize)
sns.barplot(data=min_median_values, x='data', y='normalized_median_iter', hue='test_name', palette=custom_palette, width=0.7)

# change label size
plt.xticks(fontsize='16')
plt.yticks(fontsize='16')
plt.xlabel('Matrices/Tensors', fontsize='18')
plt.ylabel('Normalized\nExecution Time', fontsize='18')
plt.xticks(rotation=30)
plt.tight_layout()

# change y axis range
if (tst == 'spttm_spttm_real'):
    plt.ylim(0, 1.4)

# create new legend
plt.legend(title=None, fontsize='18', loc='upper right')

ax = plt.gca()
if (tst == 'spttm_spttm_real'):
    yticks = ax.yaxis.get_major_ticks()
    yticks[-1].set_visible(False)
    yticks[-2].set_visible(False)
    

# rename legend labels
# plt.legend(['SparseAuto', 'Pigeon'], title=None, title_fontsize='13', fontsize='12', loc='upper right')

# Save the figure
plt.savefig(image_name)

# save plt as pdf
# plt.savefig('spmm_gemm_results.pdf')