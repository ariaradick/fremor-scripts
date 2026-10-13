import argparse
import subprocess
from pathlib import Path
import polars as pl

parser = argparse.ArgumentParser(
                prog='SPEAR CMOR Retraction',
                description='Remove datasets based on filtering from catalog'
            )

parser.add_argument('catalog_url')
parser.add_argument('--table_id', required=True)
parser.add_argument('--experiment_id', required=True)
parser.add_argument('--variable_id', required=True)
parser.add_argument('--log', default=None)

def main():
    args = parser.parse_args()

    catalog = pl.read_csv(args.catalog_url)

    subcat = catalog.filter(
        (pl.col('table_id') == args.table_id) &
        (pl.col('experiment_id') == args.experiment_id) &
        (pl.col('variable_id') == args.variable_id)
    )

    removed_files = [
        f"Removing {args.experiment_id}/{args.table_id}/{args.variable_id}",
        f"Input catalog file: {args.catalog_url}", 
        ""
    ]
    for p in subcat['path']:
        f = Path(p)
        if f.is_file():
            # answer = input(f"Delete file {p}?")
            # if answer.lower() in ["y", "yes"]:
            f.unlink()
            removed_files.append(f"Removed {p}")
            print(f"Removed file {p}")
            # else:
            #     continue
    
    if args.log is not None:
        with open(args.log, 'w') as f:
            for line in removed_files:
                f.write(f"{line}\n")


if __name__=='__main__':
    main()