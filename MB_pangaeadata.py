import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import glob
import csv as cf
import geopandas as gpd
import GlacierData_Plots1 as GLplots

# supress copy warning - careful 
pd.options.mode.chained_assignment = None  # default='warn'

# MWK mass balance data set:
# https://doi.pangaea.de/10.1594/PANGAEA.965719
# VK mass balance data set: 
# https://doi.pangaea.de/10.1594/PANGAEA.965729
# --> Download a zip file of all data sets in the collection and unpack the zip file. 

# set the file paths to the unpacked .tab files:
folder_MWK = 'pangaea_dl/MWK_MB/datasets/'
folder_VK = 'pangaea_dl/VK_MB/datasets/'

def getheader(f):
    # this is a loop to identify the header line in the pangaea format.
    with open(f, 'r') as fin:
        reader = cf.reader(fin)
        for idx, row in enumerate(reader):
            if row[0].startswith('*/'):
                headerline = idx+1
                print(row)
                print(idx)
                print('header found')
   
    data = pd.read_csv(f, header = headerline, parse_dates=True, delimiter='\t', index_col=0)
    return(data)

# load the quality controlled data from the yearly files:
def loadfiles(folder, gl, what):
    dfs = []
    # print(folder+gl+'_MB_'+what+'*.tab')
    fls = glob.glob(folder+gl+'_MB_'+what+'*.tab')
    for f in fls:
        data = getheader(f)
        dfs.append(data)

    data_merged = pd.concat(dfs).sort_index()
    data_merged['glacier'] = gl
    return(data_merged)


annualMWK = loadfiles(folder_MWK, 'MWK', 'annual')
interMWK = loadfiles(folder_MWK, 'MWK', 'inter')
winterMWK = loadfiles(folder_MWK, 'MWK', 'winter')
probingMWK = loadfiles(folder_MWK, 'MWK', 'probing')
probingMWK['Date/Time (end of period)'] = probingMWK.index

annualVK = loadfiles(folder_VK, 'VK', 'annual')
interVK = loadfiles(folder_VK, 'VK', 'inter')
winterVK = loadfiles(folder_VK, 'VK', 'winter')
probingVK = loadfiles(folder_VK, 'VK', 'probing')


probingVK['year'] = pd.to_datetime(probingVK['Date/Time (end of period)']).dt.year
probingMWK['year'] = pd.to_datetime(probingMWK['Date/Time (end of period)']).dt.year

probingVK['month'] = pd.to_datetime(probingVK['Date/Time (end of period)']).dt.month
probingMWK['month'] = pd.to_datetime(probingMWK['Date/Time (end of period)']).dt.month


# concat both glaciers into a combined dataframe:
an = pd.concat([annualVK, annualMWK])
winter = pd.concat([winterVK, winterMWK])
inter = pd.concat([interVK, interMWK])


an['year'] = pd.to_datetime(an['Date/Time (end of period)']).dt.year
winter['year'] = pd.to_datetime(winter['Date/Time (end of period)']).dt.year
inter['year'] = pd.to_datetime(inter['Date/Time (end of period)']).dt.year

# dictionary to translate between original and pangaea column names
namedict = {
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
    'MB raw [cm] (raw mass balance measurement)': 'mb_raw',
    'QF (Flag to indicate whether the ...)': 'probe_flag'
    }


def castdates_addname_gdf(df):
    df['date0'] = pd.to_datetime(df['date0'])
    df['date1'] = pd.to_datetime(df['date1'])
    df['name'] = df.index.astype(str)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(x=df.x_pos, y=df.y_pos, crs={'init': 'epsg:31255'})
    )
    return(gdf)

an_rn = an.rename(mapper=namedict, axis=1)
winter_rn = winter.rename(mapper=namedict, axis=1)
inter_rn = inter.rename(mapper=namedict, axis=1)

probingVK_rn = probingVK.rename(mapper=namedict, axis=1)
probingMWK_rn = probingMWK.rename(mapper=namedict, axis=1)


an_gdf = castdates_addname_gdf(an_rn)
winter_gdf = castdates_addname_gdf(winter_rn)
inter_gdf = castdates_addname_gdf(inter_rn)


# Figure 4:
GLplots.intermediate_stats_combined(inter_gdf, an_gdf, winter_gdf)

# Figure 5:
inter_gdf['doy'] = inter_gdf['date1'].dt.dayofyear
GLplots.plot_intermediate(inter_gdf)

# Figure 6:
GLplots.plot_annual_seasonal_elevation(winter_gdf, an_gdf, probingVK_rn, probingMWK_rn)


plt.show()

