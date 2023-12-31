import numpy as np
import pandas as pd
import datetime as dt
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from shapely.geometry import Point
import glob
import contextily as cx

# supress copy warning - careful!
pd.options.mode.chained_assignment = None  # default='warn'

# script to read files with point MB data - files previously produced in ProcessEcxel.py
# and ProcessShapefiles.py and make plots

glaciers = ['VK', 'MWK']

# read the data tables for intermediate and annual point data:
def readFiles(fn, glac):
    colnames = ['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality', 'x_pos', 'y_pos', 'z_pos',
                'position_quality', 'mb_raw', 'density', 'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                'mb_error', 'reading_error', 'density_error', 'source']
    dat = pd.read_csv(fn, skiprows=4, sep='\t', names=colnames)
    dat['date0'] = pd.to_datetime(dat['date0'], format='%Y%m%d')
    dat['date1'] = pd.to_datetime(dat['date1'], format='%Y%m%d')
    dat['year'] = dat['date1'].dt.year
    dat['glacier'] = glac

    gdf_dat = gpd.GeoDataFrame(dat, geometry=gpd.points_from_xy(dat.x_pos, dat.y_pos), crs="EPSG:31255") # check EPSG!! should this be 31255??
    return(gdf_dat)


# read the data tables for the probing
def readProbes(fn, glac):
    colnames = ['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality', 'x_pos', 'y_pos', 'z_pos',
                'position_quality', 'mb_raw', 'density', 'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                'mb_error', 'reading_error', 'density_error', 'source', 'probe_flag']
    #dat = pd.read_csv(fn)
    dat = pd.read_csv(fn, skiprows=4, sep='\t', names=colnames)
    dat['date0'] = pd.to_datetime(dat['date0'], format='%Y%m%d')
    dat['date1'] = pd.to_datetime(dat['date1'], format='%Y%m%d')
    dat['year'] = dat['date1'].dt.year
    dat['month'] = dat['date1'].dt.month
    dat['glacier'] = glac

    gdf_dat = gpd.GeoDataFrame(dat, geometry=gpd.points_from_xy(dat.x_pos, dat.y_pos), crs="EPSG:31255") # check EPSG!!
    return(gdf_dat)


def day_of_water_year(some_date):
    # Get the date of the previous October 1st
    water_year_start_date = dt.datetime(some_date.year + some_date.month // 10 - 1, 10, 1)
        
    # Return the number of days since then
    return (some_date - water_year_start_date).days + 1



probesVK = readProbes('VK'+'/'+'VK'+'_probeData.csv', 'VK')
probesMWK = readProbes('MWK'+'/'+'MWK'+'_probeData.csv', 'MWK')

an = []
winter = []
inter = []
# inter_cu = []

for g in glaciers:
    # make filepaths
    fn_mb_annual = g+'/'+g+'_annual_pits_stakes_fixeddate.csv'
    fn_mb_inter = g+'/'+g+'_intermediate_pits_stakes.csv'
    fn_mw_winter = g+'/'+g+'_winter_pits_fixeddate.csv'
    # fn_mb_inter_cumul = g+'/'+g+'_intermediate_stakes_cumul.csv'
    
    #read files
    gdf_annual = readFiles(fn_mb_annual, g)
    gdf_winter = readFiles(fn_mw_winter, g)
    gdf_inter = readFiles(fn_mb_inter, g)

    # gdf_inter_cu = readFiles(fn_mb_inter_cumul, g)

    # append files
    an.append(gdf_annual)
    winter.append(gdf_winter)
    inter.append(gdf_inter)
    # inter_cu.append(gdf_inter_cu)


#concat dataframes of both glaciers:
an = pd.concat(an)
winter = pd.concat(winter)
inter = pd.concat(inter)
# inter_cu = pd.concat(inter_cu)


# FIG 1 - overview map of sites. 
def overview():

    fig, ax = plt.subplots(1, 1, figsize=(8, 8), sharey=True, sharex=True)
    lns = []

    # path to country borders shapefile
    countries = gpd.read_file('misc/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp') 

    # path to inventory boundaries
    glGI3 = gpd.read_file('misc/GI3/Venedigergruppe.shp')
    glGI2 = gpd.read_file('misc/GI2/AGI_newdate.shp')
    glGI1 = gpd.read_file('misc/GI2/AGI_1969.shp')
    
    glGI2.to_crs(glGI3.crs, inplace=True)
    glGI1.to_crs(glGI3.crs, inplace=True)

    # path to mwk and vk boundaries
    vk = gpd.read_file('VK/Outlines/Venedigerkees_2018.shp')
    mwk = gpd.read_file('MWK/Outlines/MWK_2018.shp')

    vk = vk.to_crs(countries.crs)
    mwk = mwk.to_crs(countries.crs)
    glGI3 = glGI3.to_crs(countries.crs)
    glGI2 = glGI2.to_crs(countries.crs)

    formarker = vk.centroid

    stations = pd.DataFrame(
            {
                "st": ["AWS_VK", "AWS_MWK"],
                "Latitude": [47.1317, 47.0839],
                "Longitude": [12.3142, 12.3634],
            }
    )
    ST_gdf = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.Longitude, stations.Latitude), crs="EPSG:4326"
    )

    vk.boundary.plot(ax=ax, alpha=1, color='red')
    mwk.boundary.plot(ax=ax, alpha=1, color='red', linestyle='-')
    lnGl = Line2D([0], [0], label='VK, MWK(2018)', color='r', linewidth=0.5, linestyle='-')
    lns.append(lnGl)

    ST_gdf.plot(ax=ax, alpha=1, color='red', marker='*', markersize=80)
    patch1 = Line2D([0], [0], marker='*', linestyle = 'None', label='AWS', color='r', markersize=8)
    lns.append(patch1)

    glGI3.plot(ax=ax, facecolor='lightblue', alpha=0.4, edgecolor='k', linewidth=0.5, linestyle='-')
    patch = mpatches.Patch(color='lightblue', label='GI 3')
    lns.append(patch)

    cx.add_basemap(ax,
               crs=countries.crs,
               source=cx.providers.BasemapAT.orthofoto,
               zoom=15
              )

    ax.annotate('VK', xy=(12.33, 47.125), color='k', fontweight='bold')
    ax.annotate('MWK', xy=(12.375, 47.085), color='k', fontweight='bold')

    ax.annotate('SK', xy=(12.32, 47.11), color='k', fontweight='bold')
    ax.annotate('G', xy=(12.344, 47.109), color='k', fontweight='bold')

    axins2 = ax.inset_axes([-0.02, 0.7, 0.4, 0.5])
    countries.plot(ax=axins2, alpha=1, edgecolor="k", facecolor='none')
    formarker.plot(ax=axins2, marker='o', color='blue', markersize=150)
    axins2.set_xticklabels([])
    axins2.set_yticklabels([])
    axins2.set_xticks([])
    axins2.set_yticks([])
    axins2.set_xlim([8.5, 18.5])
    axins2.set_ylim([46.1, 49.5])

    ax.set_xlim([12.2, 12.45])
    ax.set_ylim([47.00, 47.2])
    ax.grid('both')

    # add manual symbols to auto legend
    handles = (lns)

    fig.legend(handles=handles, loc='lower right', bbox_to_anchor=(0.9, 0.2), ncol=2)

    fig.savefig('figs/fig1.png', dpi=200, bbox_inches='tight')


# FIG 2, FIG 3 - load and plot all available glacier outlines and locations of annual point MB measurements. 
# makes one plot per glacier.
def getOutlines2(glac, an):
    fldr = glac+'/'+'Outlines'
    fls = glob.glob(fldr+'/*.shp')

    df = pd.DataFrame(columns=['fname', 'year'])
    df['fname'] = fls

    fig, ax = plt.subplots(1, 1, figsize=(8, 8), sharey=True, sharex=True)

    if glac == 'VK':
        yrs = np.arange(2012, 2023)
        df['year'] = df['fname'].str[-8:-4]
        df['year'] = df['year'].astype(int)

        clrs = cm.plasma_r(np.linspace(0.7, 0.9, len(fls)))
        ax.set_ylim([219100, 222000])
        ax.set_xlim([-77900, -74450])

    if glac == 'MWK':
        yrs = np.arange(2007, 2023)
        df['year'] = df['fname'].str[17:-4]
        df['year'].replace('LIA', '1850', inplace=True)
        df['year'] = df['year'].astype(int)
        clrs = cm.plasma_r(np.linspace(0, 0.9, len(fls)))
        ax.set_ylim([215000, 218100])
        ax.set_xlim([-75000, -71400])

    df.sort_values(by=['year'], inplace=True)

    clrs2 = cm.viridis(np.linspace(0, 0.9, len(yrs+1)))
    lns = []
    pts = []

    glGI3 = gpd.read_file('misc/GI3/Venedigergruppe.shp')

    glGI2 = gpd.read_file('misc/GI2/AGI_newdate.shp')

    glGI1 = gpd.read_file('misc/GI2/AGI_1969.shp')

    glGI2.to_crs(glGI3.crs, inplace=True)
    glGI1.to_crs(glGI3.crs, inplace=True)


    glGI1.boundary.plot(ax=ax, alpha=1, color='k', linewidth=0.5, linestyle=':')
    lnGI1 = Line2D([0], [0], label='GI 1 (1969)', color='k', linewidth=0.5, linestyle=':')
    lns.append(lnGI1)

    glGI2.boundary.plot(ax=ax, alpha=1, color='k', linewidth=0.5, linestyle='-.')
    lnGI2 = Line2D([0], [0], label='GI 2 (1998)', color='k', linewidth=0.5, linestyle='-.')
    lns.append(lnGI2)

    glGI3.boundary.plot(ax=ax, alpha=1, color='k', linewidth=0.5, linestyle='--')
    lnGI3 = Line2D([0], [0], label='GI 3 (2009)', color='k', linewidth=0.5, linestyle='--')
    lns.append(lnGI3)

    for i, f in enumerate(df['fname'].values):
        shp = gpd.read_file(f)
        shp.boundary.plot(ax=ax, alpha=1, color=clrs[i], zorder=i+1)
        # create manual symbols for legend
        ln = Line2D([0], [0], label=df['year'].values[i], color=clrs[i], linewidth=1)
        lns.append(ln)

    # plot stakes
    for j, y in enumerate(yrs):
        tm = an.loc[(pd.to_datetime(an['date1']).dt.year ==y) & (an.glacier==glac) & (an.measurement_type == 1)]
        tm.plot(ax=ax, color=clrs2[j], markersize=12, edgecolor=clrs2[j],zorder=10+1)
        pt = Line2D([0], [0], marker='o', linestyle = 'None', label=y, color=clrs2[j], markersize=6)
        lns.append(pt)

    # plot pits
    for j, y in enumerate(yrs):
        tm = an.loc[(pd.to_datetime(an['date1']).dt.year ==y) & (an.glacier==glac) & (an.measurement_type == 2)]
        if len(tm) > 0:
            tm.plot(ax=ax, color=clrs2[j], marker='s', markersize=18, edgecolor=clrs2[j],zorder=10+1)

    ax.grid('both')

    # add manual symbols to auto legend
    handles = (lns)

    if glac == 'VK':
        fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.1, 0.9), ncol=2)
    if glac == 'MWK':
        fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.1, 0.5), ncol=2)

    fig.savefig('figs/'+glac+'_outlines_and_annualdata.png', dpi=200, bbox_inches='tight')


# FIG 4
def intermediate_v_annual(gdf, an, winter, ax):

    gdf['doy'] = gdf['date1'].dt.dayofyear
    cl = ['grey', 'k']
    pts = []

    for i, g in enumerate(['VK', 'MWK']):
        stakes = gdf.loc[(gdf['measurement_type']==1) & (gdf['glacier']==g)]
        stakes['fixeddate'] = pd.to_datetime(stakes['year'].astype(str) + '0930', format='%Y%m%d')
        stakes['difFloating'] = (stakes['date1'] - stakes['fixeddate']).dt.days

        pits_spring = gdf.loc[(gdf['measurement_type']==2) & (gdf['glacier']==g) & (gdf['doy'] < 180)]
        pits_spring['fixeddate'] = pd.to_datetime(pits_spring['year'].astype(str) + '0430', format='%Y%m%d')
        pits_spring['difFloating'] = (pits_spring['date1'] - pits_spring['fixeddate']).dt.days

        pits_fall = gdf.loc[(gdf['measurement_type']==2) & (gdf['glacier']==g) & (gdf['doy'] > 180)]
        pits_fall['fixeddate'] = pd.to_datetime(pits_fall['year'].astype(str) + '0930', format='%Y%m%d')
        pits_fall['difFloating'] = (pits_fall['date1'] - pits_fall['fixeddate']).dt.days

        an_pits = an.loc[(an['measurement_type']==2) & (an['glacier']==g)]
        an_stakes = an.loc[(an['measurement_type']==1) & (an['glacier']==g)]
        winter_pits = winter.loc[(winter['measurement_type']==2) & (winter['glacier']==g)]

        for y in winter_pits.year.unique():
            win = winter_pits.loc[(winter_pits.year == y) & (winter_pits['glacier']==g)][['name', 'mb_we', 'date1']]
            spr = pits_spring.loc[(pits_spring.year == y) & (pits_spring['glacier']==g)][['name', 'mb_we', 'date1', 'difFloating']]

            difcheck = win.merge(spr, left_on='name', right_on='name', suffixes=('_fixed', '_floating'))
   
            ax.scatter(difcheck.difFloating, difcheck.mb_we_fixed - difcheck.mb_we_floating, c=cl[i], marker='s', s=14, label='spring pits, '+g)

        for y in an_pits.year.unique():
            anp = an_pits.loc[(an_pits.year == y) & (an_pits['glacier']==g)][['name', 'mb_we', 'date1']]
            fall = pits_fall.loc[(pits_fall.year == y) & (pits_fall['glacier']==g)][['name', 'mb_we', 'date1', 'difFloating']]

            difcheck = anp.merge(fall, left_on='name', right_on='name', suffixes=('_fixed', '_floating'))
     
            ax.scatter(difcheck.difFloating, difcheck.mb_we_floating - difcheck.mb_we_fixed, c=cl[i], marker='^', s=14)

        for y in an_stakes.year.unique():
            an_stk = an_stakes.loc[(an_stakes.year == y) & (an_stakes['glacier']==g)][['name', 'mb_we', 'date1', 'geometry']]
            stk = stakes.loc[(stakes.year == y) & (stakes['glacier']==g)][['name', 'mb_we', 'date1', 'difFloating','geometry']]

            stk_cu_subset = pd.DataFrame(columns=['name', 'mb_we', 'date1', 'difFloating','geometry'])

            for p in stk.geometry.unique():
                stk_cu = stk.loc[(stk.geometry==p)]
                stk_cu.sort_values(by=['date1'], inplace=True)
                stk_cu['mb_we_cu'] = stk_cu['mb_we'].cumsum()
                stk_cu_season = stk_cu.loc[stk_cu.date1 == stk_cu.date1.max()]
                stk_cu_subset = pd.concat([stk_cu_subset, stk_cu_season])

            difcheck = an_stk.merge(stk_cu_subset, left_on='geometry', right_on='geometry', suffixes=('_fixed', '_floating'))
            difcheck['mbfloat_mbfixed'] = difcheck.mb_we_cu - difcheck.mb_we_fixed
     
            ax.scatter(difcheck.difFloating, difcheck['mbfloat_mbfixed'], c=cl[i], s=14, marker='o',label='stakes, '+g)

        pt1 = Line2D([0], [0], c=cl[i], marker='^', label='fall pits, '+g, linestyle='None')
        pt2 = Line2D([0], [0], c=cl[i], marker='s', label='spring pits, '+g, linestyle='None')
        pt3 = Line2D([0], [0], c=cl[i], marker='o', label='stakes, '+g, linestyle='None')
        pts.append(pt1)
        pts.append(pt2)
        pts.append(pt3)

    ax.set_ylabel('b floating - b fixed [mm w.e.]')
    ax.set_xlabel('floating date - fixed date [days]')
    ax.set_title('Difference floating date to fixed date')
    ax.grid('both')


# FIG 4
def intermediate_v_annual_unc(gdf, an, winter, ax):

    gdf['doy'] = gdf['date1'].dt.dayofyear
    cl = ['grey', 'k']
    pts = []

    stakes = gdf.loc[(gdf['measurement_type']==1)]
    stakes['fixeddate'] = pd.to_datetime(stakes['year'].astype(str) + '0930', format='%Y%m%d')
    stakes['difFloating'] = (stakes['date1'] - stakes['fixeddate']).dt.days

    pits_spring = gdf.loc[(gdf['measurement_type']==2) & (gdf['doy'] < 180)]
    pits_spring['fixeddate'] = pd.to_datetime(pits_spring['year'].astype(str) + '0430', format='%Y%m%d')
    pits_spring['difFloating'] = (pits_spring['date1'] - pits_spring['fixeddate']).dt.days

    pits_fall = gdf.loc[(gdf['measurement_type']==2) & (gdf['doy'] > 180)]
    pits_fall['fixeddate'] = pd.to_datetime(pits_fall['year'].astype(str) + '0930', format='%Y%m%d')
    pits_fall['difFloating'] = (pits_fall['date1'] - pits_fall['fixeddate']).dt.days

    an_pits = an.loc[(an['measurement_type']==2)]
    an_stakes = an.loc[(an['measurement_type']==1)]
    winter_pits = winter.loc[(winter['measurement_type']==2)]

    labels = ['s_int', 's_annual', 'p_int., spring', 'p_seas.', 'p_int, fall', 'p_annual']

    data = [stakes['mb_error'], an_stakes['mb_error'][~np.isnan(an_stakes['mb_error'])], pits_spring['mb_error'], winter_pits['mb_error'],
            pits_fall['mb_error'], an_pits['mb_error']]

    ax.boxplot(data, labels=labels)

    checkunc = an_stakes[['mb_error', 'reading_error', 'density_error', 'mb_we', 'date1', 'name', 'glacier']]
    ax.grid('both')


# FIG 4: three subplots showing intermediated data (the above subroutines are called in this one)
def intermediate_stats_combined(gdf, an, winter):
    gdf['doy'] = gdf['date1'].dt.dayofyear
   
    fig, ax = plt.subplot_mosaic([['a)', 'a)'], ['b)', 'c)']],layout='constrained', figsize=(12, 8))
    cl = ['grey', 'k']

    for i, g in enumerate(['VK', 'MWK']):
        stakes = gdf.loc[(gdf['measurement_type']==1) & (gdf['glacier']==g)]
        stakes['fixeddate'] = pd.to_datetime(stakes['year'].astype(str) + '0930', format='%Y%m%d')
        stakes['difFloating'] = (stakes['date1'] - stakes['fixeddate']).dt.days

        pits_spring = gdf.loc[(gdf['measurement_type']==2) & (gdf['glacier']==g) & (gdf['doy'] < 180)]
        pits_spring['fixeddate'] = pd.to_datetime(pits_spring['year'].astype(str) + '0430', format='%Y%m%d')
        pits_spring['difFloating'] = (pits_spring['date1'] - pits_spring['fixeddate']).dt.days

        pits_fall = gdf.loc[(gdf['measurement_type']==2) & (gdf['glacier']==g) & (gdf['doy'] > 180)]
        pits_fall['fixeddate'] = pd.to_datetime(pits_fall['year'].astype(str) + '0930', format='%Y%m%d')
        pits_fall['difFloating'] = (pits_fall['date1'] - pits_fall['fixeddate']).dt.days

        an_pits = an.loc[(an['measurement_type']==2) & (an['glacier']==g)]
        an_stakes = an.loc[(an['measurement_type']==1) & (an['glacier']==g)]
        winter_pits = winter.loc[(winter['measurement_type']==2) & (winter['glacier']==g)]

        df = pd.DataFrame(index=['spring', 'fall', 'stakes'], columns=['min', 'max', 'mean', 'median', 'count'])

        df.loc['spring', 'min'] = pits_spring['difFloating'].abs().min()
        df.loc['spring', 'max'] = pits_spring['difFloating'].abs().max()
        df.loc['spring', 'mean'] = pits_spring['difFloating'].abs().mean()
        df.loc['spring', 'median'] = pits_spring['difFloating'].abs().median()
        df.loc['spring', 'count'] = pits_spring['difFloating'].count()

        df.loc['fall', 'min'] = pits_fall['difFloating'].abs().min()
        df.loc['fall', 'max'] = pits_fall['difFloating'].abs().max()
        df.loc['fall', 'mean'] = pits_fall['difFloating'].abs().mean()
        df.loc['fall', 'median'] = pits_fall['difFloating'].abs().median()
        df.loc['fall', 'count'] = pits_fall['difFloating'].count()

        df.loc['stakes', 'count'] = stakes['difFloating'].count()

        ax['a)'].scatter(pits_spring['doy'], pits_spring['mb_we'], color = cl[i], label=g + ', pits', marker='s')
        ax['a)'].scatter(pits_fall['doy'], pits_fall['mb_we'], color = cl[i] , marker='s')

        ax['a)'].scatter(stakes['doy'], stakes['mb_we'], color = cl[i], label=g + ', stakes', marker='o', s=8)

        # uncomment to print some stats
        # print(g, df)
        # print(g, 'stake readings', stakes.shape[0])

    ax['a)'].vlines([120, 273], -3500, 3200, color ='k', linewidth=1)
    ax['a)'].set_ylim([-3500, 3200])
    ax['a)'].set_ylabel('b (mm w.e.)')
    ax['a)'].legend(loc='lower left')
    ax['a)'].grid('both')
    ax['a)'].set_xlabel('day of year')
    ax['a)'].set_title('Intermediate measurements')

    # call separate functions to generate the subplots:
    intermediate_v_annual(gdf, an, winter, ax['b)'])
    intermediate_v_annual_unc(gdf, an, winter, ax['c)'])

    ax['b)'].set_ylabel('b floating - b fixed (mm w.e.)')
    ax['c)'].set_ylabel('b (mm w.e.)')
    ax['c)'].set_title('Mass balance error')

    ax['a)'].annotate('a)', xy=(0.025, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax['b)'].annotate('b)', xy=(0.1, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax['c)'].annotate('c)', xy=(0.1, 0.9), xycoords='axes fraction', color='k', fontweight='bold')

    
    fig.savefig('figs/combinedPlot_intermediate.png', bbox_inches='tight', dpi=150)

   
# FIG 5: Sumulative seasonal ablation at three example stakes
def plot_intermediate(gdf):
    yrs = np.arange(2007, 2023)

    gdf['doy'] = gdf['date1'].dt.dayofyear
    gdf['wday'] = gdf.date1.apply(day_of_water_year)

    # print(gdf['z_pos'].min())
    # print(gdf['z_pos'].max())

    clr = cm.plasma(np.linspace(0, 1, len(yrs)))
    fig, ax = plt.subplots(3, 1, figsize=(10, 7), sharey=True, sharex=True)
    ax = ax.flatten()

    pts = []
    for i, y in enumerate(yrs):
        tmp = gdf.loc[(gdf['year']==y)]
        stkMWK = tmp.loc[(tmp['name'] == '11') & (tmp.glacier=='MWK')]

        stkMWK['mb_we_cu'] = stkMWK['mb_we'].cumsum()
        # print(stkMWK.z_pos.max())
        # print(stkMWK.z_pos.min())

        if y < 2021:
            lowVK = tmp.loc[(tmp['name'] == '95') & (tmp.glacier=='VK')]
            highVK = tmp.loc[(tmp['name'] == '100') & (tmp.glacier=='VK')]

            lowVK['mb_we_cu'] = lowVK['mb_we'].cumsum()
            highVK['mb_we_cu'] = highVK['mb_we'].cumsum()

            # print(highVK.z_pos.max())
            # print(highVK.z_pos.min())

            # print(lowVK.z_pos.max())
            # print(lowVK.z_pos.min())
        if y > 2021:
            lowVK = tmp.loc[(tmp['name'] == 'VEK-6') & (tmp.glacier=='VK')]
            highVK = tmp.loc[(tmp['name'] == 'VEK-18') & (tmp.glacier=='VK')]

            lowVK['mb_we_cu'] = lowVK['mb_we'].cumsum()
            highVK['mb_we_cu'] = highVK['mb_we'].cumsum()

            # print(highVK.z_pos.max())
            # print(highVK.z_pos.min())

            # print(lowVK.z_pos.max())
            # print(lowVK.z_pos.min())

        ax[0].plot(lowVK['doy'], lowVK['mb_we_cu'], color=clr[i], linewidth=0.5)
        ax[0].scatter(lowVK['doy'], lowVK['mb_we_cu'], color=clr[i], edgecolor='k', linewidth=0.5)

        ax[1].plot(highVK['doy'], highVK['mb_we_cu'], color=clr[i], linewidth=0.5)
        ax[1].scatter(highVK['doy'], highVK['mb_we_cu'], color=clr[i],  edgecolor='k', linewidth=0.5)

        ax[2].plot(stkMWK['doy'], stkMWK['mb_we_cu'], color=clr[i], linewidth=0.5)
        ax[2].scatter(stkMWK['doy'], stkMWK['mb_we_cu'], color=clr[i],  edgecolor='k', linewidth=0.5)

        pt = Line2D([0], [0], marker='o', linestyle='None', label=str(y), color=clr[i], markersize=8)
        pts.append(pt)
    
    ax[0].set_title('VK - Stake 95 / VEK-6')
    ax[1].set_title('VK - Stake 100 / VEK-18')
    ax[2].set_title('MWK - Stake 11')

    for a in ax:
        a.grid('both')
        a.set_ylabel('b (cumulative, mm w.e.)')
        a.set_xlim([160, 295])
        a.set_ylim([-5500, 40])
        a.vlines([273], -5500, 100, color ='k', linewidth=1)
    ax[2].set_xlabel('day of year')

    ax[0].annotate('a)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[1].annotate('b)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[2].annotate('c)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')

    fig.legend(handles=pts, loc='lower left', bbox_to_anchor=(0.9, 0.3))
    fig.savefig('figs/StakesIntermediate_seasonal.png', bbox_inches='tight', dpi=150)


# FIG 6: MB vs elevation, winter & annual
def plot_annual_seasonal_elevation(winter, an, probesVK, probesMWK):

    fig, ax = plt.subplots(2, 2, figsize=(10, 12), sharey=True)
    ax = ax.flatten()
    yrs = np.arange(2007, 2023)
    clrs = cm.plasma(np.linspace(0, 0.9, len(yrs)))
    lns = []

    for i, y in enumerate(yrs):
        tm = winter.loc[(winter.measurement_type == 2) & (pd.to_datetime(winter['date1']).dt.year ==y) & (winter['glacier'] == 'MWK')]
        ln = ax[0].scatter(tm['mb_we'], tm['z_pos'], s=28, color=clrs[i], label=str(y), edgecolor='k', linewidth=0.2, zorder=4)
        ax[0].errorbar(tm.mb_we, tm.z_pos, xerr=tm.mb_error, linestyle="None", color='k', linewidth=0.4, zorder=1)

        tm2 = winter.loc[(winter.measurement_type == 2) & (pd.to_datetime(winter['date1']).dt.year ==y) & (winter['glacier'] == 'VK')]
        ax[1].scatter(tm2['mb_we'], tm2['z_pos'], s=28, color=clrs[i], marker='o', zorder=2, edgecolor='k', linewidth=0.2)
        ax[1].errorbar(tm2.mb_we, tm2.z_pos, xerr=tm2.mb_error, linestyle="None", color='k', linewidth=0.4, zorder=1)

        tm_prbVK = probesVK.loc[(probesVK['year']==y) & (probesVK['month'] == 4) & (probesVK['glacier'] == 'VK') & (probesVK['probe_flag'] == 0)]
        tm_prb_badVK = probesVK.loc[(probesVK['year']==y) & (probesVK['month'] == 4) & (probesVK['glacier'] == 'VK') & (probesVK['probe_flag'] == 1)]
        ax[1].scatter(tm_prbVK['mb_we'], tm_prbVK['z_pos'], s=4, color=clrs[i], marker='o', zorder=1)

        tm_prbMWK = probesMWK.loc[(probesMWK['year']==y) &  (probesMWK['month'] == 4) & (probesMWK['glacier'] == 'MWK') & (probesMWK['probe_flag'] == 0)]
        tm_prb_badMWK = probesMWK.loc[(probesMWK['year']==y) &  (probesMWK['month'] == 4) & (probesMWK['glacier'] == 'MWK') & (probesMWK['probe_flag'] == 1)]
        ax[0].scatter(tm_prbMWK['mb_we'], tm_prbMWK['z_pos'], s=4, color=clrs[i], marker='o', zorder=1)
        lns.append(ln)

    ax[0].set_xlabel('b_w (mm w.e.)')
    ax[0].set_ylabel('elevation (m.a.s.l.)')
    ax[0].grid('both')
    ax[0].set_title('Winter point mass balance, MWK')

    ax[1].set_xlabel('b_w (mm w.e.)')
    ax[1].set_ylabel('elevation (m.a.s.l.)')
    ax[1].grid('both')
    ax[1].set_title('Winter point mass balance, VK')

    for j, y in enumerate(yrs):
        temp = an.loc[(an['year'] == y) & (an['glacier'] == 'MWK')]
        ax[2].scatter(temp.mb_we, temp.z_pos, color=clrs[j], s=28, edgecolor='k', linewidth=0.2, zorder=2)
        ax[2].errorbar(temp.mb_we, temp.z_pos, xerr=temp.mb_error, linestyle="None", color='k', linewidth=0.4, zorder=1)
        
        tm_prb2MWK = probesMWK.loc[(probesMWK['year']==y) &  (probesMWK['month'] == 9) & (probesMWK['glacier'] == 'MWK')& (probesMWK['probe_flag'] == 0)]
        ax[2].scatter(tm_prb2MWK['mb_we'], tm_prb2MWK['z_pos'], s=4, color=clrs[j], marker='o', zorder=4)

    for j, y in enumerate(yrs):
        temp2 = an.loc[(an['year'] == y) & (an['glacier'] == 'VK')]
        ax[3].scatter(temp2.mb_we, temp2.z_pos, color=clrs[j], s=28, marker='o', zorder=2, edgecolor='k', linewidth=0.2)
        ax[3].errorbar(temp2.mb_we, temp2.z_pos, xerr=temp2.mb_error, linestyle="None", color='k', linewidth=0.4, zorder=1)

        tm_prb2VK = probesVK.loc[(probesVK['year']==y) &  (probesVK['month'] == 9) & (probesVK['glacier'] == 'VK')& (probesVK['probe_flag'] == 0)]
        ax[3].scatter(tm_prb2VK['mb_we'], tm_prb2VK['z_pos'], s=4, color=clrs[j], marker='o', zorder=4)

    VKmax = an.loc[an['glacier'] == 'VK']['mb_we'].min()

    MWKmax = an.loc[an['glacier'] == 'MWK']['mb_we'].min()

    ax[2].set_xlabel('b (mm w.e.)')
    ax[2].set_ylabel('elevation (m.a.s.l.)')
    ax[2].grid('both')
    ax[2].set_title('Annual point mass balance, MWK')

    ax[3].set_xlabel('b (mm w.e.)')
    ax[3].set_ylabel('elevation (m.a.s.l.)')
    ax[3].grid('both')
    ax[3].set_title('Annual point mass balance, VK')

    pt1 = Line2D([0], [0], marker='o', linestyle = 'None', label='stakes and pits', color='k', markersize=8)
    pt1_2 = Line2D([0], [0], marker='o', linestyle = 'None', label='probe points', color='k', markersize=4)
    lns.append(pt1)    
    lns.append(pt1_2)
    
    ax[0].annotate('a)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[1].annotate('b)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[2].annotate('c)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[3].annotate('d)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')

    fig.legend(handles=lns, loc='lower left', bbox_to_anchor=(0.9, 0.2))
    fig.savefig('figs/annual_seasonal_elevation.png', bbox_inches='tight', dpi=200)

# # -----------------------------------------------------------
# # FIGURES
# FIG 1 - overview map (this takes a while because it loads a basemap tile for the background image)
# overview()

# FIG 2, FIG 3 - all available outlines and location of annual point balance measurements, colored by years
getOutlines2('MWK', an)
getOutlines2('VK', an)

# FIG 4 - three subplots showing intermediate data and uncertainties)
# uncomment print statements to print number of stake readings and spring and fall pits, as well as stats for difference fixed to floating date
intermediate_stats_combined(inter, an, winter)

# FIG 5 - plot subseasonal intermediate cumulative stake data for 3 stakes (3 subplots)
plot_intermediate(inter)

# FIG 6 - annual and winter point mb vs elevation:
plot_annual_seasonal_elevation(winter, an, probesVK, probesMWK)


plt.show()

