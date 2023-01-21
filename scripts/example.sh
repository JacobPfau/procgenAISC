#!/bin/bash
for i in {0..20}; do for j in {0..4}; do mix=$(echo "scale=2; ${i}/20" | bc); python run_experiment.py --preset Smiles_testdivdis --user "cuda:3" --mix_rate $mix; done; done &
