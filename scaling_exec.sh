#!/bin/bash

# export TMPDIR=/home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/
unset TMPDIR
export USE_OPENMP=true
export _OPENMP=true
export ITERATIONS=32
# cmake -DOPENMP=ON -DCMAKE_BUILD_TYPE=Release ..

echo "running threads: 1 2 4 8 16 32, iterations: 32"

# 3 4 7 8
dataset=webbase-1M.mtx
for test in sddmm_spmm_real sddmm_spmm_gemm_real
do
    for threads in 1 2 4 8 16 32
    do
        export OMP_NUM_THREADS=$threads
        echo ""
        echo "kernel:default_$test, dataset: $dataset, threads: $threads"
        OMP_NUM_THREADS=$threads TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/$dataset /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.default_$test
        echo ""
        echo "kernel:$test, dataset: $dataset, threads: $threads"
        OMP_NUM_THREADS=$threads TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/$dataset /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.$test
        echo ""
    done
done

# 2 5 6 9
# 5 default_spttm_spttm_real does not work because of the sparse output
dataset=darpa1998.tns
for test in spttm_ttm_real mttkrp_gemm_real 
do
    for threads in 1 2 4 8 16 32
    do
        export OMP_NUM_THREADS=$threads
        echo ""
        echo "kernel:default_$test, dataset: $dataset, threads: $threads"
        OMP_NUM_THREADS=$threads TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/$dataset /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.default_$test
        echo ""
        echo "kernel:$test, dataset: $dataset, threads: $threads"
        OMP_NUM_THREADS=$threads TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/$dataset /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.$test
        echo ""
    done
done


# echo "running kernel:default_sddmm_spmm_real, dataset: bcsstk17.mtx, threads: 32, iterations: 32"
# sddmm_spmm_real sddmm_spmm_gemm_real spmmh_gemm_real spmm_gemm_real
# OMP_NUM_THREADS=32 TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/bcsstk17.mtx /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.sddmm_spmm_real

# loopcontractfuse_real spttm_ttm_real mttkrp_gemm_real 
# # vast-2015-mc1-3d.tns flickr-3d.tns nell-2.tns darpa1998.tns
# OMP_NUM_THREADS=32 TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/100_1k_1k_001.tns /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.mttkrp_gemm_real


# OMP_NUM_THREADS=1 ITERATIONS=10 TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/vast-2015-mc1-3d.tns /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.default_loopcontractfuse_real


# OMP_NUM_THREADS=32 ITERATIONS=10 TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/vast-2015-mc1-3d.tns /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.default_mttkrp_gemm_real

# OMP_NUM_THREADS=1 TENSOR_FILE=/home/min/a/kadhitha/workspace/my_taco/tensor-schedules/downloads/vast-2015-mc1-3d.tns /home/min/a/kadhitha/workspace/my_taco/sparseLNR/build/bin/taco-test --gtest_filter=workspaces.loopcontractfuse_real
