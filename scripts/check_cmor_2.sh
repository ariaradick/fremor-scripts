#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=256G
#SBATCH --partition=analysis
#SBATCH --constraint=avx2
#SBATCH --output=/work/a3r/logs/cmor_check/cmor_check_%j.out
#SBATCH --error=/work/a3r/logs/cmor_check/cmor_check_%j.err

###############################################
# Parse args
###############################################

CATURL=$1
TABLEID=$2
VARID=$3
EXPID=$4
# STATSDIR=$5

###############################################
# Load conda + activate environment
###############################################
module load miniforge
conda activate /work/a3r/conda/envs/aria/

###############################################
# Run python script
###############################################
python /work/a3r/Documents/code/cmor_scripts/scripts/check_cmor_2.py \
    $CATURL \
    --table_id $TABLEID \
    --variable_id $VARID \
    --experiment_id $EXPID
    # --stats_dir $STATSDIR