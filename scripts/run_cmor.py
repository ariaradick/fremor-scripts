import json
import shutil
import pathlib
import subprocess
# import os
import argparse
import polars as pl

basePath = (pathlib.Path(__file__).parent / '..').resolve()
batchPath = basePath / 'scripts' / 'run_cmor.sh'

parser = argparse.ArgumentParser(
                prog='FRE CMOR automator',
                description='Runs FRE CMOR using catalogs to search for datasets'
            )

parser.add_argument('catalog_url')
parser.add_argument('--realm', required=True)
parser.add_argument('--variable_id', required=True)
parser.add_argument(
    '--tmp_dir', 
    default=(basePath / 'tmp')
)
parser.add_argument('--out_dir', default='/work/a3r/CMIP6_output')
 
exp_id_dict = {
    'SPEAR_c192_o1_Hist_AllForc_IC1921_K50' : 'historical',
    'SPEAR_c192_o1_Scen_SSP585_IC2011_K50' : 'scenarioSSP5-85'
}

table_dict = {
    'atmos_4xdaily' : 'CMIP6_6hr.json',
    'atmos_4xdaily_avg' : 'CMIP6_6hr.json',
    'atmos_daily' : 'CMIP6_day.json',
    'atmos' : 'CMIP6_Amon.json'
}

def main():
    args = parser.parse_args()

    tmp_path = pathlib.Path(args.tmp_dir)
    print(tmp_path.resolve())

    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True)

    df = pl.read_csv(args.catalog_url)

    res = df.filter((pl.col("realm") == args.realm) &
            (pl.col("variable_id") == args.variable_id))
    # varList = {args.variable_id : args.variable_id}
    varList = {"omega" : "wap"}
    
    with open(tmp_path / 'varlist.json', 'w') as f:
        json.dump(varList, f)

    for name,data in res.group_by("experiment_id", "member_id"):
        print(name)
        exp_name = exp_id_dict[name[0]]
        member_id = name[1]
        linkDir = tmp_path / 'datasets' / exp_name / member_id
        linkDir.mkdir(parents=True)
        for p in data.get_column("path"):
            filePath = pathlib.Path(p)
            linkPath = linkDir / filePath.name
            linkPath.symlink_to(filePath)
        if args.variable_id:
            jobName = f"cmor.{args.variable_id}.{args.realm}.{exp_name}.{member_id}"
        else:
            jobName = f"cmor.{args.realm}.{exp_name}.{member_id}"
        logPath = '/'.join(['logs',exp_name,member_id,args.realm,jobName+'.%j'])
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
                basePath,
                linkDir,
                tmp_path / 'varlist.json',
                basePath / 'tables' / table_dict[args.realm],
                basePath / 'tables' / exp_name / f'{exp_name}_{member_id}.json',
                pathlib.Path(args.out_dir) / (args.realm+'.'+args.variable_id) / exp_name / member_id
            ]
        )
        break

if __name__=='__main__':
    main()
