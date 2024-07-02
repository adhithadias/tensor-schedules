#!/bin/bash

# Build our special version of taco

cwd=$(pwd)

cd $cwd/../sparseLNR
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j8
cd $cwd
