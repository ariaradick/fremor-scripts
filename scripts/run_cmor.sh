#!/bin/bash
#SBATCH --time=08:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=160G
#SBATCH --partition=analysis
#SBATCH --constraint=avx2

###############################################
# Parse args
###############################################

WORKDIR=$1
INDIR=$2
VARLIST=$3
TABLE_CONFIG=$4
EXP_CONFIG=$5
OUTDIR=$6

###############################################
# Load conda + activate environment
###############################################
module load miniforge
conda activate /work/a3r/conda/envs/fremor_env

###############################################
# Move to working directory
###############################################
cd $WORKDIR

###############################################
# Run FRE CMOR
###############################################
fremor -vv run \
  --indir $INDIR \
  --varlist $VARLIST \
  --table_config $TABLE_CONFIG \
  --exp_config $EXP_CONFIG \
  --outdir $OUTDIR
  # --run_one


