#!/bin/bash

cwd=$(pwd)

# comparison against SpTTN
python3 scripts/ttmc_compare.py --directory=$cwd/..

# plot the comparison results
python3 scripts/ttmc_compare_line_plot.py -t 1 --directory $cwd/..
python3 scripts/ttmc_compare_line_plot.py -t 2 --directory $cwd/..