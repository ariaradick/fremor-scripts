#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --partition=analysis

INPUT=$1
OUTDIR=$2

rsync -airnv $INPUT $OUTDIR