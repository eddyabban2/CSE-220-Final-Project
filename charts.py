import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

benchmarks = [       "x86-bubblesort",
    "lulesh",
    "x86-npb-lu-size-s",
    "x86-npb-ft-size-s",
    "x86-floatmm",
    "x86-npb-is-size-s",
    "x86-npb-cg-size-s",
    "x86-gapbs-tc",
    "x86-gapbs-bfs"]
branch_predictors =[
    "perceptron",
    "tournament",
    "BiModeBP"
]

def get_data(benchmark_name, predictor_type):
    file_path = f'gem5/results/{benchmark_name}_{predictor_type}/stats.txt'
    print(f"getting data for {file_path}")
    miss_count = 0
    prediction_count = 0
    hit_rate = 0
    cpi = 0
    run_time = 0
    with open(file_path, 'r') as file:
        for line in file:
            if(line.startswith("board.processor.cores0.core.branchPred.condIncorrect")):
                print(f"Found miss count line: {line.strip()}")
                miss_count = int(line.split()[1])
            if(line.startswith("board.processor.cores0.core.branchPred.condPredicted") and not line.startswith("board.processor.cores0.core.branchPred.condPredictedTaken")):
                prediction_count = int(line.split()[1])
                print(f"Found prediction count: {line.strip()}")
            if(line.startswith("board.processor.cores0.core.cpi")):
                cpi = float(line.split()[1])
                print(f"Found cpi line: {line.strip()}")
            if(line.startswith("simSeconds")):
                run_time = float(line.split()[1])
                print(f"Found simsecond line: {line.strip()}")

        hit_rate = 1 - (float(miss_count) / float(prediction_count))
    
    return {
        "benchmark": benchmark_name,
        "branch_predictor": predictor_type,
        "cpi": float(cpi),
        "branch prediction ratio": hit_rate,
        "run_time": float(run_time)
    }

def get_all_data():
    results = []
    for benchmark in benchmarks:
        for predictor in branch_predictors:
            data = get_data(benchmark, predictor)
            results.append(data)
    return results

def plot_metrics_by_benchmark(data):
    """Create plots with clustered bars: each cluster = benchmark, bars within = branch predictors"""
    metrics = ['cpi', 'branch prediction ratio', 'run_time']
    
    for metric in metrics:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Prepare data
        benchmark_names = benchmarks
        predictor_names = branch_predictors
        
        # Create a nested list: for each benchmark, get values for each predictor
        metric_values = []
        for benchmark in benchmark_names:
            bench_data = [d for d in data if d["benchmark"] == benchmark]
            values = [d[metric] for d in sorted(bench_data, key=lambda x: predictor_names.index(x["branch_predictor"]))]
            print(f"Values for {benchmark} - {metric}: {values}")
            metric_values.append(values)
        
        # Set up bar positions
        num_benchmarks = len(benchmark_names)
        num_predictors = len(predictor_names)
        cluster_width = 0.6
        bar_width = cluster_width / num_predictors
        
        x_positions = np.arange(num_benchmarks)
        
        # Plot bars for each predictor
        for pred_idx, predictor in enumerate(predictor_names):
            offsets = (pred_idx - (num_predictors - 1) / 2) * bar_width
            values = [metric_values[bench_idx][pred_idx] for bench_idx in range(num_benchmarks)]
            ax.bar(x_positions + offsets, values, bar_width, label=predictor, alpha=0.8)
        
        # Customize
        short_names = [b.replace("x86-", "").replace("size-s", "s") for b in benchmark_names]
        ax.set_xticks(x_positions)
        ax.set_xticklabels(short_names, rotation=45, ha='right')
        
        
        metric_label = metric.replace('_', ' ').title()
        if metric == 'run_time':
            metric_label = 'Runtime (seconds)'
            ax.set_ylabel('Instructions Per Second')
            ax.set_title(f'Instructions Per Second of Branch Predictors Across Benchmarks', fontweight='bold', fontsize=14)
        elif metric == 'branch prediction ratio':
            metric_label = 'Accuracy of Branch Predictors Across Benchmarks'
            ax.set_title(f'Accuracy of Branch Predictors Across Benchmarks', fontweight='bold', fontsize=14)
            ax.set_ylabel('Accuracy')
        elif metric == 'cpi':
            metric_label = 'Cycles Per Instruction (CPI)'
            ax.set_title(f'CPI of Branch Predictors Across Benchmarks', fontweight='bold', fontsize=14)
            ax.set_ylabel('Cycles Per Instruction (CPI)')
        else:
            ax.set_title(f'{metric_label} Across All Benchmarks and Predictors', fontweight='bold', fontsize=14)
            ax.set_ylabel(metric_label)
        
        ax.legend(title='Branch Predictor', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'metrics_{metric}_clustered.png', dpi=300, bbox_inches='tight')
        print(f"Saved: metrics_{metric}_clustered.png")
# Main execution
data = get_all_data()
for entry in data:
    print(entry)

# Generate visualizations
plot_metrics_by_benchmark(data)

