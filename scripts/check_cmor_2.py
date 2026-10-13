import argparse
import polars as pl
import numpy as np
import xarray as xr 
import dask

parser = argparse.ArgumentParser(
                prog='FRE CMOR checker',
                description='Verifies FRE CMOR output using catalogs to search for datasets'
            )

parser.add_argument('catalog_url')
parser.add_argument('--table_id', required=True)
parser.add_argument('--variable_id', required=True)
parser.add_argument('--experiment_id', required=True)
parser.add_argument('--stats_dir', default=('/work/a3r/Documents/catalog_thumbs/tftest/'))

args = parser.parse_args()

exp_id_dict = {
    'historical' : 'SPEAR_c192_o1_Hist_AllForc_IC1921_K50',
    'scenarioSSP5-85' : 'SPEAR_c192_o1_Scen_SSP585_IC2011_K50'
}

table_dict = {
    'psl' : {'6hr' : 'atmos_4xdaily'},
    'prsn' : {'6hr' : 'atmos_4xdaily_avg'},
    'tasmin' : {'day' : 'atmos_daily'},
    'tasmax' : {'day' : 'atmos_daily'}
}

var_names = {
    'psl' : 'slp',
    'prsn' : 'snow_tot',
    'tasmin' : 't_ref_min',
    'tasmax' : 't_ref_max'
}

columns = ['min', 'max', 'mean', 'std']

def get_member_id(variant_label):
    return "pp_ens_" + variant_label.split("i")[0][1:].zfill(2)

cmor_out_catalog = args.catalog_url
csv_base_path = args.stats_dir

cat_df = pl.read_csv(cmor_out_catalog)

# use cmorized values
var_id = args.variable_id
exp_id = args.experiment_id
table_id = args.table_id

subcat = cat_df.filter(
    (pl.col("variable_id") == var_id) &
    (pl.col("experiment_id") == exp_id) &
    (pl.col("table_id") == table_id)
)

in_csv = (csv_base_path +
    exp_id_dict[exp_id] + '/' +
    table_dict[var_id][table_id] + '/' +
    var_names[var_id] + '.csv')

out_csv = (csv_base_path +
    exp_id_dict[exp_id] + '/' +
    table_dict[var_id][table_id] + '/' +
    var_names[var_id] + '_cmor' + '.csv')

correct_values = pl.read_csv(in_csv)

are_values_correct = []

for grp,df in subcat.group_by("member_id"):
    variant_id = grp[0]
    # calculate min,max,mean,std

    if len(df['path']) == 1:
        ds = xr.open_dataset(
            df['path'][0], 
            chunks='auto',
            engine='netcdf4'
        )[var_id]
    else:
        ds = xr.open_mfdataset(
            df['path'], 
            parallel=True, 
            chunks='auto',
            engine='netcdf4'
        )[var_id]

    # test with just one time slice:
    # ds = xr.open_dataset(
    #     df['path'][0], 
    #     chunks='auto',
    #     engine='netcdf4'
    # )[var_id].isel(time=0)

    weights = np.cos(np.deg2rad(ds.lat))
    weights.name = "weights"
    avgval_lazy = ds.weighted(weights).mean()
    stdval_lazy = ds.weighted(weights).std()

    minval_lazy = ds.min()
    maxval_lazy = ds.max()

    cmor_values = np.array(dask.compute(
        minval_lazy,
        maxval_lazy,
        avgval_lazy,
        stdval_lazy
    ))

    expected_values = correct_values.filter(
        pl.col('member_id') == get_member_id(variant_id)
    ).select(pl.exclude('member_id')).to_numpy()

    # res = {i : j for i,j in zip(columns, (cmor_values == expected_values)[0])}
    res = {i : j for i,j in zip(columns, cmor_values)}
    res['match'] = np.isclose(cmor_values, expected_values).all()
    res['member_id'] = variant_id

    are_values_correct.append(res)

    # break

is_correct_df = pl.DataFrame(
    are_values_correct, 
    {
        'member_id' : str, 
        'min' : float, 
        'max' : float, 
        'mean' : float, 
        'std': float,
        'match': bool
    }
).select(correct_values.columns + ['match'])
is_correct_df.sort("member_id").write_csv(out_csv)