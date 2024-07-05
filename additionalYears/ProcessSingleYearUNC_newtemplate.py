import numpy as np
import pandas as pd
import Uncertainties as unc
import datetime as dt

# supress copy warning - careful!
pd.options.mode.chained_assignment = None  # default='warn'

# read formated files and reprocess uncertainties:


def loadfiles(gl, yr):
    path = '/Users/leahartl/Desktop/LTER/MWKVK_processing/outnew/'+yr+'_reprocess/'
    if gl =='MWK':
        annual = pd.read_csv(path + gl+'_MB_annual_LH_'+yr+'.csv', delimiter=';', parse_dates=True, decimal=',') #adjusted flags, MWK
    if gl =='VK':
        annual = pd.read_csv(path + gl+'_MB_annual_'+yr+'.csv', delimiter=';', parse_dates=True, decimal=',')
    inter = pd.read_csv(path + gl+'_MB_intermediate_'+yr+'.csv', delimiter=';', parse_dates=True, decimal=',')
    probe = pd.read_csv(path + gl+'_MB_probing_'+yr+'.csv', delimiter=';', parse_dates=True, decimal=',')
    winter = pd.read_csv(path + gl+'_MB_winter_'+yr+'.csv', delimiter=';', parse_dates=True, decimal=',')

    # dictionary to translate between original and pangaea column names
    coldict = {
    'Date/Time (begin of period)':'date0',
    'Date/Time (end of period)':'date1',
    'Name (stake, sounding, probing)': 'name',
    'Duration [days] (period length)': 'period',
    'Observer': 'source',
    'x [m] (x-position of stake, EPSG:31255)': 'x_pos',
    'y [m] (y-position of stake, EPSG:31255)': 'y_pos',
    'z [m] (elevation of stake)': 'z_pos',
    'QF date (quality identifier for date)': 'date_quality',
    'QF pos (quality identifier for position)': 'position_quality',
    'Dens snow/firn/ice [kg/m**3]': 'density',
    'QF rho (quality identifier for density)': 'density_quality',
    'QF pos (quality identifier for position)': 'position_quality',
    'MB point [mm w.e./kg/m**2]': 'mb_we',
    'QF measurement (quality identifier for stake ...)': 'measurement_quality',
    'Measurement type (type of mass balance observation)': 'measurement_type',
    'MB point unc [mm w.e.] (Uncertainty of point mass bal...)': 'mb_error',
    'Reading unc [mm w.e.] (Reading uncertainty of point ...)': 'reading_error',
    'Density unc [mm w.e.] (Density uncertainty of point ...)': 'density_error',
    'MB raw [cm] (raw mass balance measurement)': 'mb_raw'
    }


    inv_map = {v: k for k, v in coldict.items()}

    annual_rn = annual.rename(mapper=coldict, axis=1)
    

    # mit MSW klären: density quality flag
    print(annual_rn[['density','density_quality', 'density_error', 'mb_we']].head())

    annual_rn_u = unc.uncertainties(annual_rn, 'annual')
    print(annual_rn[['density','density_quality', 'density_error', 'mb_we']].head(18))


    inter_rn = inter.rename(mapper=coldict, axis=1)
    inter_rn_u = unc.uncertainties(inter_rn, 'annual')

    print(inter_rn[['density','density_quality', 'density_error', 'mb_we']].head())
    print(inter_rn_u[['density','density_quality', 'density_error', 'mb_we']].head())

    winter_rn = winter.rename(mapper=coldict, axis=1)
    winter_rn_u = unc.uncertainties(winter_rn, 'annual')

    print(winter_rn[['density','density_quality', 'density_error', 'mb_we']].head())
    print(winter_rn_u[['density','density_quality', 'density_error', 'mb_we']].head())

    probe_rn = probe.rename(mapper=coldict, axis=1)
    probe_rn_u = unc.uncertainties(probe_rn, 'annual')

    print(probe_rn[['density','density_quality', 'density_error', 'mb_we']].head())
    print(probe_rn_u[['density','density_quality', 'density_error', 'mb_we']].head())


    annual_rn_u.drop(columns=['time0', 'time1'], inplace=True)
    inter_rn_u.drop(columns=['time0', 'time1'], inplace=True)
    winter_rn_u.drop(columns=['time0', 'time1'], inplace=True)
    probe_rn_u.drop(columns=['time0', 'time1'], inplace=True)
    
    
    annual_rn_u.rename(mapper=inv_map, axis=1).to_csv('MWK_MB_annual_2023_2.csv', index=False)
    inter_rn_u.rename(mapper=inv_map, axis=1).to_csv('MWK_MB_inter_2023_2.csv', index=False)
    winter_rn_u.rename(mapper=inv_map, axis=1).to_csv('MWK_MB_winter_2023_2.csv', index=False)
    probe_rn_u.rename(mapper=inv_map, axis=1).to_csv('MWK_MB_probe_2023_2.csv', index=False)



loadfiles('MWK', '2023')
