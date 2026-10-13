import argparse
import subprocess
from pathlib import Path
import polars as pl

cmip_path_template = [
    'institution_id', 
    'source_id', 
    'experiment_id', 
    'member_id',
    'table_id',
    'variable_id',
    'grid_label',
    'version_id'
]

parser = argparse.ArgumentParser(
                prog='CMOR data mover',
                description='Moves cmorized data described by an input catalog'
            )

parser.add_argument('catalog_url')
parser.add_argument(
    '--out_dir', 
    default=(
        '/data/2/GFDL-LARGE-ENSEMBLES/CMIP/'
    )
)
parser.add_argument(
    '--log_dir', 
    default=(
        '/work/a3r/logs/move_data'
    )
)

parser.add_argument(
    '-n',
    '--dry_run', 
    action='store_true'
)

parser.add_argument(
    '--run_one', 
    action='store_true'
)

def main(catalog, out_dir, log_dir, run_one=False, dry_run=False):

    if dry_run:
        batchPath = '/work/a3r/Documents/code/cmor_scripts/scripts/move_cmorized_data_dry.sh'
    else:
        batchPath = '/work/a3r/Documents/code/cmor_scripts/scripts/move_cmorized_data.sh'
    
    cat_df = pl.read_csv(catalog)

    for grp,df in cat_df.group_by(cmip_path_template):
        one_row = df.row(0, named=True)
        one_row['version_id'] = 'v20210201'
        toMove = str(Path(one_row['path']).parent) + '/*'
        print(grp)

        destination = out_dir + '/'.join(
            [one_row[x] for x in cmip_path_template]
        ) + '/'

        jobName = '.'.join([
            'move_data',
            one_row['variable_id'],
            one_row['table_id'],
            one_row['experiment_id'],
            one_row['member_id']
        ])

        logPath = str( Path(log_dir) / '/'.join([
            one_row['experiment_id'],
            one_row['member_id'],
            one_row['table_id'],
            jobName+'.%j'
        ]))
        
        subprocess.run(
            [
                "sbatch",
                "-J",
                jobName,
                "--output",
                logPath+'.out',
                "--error",
                logPath+'.err',
                batchPath,
                toMove,
                destination
            ]
        )

        if run_one:
            break

if __name__=='__main__':
    args = parser.parse_args()
    main(args.catalog_url, args.out_dir, args.log_dir, run_one=args.run_one,
        dry_run=args.dry_run)

