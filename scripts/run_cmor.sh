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
# conda activate /nbhome/Jake.Zappala/conda/envs/fre-jake
conda activate /work/a3r/conda/envs/fremor_env
# conda activate /nbhome/fms/conda/envs/fremor-0.9.7
# module load fremor/0.9.7

###############################################
# Move to working directory
###############################################
cd $WORKDIR

fremor -vv run \
  --indir $INDIR \
  --varlist $VARLIST \
  --table_config $TABLE_CONFIG \
  --exp_config $EXP_CONFIG \
  --outdir $OUTDIR \
  --run_one

###############################################
# Run FRE CMOR
###############################################
# fre -vv cmor run \
#   --indir $INDIR \
#   --varlist $VARLIST \
#   --table_config $TABLE_CONFIG \
#   --exp_config $EXP_CONFIG \
#   --outdir $OUTDIR