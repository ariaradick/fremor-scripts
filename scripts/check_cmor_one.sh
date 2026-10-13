#!/bin/bash
#SBATCH --time=08:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=256G
#SBATCH --partition=analysis
#SBATCH --constraint=avx2

###############################################
# Parse args
###############################################

CATURL=$1
REALM=$2
VARID=$3
EXPID=$4
MEMBER=$5
OUTDIR=$6

###############################################
# Load conda + activate environment
###############################################
module load miniforge
conda activate aria

###############################################
# Run python script
###############################################
python /work/a3r/Documents/code/cmor_scripts/scripts/check_cmor.py \
    $CATURL \
    --realm $REALM \
    --variable_id $VARID \
    --experiment_id $EXPID \
    --member_id $MEMBER \
    --out_dir $OUTDIR