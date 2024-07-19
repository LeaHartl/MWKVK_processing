# ! /usr/bin/env python3
import numpy as np
import pandas as pd
import geopandas as gpd
import json
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as seaborn
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
# from geopandas import GeoDataFrame
from shapely.geometry import Point
import glob

# this reads files with MB data as downloaded from pangaea at the following links.
# MWK: https://doi.pangaea.de/10.1594/PANGAEA.806662 
# VK: https://doi.pangaea.de/10.1594/PANGAEA.833232
# to run, download all data using the option "Download ZIP file containing all datasets as tab-delimited text" 
# unpack the zip files and adjust file paths in "readFiles_elevation" and "readFiles_massbalance"
# to point to the directoriy to which you downloaded data.


# Issues found in pangaea data and fixes:
# MKW and VK: in some years the column headers for winter and summer MB were the wrong way around, changed in the files.
# VK: some errors in the summary data for 14/15, 15/16 and 16/17, change in the files according to MB reports provided by BS.
# corrections have been submitted to pangaea

glaciers = ['MWK', 'VK']

# load the files for elevation zone data:
def readFiles_elevation(gl, y2):
    y1 = y2-1
    fldr = gl+'/'+gl+'_mass_balances_elevation_zones/datasets/'
    fn = gl+'_elevation_zones_'+str(y1)+'_'+str(y2)+'.tab'
    fl = fldr + fn
    with open(fl, "r", encoding="utf-8") as f:
        while line := f.readline():
            if line.strip() == "*/":
                break
    
        df = pd.read_csv(f, delimiter='\t')
        df.index += 1
    return(df)


def readFiles_massbalance(gl, y2):
    y1 = y2-1
    fldr = gl+'/'+gl+'_mass_balances_elevation_zones/datasets/'
    fn = gl+'_mass_balance_'+str(y1)+'_'+str(y2)+'.tab'
    fl = fldr + fn
    with open(fl, "r", encoding="utf-8") as f:
        while line := f.readline():
            if line.strip() == "*/":
                break

        df = pd.read_csv(f, delimiter='\t')
        df.index += 1
        if 'ELA [m a.s.l.]' not in df.columns:
            df['ELA [m a.s.l.]'] = np.nan
    return(df)


# FIG 11 - time series of glacier wide mass balance (three panels)
def MB_bars3panels():
    yrsMWK = np.arange(2007, 2023, 1)
    yrsVK = np.arange(2012, 2023, 1)

    mwk = []
    for i, yr in enumerate(yrsMWK):
        tmp = readFiles_massbalance('MWK', yr)
        # if 'ELA [m a.s.l.]' not in tmp.columns:
            # tmp['ELA [m a.s.l.]'] = np.nan
        tmp.rename(columns={tmp.columns[0]: "Date/time start" }, inplace = True)
        tmp.rename(columns={tmp.columns[1]: "Date/time end" }, inplace = True)
        mwk.append(tmp)
    MWK = pd.concat(mwk)
    MWK.index = yrsMWK

    vk = []
    for i, yr in enumerate(yrsVK):
        tmp = readFiles_massbalance('VK', yr)
        # if 'ELA [m a.s.l.]' not in tmp.columns:
            # tmp['ELA [m a.s.l.]'] = np.nan
        tmp.rename(columns={tmp.columns[0]: "Date/time start" }, inplace = True)
        tmp.rename(columns={tmp.columns[1]: "Date/time end" }, inplace = True)
        vk.append(tmp)
    VK = pd.concat(vk)
    VK.index = yrsVK

    VK = VK.reindex(yrsMWK).fillna(method='ffill')

    fig, ax = plt.subplots(3, 1, figsize=(12, 10))#, sharex=True)
    ax = ax.flatten()

    dataMWK = {'Winter': MWK['bw [kg/m**2]'].astype(float),
            'Summer': MWK['bs [kg/m**2]'].astype(float),
            'Annual': MWK['b [kg/m**2]'].astype(float),
            }

    dataVK = {
            'Winter': VK['bw [kg/m**2]'].astype(float),
            'Summer': VK['bs [kg/m**2]'].astype(float),
            'Annual': VK['b [kg/m**2]'].astype(float),
            }

    dfMWK = pd.DataFrame(dataMWK, index=yrsMWK)
    dfVK = pd.DataFrame(dataVK, index=yrsVK)
    dfVK = dfVK.reindex(yrsMWK)
    dfMWK.plot.bar(rot=0, ax=ax[0], width=0.9, color={"Annual": "silver", "Summer": "red", "Winter" :"blue"}, legend=False)
    dfVK.plot.bar(rot=0, ax=ax[1], width=0.9, color={"Annual": "silver", "Summer": "red", "Winter" :"blue"}).legend(loc='lower left')

    ax[0].grid('both')
    ax[0].set_ylabel('b (mm w.e.)')
    x_label = ax[0].axes.get_xaxis().get_label()
    x_label.set_visible(False)
    ax[0].set_title('MWK')

    ax[1].grid('both')
    ax[1].set_ylabel('b (mm w.e.)')
    x_label = ax[1].axes.get_xaxis().get_label()
    x_label.set_visible(False)
    ax[1].set_title('VK')

    ax[2].plot(dfMWK.index, dfMWK.Annual.cumsum(), color='k', label='MWK')
    ax[2].plot(dfVK.index, dfVK.Annual.cumsum(), color='k', linestyle='--', label='VK')

    ax[2].legend()
    ax[2].grid('both')
    ax[2].set_xlabel('year')
    ax[2].set_ylabel('cumulative b (mm w.e.)')
    ax[2].set_xticks(dfMWK.index.values)

    ax[0].annotate('a)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[1].annotate('b)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
    ax[2].annotate('c)', xy=(0.02, 0.9), xycoords='axes fraction', color='k', fontweight='bold')

    fig.savefig('figs/timeseries3panels.png', bbox_inches='tight', dpi=300)

# FIG 12 - subplots  of winter, summer, annual balance for each year, as horizontal bar plots
def ElevZones():
    yrsMWK = np.arange(2007, 2023, 1)
    yrsVK = np.arange(2012, 2023, 1)
    rows=4
    cols=4
    fig, ax = plt.subplots(rows, cols, sharex=True, sharey=True, figsize=(12, 8))
    ax = ax.flatten()
    for a in ax:
        a.set_xlim(-6100, 2500)
        a.set_ylim(2400, 3500)
    ax[0].set_ylabel('elevation (m)')
    ax[4].set_ylabel('elevation (m)')
    ax[8].set_ylabel('elevation (m)')
    ax[12].set_ylabel('elevation (m)')
    ax[12].set_xlabel('b (mm w.e.)')
    ax[13].set_xlabel('b (mm w.e.)')
    ax[14].set_xlabel('b (mm w.e.)')
    ax[15].set_xlabel('b (mm w.e.)')
    highMWK = []
    highVK = []
    for i, yr in enumerate(yrsMWK):
        tmp = readFiles_elevation('MWK', yr)
        tmp['elev'] = (tmp['Elev max [m a.s.l.]'] + tmp['Elev min [m a.s.l.]']) / 2
        highM = tmp.loc[tmp.elev >= 3200]['baZ [kg/m**2]'].sum()
        highMWK.append(highM)
        ax[i].barh(tmp.elev, tmp['bwaZ [kg/m**2]'], align='center', height=50, color='blue', alpha=0.8)
        ax[i].barh(tmp.elev, tmp['bsaZ [kg/m**2]'], align='center', height=50, color='red', alpha=0.8)
        ax[i].barh(tmp.elev, tmp['baZ [kg/m**2]'], align='center', height=50, color='silver', alpha=0.8)
        ax[i].vlines(0, 2400, 3500, colors='k')
        
        ax[i].set_title(str(yr))
        ax[i].grid(axis='both', which='both', zorder=1)

        tmp2 = readFiles_massbalance('MWK', yr)
        ax[i].hlines(tmp2['ELA [m a.s.l.]'].astype(float), -6100, 2500, linestyle='-', color='k', linewidth=0.8)

        if yr in yrsVK:
            tmpVK = readFiles_elevation('VK', yr)
            tmpVK['elev'] = (tmpVK['Elev max [m a.s.l.]'] + tmpVK['Elev min [m a.s.l.]']) / 2
            highV = tmpVK.loc[tmpVK.elev >= 3200]['baZ [kg/m**2]'].sum()
            highVK.append(highV)
            ax[i].step(tmpVK['baZ [kg/m**2]'], tmpVK.elev, color='slategrey', where='mid', linestyle='-')
            ax[i].step(tmpVK['bsaZ [kg/m**2]'], tmpVK.elev, color='darkred', where='mid', linestyle='-')
            ax[i].step(tmpVK['bwaZ [kg/m**2]'], tmpVK.elev, color='darkblue', where='mid', linestyle='-')

            tmp2VK = readFiles_massbalance('VK', yr)
            ax[i].hlines(tmp2VK['ELA [m a.s.l.]'].astype(float), -6100, 2500, linestyle='--', color='k', linewidth=0.8)

    # create manual symbols for legend
    patch = mpatches.Patch(color='silver', label='MWK annual')
    patch_w = mpatches.Patch(color='blue', label='MWK winter')
    patch_s = mpatches.Patch(color='red', label='MWK summer')     
    lineMWK = Line2D([0], [0], label='MWK ELA', color='k', linewidth=0.8)
    line_a = Line2D([0], [0], label='VK annual', color='slategrey', linewidth=1)
    line_w = Line2D([0], [0], label='VK winter', color='darkblue', linewidth=1)
    line_s = Line2D([0], [0], label='VK summer', color='darkred', linewidth=1)
    lineVK = Line2D([0], [0], label='VK ELA', color='k', linestyle='--', linewidth=0.8)

    # add manual symbols to auto legend
    handles = ([patch, patch_w, patch_s, lineMWK, line_a, line_w, line_s, lineVK])

    fig.legend(handles=handles, loc='center right', bbox_to_anchor=(1.05, 0.5))
    fig.savefig('figs/elevationzones.png', bbox_inches='tight', dpi=300)



# FIG 12, 13 - subplots  of winter, summer, annual balance for each year, as horizontal bar plots
def ElevZones_v2(gl):
    # yrsMWK = np.arange(2007, 2023, 1)
    # yrsVK = np.arange(2012, 2023, 1)
    if gl == 'MWK':
        rows = 4
        cols = 4
        yrs = np.arange(2007, 2023, 1)
        xl = [-6100, 2500]
        yl = [2600, 3500]
    if gl == 'VK':
        rows = 3
        cols = 4
        yrs = np.arange(2012, 2023, 1)
        xl = [-6100, 2500]
        yl = [2300, 3500]
    fig, ax = plt.subplots(rows, cols, sharex=True, sharey=True, figsize=(12, 8))
    ax = ax.flatten()
    for a in ax:
        a.set_xlim(xl)
        a.set_ylim(yl)
        a.set_xticks([-6000, -4000, -2000, 0, 2000])
        a.set_xticklabels(['', '-4000', '-2000', '0', '2000'])

    if gl == 'MWK':
        ax[0].set_ylabel('elevation (m)')
        ax[4].set_ylabel('elevation (m)')
        ax[8].set_ylabel('elevation (m)')
        ax[12].set_ylabel('elevation (m)')
        ax[12].set_xlabel('b (mm w.e.)')
        ax[13].set_xlabel('b (mm w.e.)')
        ax[14].set_xlabel('b (mm w.e.)')
        ax[15].set_xlabel('b (mm w.e.)')

    if gl == 'VK':
        ax[0].set_ylabel('elevation (m)')
        ax[4].set_ylabel('elevation (m)')
        ax[8].set_ylabel('elevation (m)')
        ax[8].set_xlabel('b (mm w.e.)')
        ax[9].set_xlabel('b (mm w.e.)')
        ax[10].set_xlabel('b (mm w.e.)')
        ax[-1].set_axis_off()

    highMWK = []
    highVK = []
    for i, yr in enumerate(yrs):
        tmp = readFiles_elevation(gl, yr)
        tmp['elev'] = (tmp['Elev max [m a.s.l.]'] + tmp['Elev min [m a.s.l.]']) / 2
        highM = tmp.loc[tmp.elev >= 3200]['baZ [kg/m**2]'].sum()
        # highMWK.append(highM)
        ax[i].barh(tmp.elev, tmp['bwaZ [kg/m**2]'], align='center', height=50, color='blue', alpha=0.8)
        ax[i].barh(tmp.elev, tmp['bsaZ [kg/m**2]'], align='center', height=50, color='red', alpha=0.8)
        ax[i].barh(tmp.elev, tmp['baZ [kg/m**2]'], align='center', height=50, color='silver', alpha=0.8)
        ax[i].vlines(0, 2400, 3500, colors='k')
        
        # ax[i].set_title(str(yr))
        ax[i].annotate(str(yr), xy=(0.1, 0.9), xycoords='axes fraction', color='k', fontweight='bold')
        ax[i].grid(axis='both', which='both', zorder=1)

        tmp2 = readFiles_massbalance(gl, yr)
        ax[i].hlines(tmp2['ELA [m a.s.l.]'].astype(float), -6100, 2500, linestyle='-', color='k', linewidth=0.8)

        # if yr in yrsVK:
        #     tmpVK = readFiles_elevation('VK', yr)
        #     tmpVK['elev'] = (tmpVK['Elev max [m a.s.l.]'] + tmpVK['Elev min [m a.s.l.]']) / 2
        #     highV = tmpVK.loc[tmpVK.elev >= 3200]['baZ [kg/m**2]'].sum()
        #     highVK.append(highV)
        #     ax[i].step(tmpVK['baZ [kg/m**2]'], tmpVK.elev, color='slategrey', where='mid', linestyle='-')
        #     ax[i].step(tmpVK['bsaZ [kg/m**2]'], tmpVK.elev, color='darkred', where='mid', linestyle='-')
        #     ax[i].step(tmpVK['bwaZ [kg/m**2]'], tmpVK.elev, color='darkblue', where='mid', linestyle='-')

        #     tmp2VK = readFiles_massbalance('VK', yr)
        #     ax[i].hlines(tmp2VK['ELA [m a.s.l.]'].astype(float), -6100, 2500, linestyle='--', color='k', linewidth=0.8)

    # create manual symbols for legend
    patch = mpatches.Patch(color='silver', label='annual')
    patch_w = mpatches.Patch(color='blue', label='winter')
    patch_s = mpatches.Patch(color='red', label='summer')     
    line = Line2D([0], [0], label='ELA', color='k', linewidth=0.8)

    # add manual symbols to auto legend
    handles = ([patch, patch_w, patch_s, line])

    fig.legend(handles=handles, loc='center right', bbox_to_anchor=(1.05, 0.5))
    plt.subplots_adjust(wspace=0.04, hspace=0.04)
    fig.savefig('figs/elevationzones_'+gl+'.png', bbox_inches='tight', dpi=300)




# ElevZones()
ElevZones_v2('VK')
ElevZones_v2('MWK')

# MB_bars3panels()


plt.show()


