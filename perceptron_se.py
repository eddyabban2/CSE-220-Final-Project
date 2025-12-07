import time
import m5
import argparse
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

from m5.objects import PerceptronBP, TournamentBP, BiModeBP, LocalBP, SimpleBTB

from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)

'''
Example usage:
./build/ALL/gem5.opt \
    configs/example/gem5_library/perceptron_attempt2.py \
    --benchmark <benchmark_name> \
    --branch-predictor <predictor_type>

./build/ALL/gem5.opt \
    configs/example/gem5_library/perceptron_attempt2.py \
    --benchmark x86-bubblesort \
    --branch-predictor perceptron
'''

benchmark_choices = [
    "x86-bubblesort",
    "x86-linux-kernel-4.4.186",
    "lulesh",
    "x86-llvm-minisat",
    "x86-npb-lu-size-s",
    "x86-npb-ft-size-s",
    "x86-floatmm",
    "x86-npb-is-size-s",
    "x86-npb-cg-size-s",
    "x86-gapbs-tc",
    "x86-gapbs-bfs", 
    "x86-parsec-blackscholes",
    "x86-parsec-bodytrack",
    "x86-parsec-canneal",
    "x86-parsec-dedup",
    "x86-parsec-facesim"
]
branch_choices = [
    "perceptron",
    "tournament",
    "BiModeBP", 
    "LocalBP", 
]

size_choices = ["simsmall", "simmedium", "simlarge"]

parser = argparse.ArgumentParser(
    description="An example configuration script to run the npb benchmarks."
)

parser.add_argument(
    "--benchmark",
    type=str,
    required=True,
    help="Input the benchmark program to execute.",
    choices=benchmark_choices,
)

parser.add_argument(
    "--branch-predictor",
    type=str,
    required=True,
    help="Branch Predictor to use.",
    choices=branch_choices,
)

parser.add_argument(
    "--size",
    type=str,
    required=True,
    help="Simulation size the benchmark program.",
    choices=size_choices,
)

args = parser.parse_args()

# ============================================================================
# Branch Predictor Configuration Helper Function
# ============================================================================

def create_branch_predictor(predictor_type):
    """
    Create a branch predictor object based on the specified type.
    
    Args:
        predictor_type (str): The type of branch predictor to create.
                             Options: 'perceptron', 'tournament', 'tage'
    
    Returns:
        m5.objects: A branch predictor object configured with appropriate parameters.
    """
    if predictor_type == "perceptron":
        return PerceptronBP(
            tableSize=8192,
            historyLength=16,
            weightBits=8,
        )
    elif predictor_type == "tournament":
        # Tournament predictor combines local and global predictors
        return TournamentBP()
    elif predictor_type == "BiModeBP":
        return BiModeBP()
    elif predictor_type == "LocalBP":
        return LocalBP()
    else:
        raise ValueError(f"Unknown branch predictor type: {predictor_type}")

# Obtain the components.
cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=8,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="256KiB",
    l2_assoc=16,
    num_l2_banks=2,
)

memory = DualChannelDDR4_2400(size="3GiB")
processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, num_cores=2, isa=ISA.X86)

table_size = 4096
history_length = 16
weight_bits = 8

for core in processor.get_cores():
    sim_cpu = core.get_simobject()
    sim_cpu.branchPred = create_branch_predictor(args.branch_predictor)

# Add them to the board.
board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

if(args.benchmark.startswith("x86-parsec-")):
    resource_id = args.benchmark
    command = (
        f"cd /home/gem5/parsec-benchmark;"
        + "source env.sh;"
        + f"parsecmgmt -a run -p {args.benchmark} -c gcc-hooks -i {args.size}         -n 2;"
        + "sleep 5;"
        + "m5 exit;"
    )
    board.set_kernel_disk_workload(
        # The x86 linux kernel will be automatically downloaded to the
        # `~/.cache/gem5` directory if not already present.
        # PARSEC benchamarks were tested with kernel version 4.19.83
        kernel=obtain_resource(
            "x86-linux-kernel-4.19.83", 
            resource_version="1.0.0", 
            resource_directory="/gem5/.cache"
        ),
        # The x86-parsec image will be automatically downloaded to the
        # `~/.cache/gem5` directory if not already present.
        disk_image=obtain_resource(
            "x86-parsec", 
            resource_version="1.0.0", 
            resource_directory="/gem5/.cache"),
        readfile_contents=command,
    )
    simulator = Simulator(board=board)
    simulator.run()

else:
    binary = obtain_resource(resource_id=args.benchmark, resource_directory="/gem5/.cache")  # choose your SPLASH-2 benchmark

    # # optionally include arguments (many SPLASH2 binaries take a size parameter)
    board.set_se_binary_workload(
        binary
    )
    simulator = Simulator(board=board)
    simulator.run()

