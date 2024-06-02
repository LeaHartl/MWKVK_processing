import numpy as np
import pandas as pd
import datetime as dt
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as seaborn
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from shapely.geometry import Point
import glob

import Uncertainties as unc

# read BS and MS' shapefiles files of probing data and glacier wide mass balance
# reformat probe data to match GLAMOS tables as much as possible and export
# make plots of glacier wide / elevation zone mass balance: for winter and annual MB and each glacier,
# produce one figure with subplots for each year in the time series (4 figures in total)


# read the data tables for intermediate and annual point data (produced in ProcessExcl.py):
def readFiles(fn, glac):
    colnames = ['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality', 'x_pos', 'y_pos', 'z_pos',
                'position_quality', 'mb_raw', 'density', 'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                'mb_error', 'reading_error', 'density_error', 'source']
    dat = pd.read_csv(fn, skiprows=4, sep='\t', names=colnames)
    dat['date0'] = pd.to_datetime(dat['date0'], format='%Y%m%d')
    dat['date1'] = pd.to_datetime(dat['date1'], format='%Y%m%d')
    dat['year'] = dat['date1'].dt.year
    dat['glacier'] = glac

    gdf_dat = gpd.GeoDataFrame(dat, geometry=gpd.points_from_xy(dat.x_pos, dat.y_pos), crs="EPSG:31255") # check EPSG!!
    return(gdf_dat)


# load and process the probing data from initial shapefiles
def ProcessProbes(glac, df, df_p, an, winter, what):

    prbs = pd.DataFrame(columns=['NAME', 'Wert', 'X', 'Y', 'Z', 'probe_flag', 'date1', 'yr'])

    for i, y in enumerate(df['year'].values):

        f = df['fname'].loc[df['year']==y].values[0]
        shp = gpd.read_file(f)
        shp.to_crs(an.crs, inplace=True)

        # deal with iconsistent column names
        shp = shp.rename(columns={"WW": "Wert"})
        shp = shp.rename(columns={"Akk": "Wert"})
        shp = shp.rename(columns={"mHOEHE": "Wert"})
        shp = shp.rename(columns={"WW_1": "Wert"})
        shp = shp.rename(columns={"WW1": "Wert"})
        shp = shp.rename(columns={"Abl": "Wert"})
        shp = shp.rename(columns={"mb": "Wert"})

        shp = shp.rename(columns={"Hoehe": "z_pos"})
        shp = shp.rename(columns={"HStufe": "z_pos"})
        shp = shp.rename(columns={"RASTERVALU": "z_pos"})

        if what == 'annual':
            # ensure consistent units
            shp.Wert = shp.Wert.astype('float')*10
            # uncomment to save as new .shp
            # shp.to_file('figs/'+glac+'_maps/'+str(y)+'_'+glac+'_'+what+'.shp')

            an2 = an.loc[(an.glacier == glac) & (an.year == y)]

            if (y > 2007) & (y < 2022):
                f_prb = df_p['fname'].loc[df_p['year']==y].values[0]
                prb = gpd.read_file(f_prb)
                prb.to_crs(shp.crs, inplace=True)

                prb = prb.rename(columns={"WW": "mb_we"})
                prb = prb.rename(columns={"Akk": "mb_we"})
                prb = prb.rename(columns={"Sondierung": "mb_we"})
                prb = prb.rename(columns={"WWSondieru": "mb_we"})
                prb = prb.rename(columns={"RASTERVALU": "z_pos"})
                prb = prb.rename(columns={"HStufe": "z_pos"})
                prb = prb.rename(columns={"dgm08": "z_pos"})
                prb = prb.rename(columns={"POINT_X": "X"})
                prb = prb.rename(columns={"POINT_Y": "Y"})

                prb.mb_we = pd.to_numeric(prb.mb_we, errors='coerce')

                if glac == 'MWK':
                    prb['name'] = 'nan'

                prb.to_crs(an.crs, inplace=True)
                prb['probe_flag'] = 0
                prb['date1'] = str(y) + '0930'
                prb['yr'] = y

                prb = prb.rename(columns={"NAME": "name"})

                joined = prb.sjoin_nearest(shp, how="left")
                joined['upperbound'] = joined['Wert']+100
                joined['lowerbound'] = joined['Wert']-100

                joined['probe_flag'] = 0

                joined['probe_flag'].loc[(joined.mb_we < joined.lowerbound) | (joined.mb_we > joined.upperbound)] = 1
                joinedsub = joined#[['NAME', 'Wert_left', 'X', 'Y', 'Z', 'probe_flag']]
                joinedsub = joinedsub.rename(columns={"mb_we_left": "mb_we"})
                joinedsub = joinedsub.rename(columns={"z_pos_left": "z_pos"})
                joinedsub = joinedsub.rename(columns={"NAME": "name"})
                joinedsub['date1'] = str(y) +'0930'
                joinedsub['yr'] = y

                # probes and shape
                prbs = pd.concat([prbs, joinedsub])

        if what == 'winter':

            shp.Wert = shp.Wert.astype('float')
            if (glac == 'MWK') & (y > 2007):
                shp.Wert = shp.Wert.astype('float')*10

            f_prb = df_p['fname'].loc[df_p['year']==y].values[0]
            prb = gpd.read_file(f_prb)
            prb.to_crs(an.crs, inplace=True)
            shp.to_crs(an.crs, inplace=True)

            prb = prb.rename(columns={"WW": "mb_we"})
            prb = prb.rename(columns={"Akk": "mb_we"})
            prb = prb.rename(columns={"Sondierung": "mb_we"})
            prb = prb.rename(columns={"WWSondieru": "mb_we"})
            prb = prb.rename(columns={"RASTERVALU": "z_pos"})
            prb = prb.rename(columns={"dgm08": "z_pos"})
            prb = prb.rename(columns={"HStufe": "z_pos"})
            prb = prb.rename(columns={"POINT_X": "X"})
            prb = prb.rename(columns={"POINT_Y": "Y"})

            prb.mb_we = pd.to_numeric(prb.mb_we, errors='coerce')
            if glac == 'MWK':
                    prb['name'] = 'nan'

            win = winter.loc[(winter.glacier == glac) & (winter.year == y)]
            joined = prb.sjoin_nearest(shp, how="left")#, predicate="within")

            joined['upperbound'] = joined['Wert']+100
            joined['lowerbound'] = joined['Wert']-100

            joined['probe_flag'] = 0

            joined['probe_flag'].loc[(joined.mb_we < joined.lowerbound) | (joined.mb_we > joined.upperbound)] = 1
            joinedsub = joined#[['NAME', 'Wert_left', 'X', 'Y', 'Z', 'probe_flag']]
            joinedsub = joinedsub.rename(columns={"mb_we_left": "mb_we"})
            joinedsub = joinedsub.rename(columns={"z_pos_left": "z_pos"})
            joinedsub = joinedsub.rename(columns={"NAME": "name"})

            joinedsub['date1'] = str(y) +'0430'
            joinedsub['yr'] = y

            # probes and shape
            # bad = joined.loc[(joined.mb_we < joined.lowerbound) | (joined.mb_we > joined.upperbound)]
            prbs = pd.concat([prbs, joinedsub])

    return(prbs[['name', 'mb_we', 'X', 'Y', 'z_pos', 'probe_flag', 'date1', 'yr', 'lowerbound', 'upperbound', 'Wert']])


def MakeMapsSubplots(glac, df, df_p, an, winter, cmap, vmin, vmax, what):
    lns = []
    pts = []
    if what == 'annual':
        divnorm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter = 0, vmax=vmax)

    if glac == 'VK':
        yrs = np.arange(2012, 2024)
        row = 4
        col = 3
    if glac == 'MWK':
        yrs = np.arange(2007, 2024)
        row = 3
        col = 6

    fig, ax = plt.subplots(row, col, figsize=(8, 8), sharey=True, sharex=True)
    ax = ax.flatten()

    for i, y in enumerate(df['year'].values):
        ax[i].set_title(str(y))

        f = df['fname'].loc[df['year']==y].values[0]
        shp = gpd.read_file(f)
        shp.to_crs(an.crs, inplace=True)

        shp = shp.rename(columns={"WW": "Wert"})
        shp = shp.rename(columns={"Akk": "Wert"})
        shp = shp.rename(columns={"mHOEHE": "Wert"})
        shp = shp.rename(columns={"WW_1": "Wert"})
        shp = shp.rename(columns={"WW1": "Wert"})
        shp = shp.rename(columns={"Abl": "Wert"})
        shp = shp.rename(columns={"mb": "Wert"})

        if what == 'annual':
            
            shp.Wert = shp.Wert.astype('float')*10
            if (glac == 'MWK') & (y == 2023):
                shp.Wert = shp.Wert.astype('float')/10
            
            shp.plot(ax=ax[i], column='Wert', alpha=1, cmap=cmap, norm=divnorm, legend=False, zorder=8)#, norm=norm_w)# zorder=i+1

            an_stk = an.loc[(an.glacier == glac) & (an.year == y) & (an['measurement_type'] == 1)]
            an_pits = an.loc[(an.glacier == glac) & (an.year == y) & (an['measurement_type'] == 2)]

            an_stk.plot(ax=ax[i], column='mb_we', alpha=1, edgecolor='k', linewidth=0.5, marker='o',
                cmap=cmap, norm=divnorm, legend=False, zorder=10)

            an_pits.plot(ax=ax[i], column='mb_we', alpha=1, edgecolor='k', linewidth=0.5, marker='s',
                cmap=cmap, norm=divnorm, legend=False, zorder=12)

            fig.subplots_adjust(right=0.8)
            cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
            sm = plt.cm.ScalarMappable(cmap='RdBu', norm=divnorm)
            cbar = fig.colorbar(sm, cax=cbar_ax)
            cbar.set_label('Annual mass balance (mm w.e.)')
            cbar.ax.set_yscale('linear')
        
        if what == 'winter':

            bounds_w = np.arange(0, 2400, 200)
            norm_w = mcolors.BoundaryNorm(boundaries=bounds_w, ncolors=256, extend='both')

            if (glac == 'MWK') & (y > 2007) & (y < 2023):
                shp.Wert = shp.Wert.astype('float')*10

            shp.Wert = shp.Wert.astype('float')
            shp['upperbound'] = shp['Wert']+100
            shp['lowerbound'] = shp['Wert']-100

            f_prb = df_p['fname'].loc[df_p['year']==y].values[0]
            prb = gpd.read_file(f_prb)
            prb.to_crs(an.crs, inplace=True)
            shp.to_crs(an.crs, inplace=True)

            prb = prb.rename(columns={"WW": "Wert"})
            prb = prb.rename(columns={"Akk": "Wert"})
            prb = prb.rename(columns={"Sondierung": "Wert"})
            prb = prb.rename(columns={"WWSondieru": "Wert"})
            prb = prb.rename(columns={"mb": "Wert"})
            prb.Wert = pd.to_numeric(prb.Wert, errors='coerce')

            win = winter.loc[(winter.glacier == glac) & (winter.year == y)]

            joined = prb.sjoin_nearest(shp, how="left")#

            joined2 = win.sjoin_nearest(shp, how="left")
            joined2['upperbound'] = joined2['Wert']+100
            joined2['lowerbound'] = joined2['Wert']-100

            shp.plot(ax=ax[i], column='Wert', alpha=1, cmap=cmap, legend=False, norm=norm_w)# zorder=i+1)

            prb.plot(ax=ax[i], column='Wert', alpha=1, markersize=2, linewidth=0.1, edgecolor='k',
                     cmap=cmap, legend=False, norm=norm_w)# zorder=i+1)

            win.plot(ax=ax[i], column='mb_we', alpha=1, edgecolor='k', linewidth=0.5, marker='s',
                     cmap=cmap, legend=False, zorder=10, norm=norm_w)

            fig.subplots_adjust(right=0.8)
            cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_w)
            cbar = fig.colorbar(sm, cax=cbar_ax)
            cbar.set_label('Winter mass balance (mm w.e.)')

        for a in ax:
            if glac == 'VK':
                a.set_xticks([-75000, -77000])
                a.set_yticks([220000, 221000])
                a.set_ylim([219500, 222000])
                a.set_xlim([-77500, -74100])
                a.tick_params(axis='both', labelsize=10)

            if glac == 'MWK':
                a.set_xticks([-72000, -73000])
                a.set_ylim([215300, 218100])
                a.set_xlim([-73400, -71450])
                a.tick_params(axis='both', labelsize=8)

        if glac == 'MWK':   
            ax[-6].set_xlabel('m')
            ax[-5].set_xlabel('m')
            ax[-4].set_xlabel('m')
            ax[-3].set_xlabel('m')
            ax[-2].set_xlabel('m')
            ax[-1].set_xlabel('m')
            ax[0].set_ylabel('m')
            ax[6].set_ylabel('m')
            ax[12].set_ylabel('m')
            # ax[12].set_ylabel('m')

        if glac == 'VK':   
            ax[9].set_xlabel('m')
            ax[10].set_xlabel('m')
            ax[0].set_ylabel('m')
            ax[3].set_ylabel('m')
            ax[6].set_ylabel('m')
            ax[9].set_ylabel('m')
                
        if glac == 'MWK':
            ax[-1].set_axis_off()

    fig.savefig('figs/'+glac+'_'+what+'_maps_subplots_2023.png', dpi=200, bbox_inches='tight')
    print('fig saved')


def loadShapes(glac, an, winter):

    if glac == 'MWK':
        pathProbes = glac+'/LTER/Sondierungen_shp_LTER'
        pathGlaciers = glac+'/LTER/MB_shp_LTER/'

        flsProbes = glob.glob(pathProbes+'/*.shp')
        flsGlaciers = glob.glob(pathGlaciers+'/*.shp')

        df = pd.DataFrame(columns=['fname', 'year'])
        df['fname'] = flsGlaciers

        df_p = pd.DataFrame(columns=['fname', 'year'])
        df_p['fname'] = flsProbes

        df['year'] = df['fname'].str[-8:-4]
        df['year'] = df['year'].astype(int) 
        df['type'] = df['fname'].str[-21:-9]
 
        df_p['year'] = df_p['fname'].str[-8:-4]
        df_p['year'] = df_p['year'].astype(int)
        df_p['type'] = df_p['fname'].str[31:-9]

        df.sort_values(by=['year'], inplace=True)
        df_p.sort_values(by=['year'], inplace=True)

        df_Winter = df.loc[df.type=='Winterbilanz']
        df_Annual = df.loc[df.type=='Massenbilanz']

        df_Winter_p = df_p.loc[df_p.type=='Frühjahrssondierung']
        df_Annual_p = df_p.loc[df_p.type=='Herbstsondierung']

    if glac == 'VK':
        pathProbes = glac+'/Sondierungen'
        pathGlaciers = glac+'/MB-all'

        flsProbes = glob.glob(pathProbes+'/*Z.shp')

        flsGlaciers = glob.glob(pathGlaciers+'/*.shp')

        df = pd.DataFrame(columns=['fname', 'year'])
        df['fname'] = flsGlaciers
        df['year'] = '20'+df['fname'].str[-9:-7]
        df['year'] = df['year'].astype(int)
        df['type'] = df['fname'].str[-6:-4]

        df_p = pd.DataFrame(columns=['fname', 'year'])
        df_p['fname'] = flsProbes

        df_p['year'] = '20'+df_p['fname'].str[-7:-5]
        df_p['year'] = df_p['year'].astype(int)
        df_p['type'] = df_p['fname'].str[16:-8]

        df.sort_values(by=['year'], inplace=True)
        df_p.sort_values(by=['year'], inplace=True)

        df_Winter = df.loc[df.type=='WB']
        df_Annual = df.loc[df.type=='MB']

        df_Winter_p = df_p.loc[df_p.type=='Frühjahr']
        df_Annual_p = df_p.loc[df_p.type=='Herbst']

    cmap_w = 'cividis_r'
    vmin_w = 0
    vmax_w = 2200

    cmap_s = 'RdBu'
    vmin_s = -5000
    vmax_s = 1000


    # MakeMapsSubplots(glac, df_Annual, df_Annual_p, an, winter, cmap_s, vmin_s, vmax_s, 'annual')

    # MakeMapsSubplots(glac, df_Winter, df_Winter_p, an, winter, cmap_w, vmin_w, vmax_w,  'winter')

    prbAnnual = ProcessProbes(glac, df_Annual, df_Annual_p, an, winter, 'annual')
    prbWinter = ProcessProbes(glac, df_Winter, df_Winter_p, an, winter, 'winter')

    prbsAll = pd.concat([prbAnnual, prbWinter])



    prbsAll['date_quality'] = 3 # start date unknown, end date exactly known (fixed date probing)
    prbsAll['measurement_quality'] = 5 # 5 is for "reconstructed value (other reason)" to indicate extrapolation to fixed date
    prbsAll['measurement_type'] = 3 # glamos uses 2 (same as for snow pits). using 3 as a different category for our data set.
    prbsAll['density_quality'] = 3 # Density of snow/firn estimated from nearby measurements, uncertainty 8%

    prbsAll['mb_error'] = np.nan # initialize column - this is filled in a later step in Uncertainties.py
    prbsAll['reading_error'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    prbsAll['density_error'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    prbsAll['mb_raw'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    prbsAll = prbsAll.rename(columns={"X": "x_pos"})
    prbsAll = prbsAll.rename(columns={"Y": "y_pos"})

    if glac=='VK':
        prbsAll['source'] = 'BS'
    if glac=='MWK':
        prbsAll['source'] = 'MSW'
    # probes with uncertainties:
    # print(prbsAll.head())
    # print(prbsAll.columns)
    prbsAll_u = unc.uncertainties(prbsAll, 'probe')


    # prbsAll_u.to_csv(glac+'/'+glac+'_probeData1.csv')
    writetofile(prbsAll_u, glac, '2023')


def writetofile(dat, gl, y):
    print('hier',dat)

    fn = 'outnew/Vorlage_'+gl+'_MB_probing_'+y+'.csv'
    fnex = 'outnew/Vorlage_'+gl+'_MB_probing_'+y

    print(dat.head())

    dat['Date/Time (begin of period)'] = 'NaN'#dat['date0'].astype(str)+ ' ' +dat['time0'].astype(str)


    dat['Date/Time (end of period)'] = dat['date1'].astype(str)
    dat['Date/Time (end of period)'] = pd.to_datetime(dat['Date/Time (end of period)'], errors='coerce')
    dat = dat.loc[dat['Date/Time (end of period)'].dt.year == int(y)]
    dat['Date/Time (end of period)'] = dat['Date/Time (end of period)'].dt.strftime('%Y-%m-%dT%12:%00')
    print(dat.tail())
    

    dat = dat.rename(columns={"name": 'Name (stake, sounding, probing)', "period": "Duration [days] (period length)", "source":"Observer"})
    dat = dat.rename(columns={"x_pos": "x [m] (x-position of stake, EPSG:31255)", "y_pos": "y [m] (y-position of stake, EPSG:31255)", "z_pos":"z [m] (elevation of stake)"})
    dat = dat.rename(columns={"date_quality": "QF date (quality identifier for date)", "position_quality": "QF pos (quality identifier for position)", "density":"Dens snow/firn/ice [kg/m**3]"})
    dat = dat.rename(columns={"density_quality": "QF rho (quality identifier for density)", "position_quality": "QF pos (quality identifier for position)", "density":"Dens snow/firn/ice [kg/m**3]"})
    dat = dat.rename(columns={"mb_we": "MB point [mm w.e./kg/m**2]", "measurement_quality": "QF measurement (quality identifier for stake ...)", "measurement_type'":"Measurement type (type of mass balance observation)"})
    dat = dat.rename(columns={"mb_error": "MB point unc [mm w.e.] (Uncertainty of point mass bal...)", "reading_error": "Reading unc [mm w.e.] (Reading uncertainty of point ...)", "density_error":"Density unc [mm w.e.] (Density uncertainty of point ...)"})
    dat = dat.rename(columns={"mb_raw": "MB raw [cm] (raw mass balance measurement)"})
    print(dat)
    
    dat = dat.rename(columns={"probe_flag": "QF (Flag to indicate whether the ...)"})

    

    dat = dat.drop(['date0', 'time0', 'date1', 'time1'], axis=1)
    dat = dat[['Name (stake, sounding, probing)', 'Date/Time (begin of period)', 'Date/Time (end of period)',
       'Duration [days] (period length)',
       'QF date (quality identifier for date)',
       'x [m] (x-position of stake, EPSG:31255)',
       'y [m] (y-position of stake, EPSG:31255)', 'z [m] (elevation of stake)',
       'QF pos (quality identifier for position)', 
       'MB raw [cm] (raw mass balance measurement)',
       'Dens snow/firn/ice [kg/m**3]',
       'QF rho (quality identifier for density)', 'MB point [mm w.e./kg/m**2]',
       'QF measurement (quality identifier for stake ...)', 'measurement_type',
       'MB point unc [mm w.e.] (Uncertainty of point mass bal...)',
       'Reading unc [mm w.e.] (Reading uncertainty of point ...)',
       'Density unc [mm w.e.] (Density uncertainty of point ...)', 'Observer',
       'QF (Flag to indicate whether the ...)']]
    #dat.index=dat["Name (stake, sounding, probing)"]
    print(dat.head())

    dat.to_csv(fn, index=False)
    dat.to_excel(fnex+'.xlsx', index = False)



glaciers = ['VK', 'MWK']

an = []
winter = []

for g in glaciers:
    # make filepaths
    fn_mb_annual = g+'/'+g+'_annual_pits_stakes_fixeddate_2023.csv'
    fn_mw_winter = g+'/'+g+'_winter_pits_fixeddate_2023.csv'

    #read files
    gdf_annual = readFiles(fn_mb_annual, g)
    gdf_winter = readFiles(fn_mw_winter, g)

    # append files
    an.append(gdf_annual)
    winter.append(gdf_winter)


#concat dataframes of both glaciers:
an = pd.concat(an)
winter = pd.concat(winter)


# run all the subroutines
loadShapes('VK', an, winter)
loadShapes('MWK', an, winter)

