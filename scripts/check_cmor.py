import pathlib
import argparse
import polars as pl
import xarray as xr

basePath = (pathlib.Path(__file__).parent / '..').resolve()

parser = argparse.ArgumentParser(
                prog='FRE CMOR checker',
                description='Verifies FRE CMOR output using catalogs to search for datasets'
            )

parser.add_argument('catalog_url')
parser.add_argument('--realm', required=True)
parser.add_argument('--variable_id', required=True)
parser.add_argument('--experiment_id', required=True)
parser.add_argument('--member_id', required=True)
parser.add_argument('--out_dir', default=('/work/a3r/CMIP6_output'))

exp_id_dict = {
    'historical' : 'SPEAR_c192_o1_Hist_AllForc_IC1921_K50',
    'scenarioSSP5-85' : 'SPEAR_c192_o1_Scen_SSP585_IC2011_K50'
}

var_names = {
    'slp' : 'psl'
}

def variant_label(member_id):
    variant_number = int(member_id[-2:])
    return f"r{variant_number}i1p1f1"

def get_cat_paths(cat_df, **kwargs):
    return cat_df.filter(**kwargs).get_column("path")

def get_output_paths(output_dir):
    outPathGlob = pathlib.Path(output_dir).glob('**/*')
    return [x for x in outPathGlob if x.is_file()]

def main():
    args = parser.parse_args()

    catUrl = args.catalog_url
    outDir = args.out_dir

    catFilter = {
        'realm' : args.realm,
        'experiment_id' : exp_id_dict[args.experiment_id],
        'variable_id' : args.variable_id,
        'member_id' : args.member_id
    }

    cat_df = pl.read_csv(catUrl)

    originalPaths = get_cat_paths(cat_df, **catFilter)
    newPaths = get_output_paths(pathlib.Path(outDir) / args.experiment_id / args.member_id)
    print(originalPaths)
    print(newPaths)

    ds_og = xr.open_mfdataset(originalPaths)
    ds_new = xr.open_mfdataset(newPaths)

    print("Running data verification for {args.experiment_id}, {args.member_id}")
    if (ds_og[args.variable_id] == ds_new[var_names[args.variable_id]]).all():
        print("Pass!")
    else:
        print("Fail!")

if __name__=='__main__':
    main()