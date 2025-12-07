# CSE-220-Final-Project

# File Descriptions:
- BranchPredictor.py: Modified file from gem5/src/cpu/pred/BranchPredictor.py. Modified to include perceptron branch predictor
- charts.py: Script used to generate diagrams 
- Dockerfile: Docker Container used to run simulations
- perceptron_se.py: Script used to create gem5 simulation 
- perceptron.cc & perceptron.hh: Files used to define perceptorn, should be moved to gem5/src/cpu/pred if you wish to replicate our simulator
- run.sh: bash script used to quickly run multiple simulations 
- SConscript: Compilation script from gem5 that has been modified to include perceptron branch predictor