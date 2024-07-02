#!/bin/bash

cwd=$(pwd)

# scale plots
# python scripts/scaling_exec_replace.py --directory $cwd/..
./scripts/scaling_exec.sh $cwd/.. &> $cwd/scaling.txt
# python3 scripts/scaling_exec.py --directory $cwd
# python3 scripts/plot_scale_graph.py --directory $cwd -t 1
# python3 scripts/plot_scale_graph.py --directory $cwd -t 2