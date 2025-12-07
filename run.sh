#! /bin/bash

benchmarks=(
    "x86-bubblesort"
    "lulesh"
    "x86-npb-lu-size-s"
    "x86-npb-ft-size-s"
    "x86-floatmm"
    "x86-npb-is-size-s"
    "x86-npb-cg-size-s"
    "x86-gapbs-tc"
    "x86-gapbs-bfs"
    # "x86-parsec-blackscholes"
    # "x86-parsec-bodytrack"
    # "x86-parsec-canneal"
    # "x86-parsec-dedup"
    # "x86-parsec-facesim"
)

branch_predictors=(
    "perceptron"
    "tournament"
    "BiModeBP"
)

# sleep 5
echo "running benchmarks with different branch predictors..."

count=0

for benchmark in "${benchmarks[@]}"; do
    for bp in "${branch_predictors[@]}"; do
        output_folder="results/${benchmark}_${bp}"
        echo "${output_folder}/stats.txt"
        if [ -s "${output_folder}/stats.txt" ]; then
            echo "it looks like this one has already been run: {$output_folder}/stats.txt, skipping..."
        else
            echo "Running benchmark: ${benchmark} with branch predictor: ${bp}"
            build/ALL/gem5.opt  \
                --outdir ${output_folder} \
                configs/example/gem5_library/perceptron_attempt2.py \
                --benchmark ${benchmark} --branch-predictor ${bp} --size simsmall > ${benchmark}-${bp}.stdout # & 
        fi
    done
done