#!/bin/bash
#SBATCH --job-name=cmor
#SBATCH --output=logs/cmor.%j.out
#SBATCH --error=logs/cmor.%j.err
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G

module load miniforge
conda activate aria
python /work/a3r/Documents/code/cmor_scripts/scripts/run_cmor.py \
    'https://raw.githubusercontent.com/NOAA-GFDL/spear-flp/refs/heads/main/catalog_blue.csv' \
    --variable_id=slp \
    --experiment_id='SPEAR_c192_o1_Scen_SSP585_IC2011_K50' \
    --realm='atmos_4xdaily'