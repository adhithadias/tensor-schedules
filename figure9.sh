#!/bin/bash

cwd=$(pwd)

# comparison against willow
python3 scripts/test_willow.py --directory $cwd/..
python3 scripts/test_willow_plot.py --directory $cwd --test-name spmm_gemm_real
python3 scripts/test_willow_plot.py --directory $cwd --test-name spttm_spttm_real