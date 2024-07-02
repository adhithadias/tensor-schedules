from regex import findall
from statistics import median, stdev
import argparse

parser = argparse.ArgumentParser(description='Run sparseLNR tests')
parser.add_argument('--directory', type=str, help='Path to taco directory')
args = parser.parse_args()

print(parser)
directory = args.directory

file1 = open(f'{directory}/scaling.txt', 'r')

all_data = {}
data = []
count = 0
for line in file1:
    if ('kernel' in line):
        
        ls = line.split(',')
        kernel = ls[0].split(':')[1].strip(' ').replace('default_', '').replace('_real', '')
        dataset = ls[1].split(":")[1].strip(' ').strip('\n')
        threads = ls[2].split(':')[1].strip(' ').strip('\n')
        for line in file1:
            # print(line)
            nums = findall(r'\d+\.?\d*\n', line) # /^\d*\.?\d*$/
            if (len(nums) > 0):
                break
        values = []
        for line in file1:
            # print(line)
            nums = findall(r'\d+\.?\d*\n', line) # /^\d*\.?\d*$/
            if (len(nums) == 0):
                break
            values.append(float(nums[0].rstrip('\n')))
                
        med = 0
        stddev = 0
        try:
            med = median(values)
            stddev = stdev(values)
        except:
            break

        count += 1

        if (count % 2 == 0):
            data.extend([med, stddev, data[1]/med])
            # speedup = data[1] / data[3]
            # data.append(speedup)
            key = kernel + '_' + dataset
            if (key in all_data):
                all_data[key].append(data)
            else:
                all_data[key] = [data]
            # all_data.append(data)
            data = []
        else:
            data = [threads, med, stddev]

map = {
    'loopcontractfuse': '2',
    'sddmm_spmm': '3',
    'sddmm_spmm_gemm': '4',
    'spttm_ttm': '5',
    'spmmh_gemm': '7',
    'spmm_gemm': '8',
    'mttkrp_gemm': '9'
}

# print(all_data)

for key in all_data:
    print(key)
    header = 'threads,default_median,default_stddev,sparseauto_median,sparseauto_stddev,speedup\n'
    print(header, end='')
    f = open(f'{directory}/csv_results/scaletest_{key}_scaling.csv', "w")
    f.write(header)
    for row in all_data[key]:
        r = ','.join(str(round(x,2)) if type(x) == float else x for x in row)
        f.write(r + '\n')
        print(r)
    f.close()
