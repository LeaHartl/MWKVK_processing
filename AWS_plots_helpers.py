import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

from matplotlib import cm
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

from windrose import WindroseAxes, plot_windrose
import scipy.stats as stats
from scipy.stats import circmean


# functions to plot AWS data

def timeseriesplot(ds, st):
    # cut off incomplete days:
    # careful: this does not work if it's the first/last day of the month
    starthour = '00:00:00'
    startday = str(ds.index[0].day +1)
    startmonth = str(ds.index[0].month)
    startyear = str(ds.index[0].year)
    start = pd.to_datetime(startyear+'-'+startmonth+'-'+startday+'-'+starthour)
    
    endhour = '23:50:00'
    endday = str(ds.index[-1].day -1)
    endmonth = str(ds.index[-1].month)
    endyear = str(ds.index[-1].year)
    end = pd.to_datetime(endyear+'-'+endmonth+'-'+endday+'-'+endhour)

    # print('start:', start)
    # print('end:', end)

    smonth = pd.to_datetime('2019-10-01 00:00')

    df = ds.loc[start:end]

    df_mean = df.resample('d').mean()
    df_min = df.resample('d').min()
    df_max = df.resample('d').max()

    df_mnth = df.loc[smonth:].resample('m').mean()

    df_mnth_low = df_min.loc[smonth:].resample('m').mean()
    df_mnth_high = df_max.loc[smonth:].resample('m').mean()

    df_mnth['month'] = df_mnth.index.month
    df_mnth['year'] = df_mnth.index.year
    df_mnth_p = df_mnth.pivot(index='month', columns='year', values='Tair_Avg')
    df_mnth_p_SW = df_mnth.pivot(index='month', columns='year', values='SWin_Avg')
    # uncomment to print some stats and a latex table
    # print(df_mnth_p.round(1))
    # print(df_mnth_p.round(1).to_latex())
    # save stats to CSV
    df_mnth_p.round(1).to_csv('out/'+st+'_monthlyT.csv')
    df_mnth_p_SW.round(1).to_csv('out/'+st+'_monthlySW.csv')


    fig, ax = plt.subplots(6, 1, figsize=(12, 10), sharex=True)
    ax = ax.flatten()

    ax[0].plot(df_mnth.index, df_mnth.Tair_Avg, c='k', label='monthly mean')
    #ax[0].plot(df_mnth_low.index, df_mnth_low.Tair_Avg, c='b', label='daily low, monthly mean')
    #ax[0].plot(df_mnth_high.index, df_mnth_high.Tair_Avg, c='r', label='daily high, monthly mean')
    ax[0].plot(df_mean.index, df_mean.Tair_Avg, c='k', linestyle='--', linewidth=0.5, label='daily mean')
    ax[0].fill_between(df_mean.index, df_min.Tair_Avg, df_max.Tair_Avg, alpha=0.5, label='daily range')
    ax[0].set_title('Air Temperature')

    ax[0].grid('both')
    ax[0].legend(loc='center', ncol=3, bbox_to_anchor=[0.5, 0.9])
    ax[0].set_ylabel('°C')
    ax[0].set_ylim([-25, 25])

    ax[1].plot(df_mnth.index, df_mnth.Hum_Avg, c='k', label='monthly mean')
    ax[1].plot(df_mean.index, df_mean.Hum_Avg, c='k', linestyle='--', linewidth=0.5, label='daily mean')
    ax[1].grid('both')
    ax[1].set_ylabel('%')
    ax[1].set_title('Relative Humidity')
    ax[1].legend(loc='center', ncol=2, bbox_to_anchor=[0.5, 0.9])
    ax[1].set_ylim([0, 130])

    ax[2].plot(df_mnth.index, df_mnth.Press_Avg, c='k', label='monthly mean')
    ax[2].plot(df_mean.index, df_mean.Press_Avg, c='k', linestyle='--', linewidth=0.5, label='daily mean')
    ax[2].set_ylabel('mbar')
    ax[2].set_title('Surface Pressure')
    # ax[2].yaxis.label.set_color('r')
    ax[2].legend(loc='center', ncol=2, bbox_to_anchor=[0.5, 0.9])
    ax[2].set_ylim([670, 740])
    ax[2].grid('both')

    ax[3].plot(df_mnth.index, df_mnth.SWin_Avg, c='k', label='monthly mean SW in')
    ax[3].plot(df_mean.index, df_mean.SWin_Avg, c='k', linestyle='--', linewidth=0.5, label='daily mean SW in')
    ax[3].plot(df_mnth.index, df_mnth.SWout_Avg, c='grey', label='monthly mean SW out')
    ax[3].plot(df_mean.index, df_mean.SWout_Avg, c='grey', linestyle='--', linewidth=0.5, label='daily mean SW out')
    ax[3].set_ylim([0, 900])
    ax[3].grid('both')
    ax[3].legend()
    ax[3].set_title('Shortwave radiation')
    ax[3].set_ylabel('$W/m^2$')

    ax[4].plot(df_mnth.index, df_mnth.LWin_Cor, c='k', label='monthly mean LW in')
    ax[4].plot(df_mean.index, df_mean.LWin_Cor, c='k', linestyle='--', linewidth=0.5, label='daily mean LW in')
    ax[4].plot(df_mnth.index, df_mnth.LWout_Cor, c='grey', label='monthly mean LW out')
    ax[4].plot(df_mean.index, df_mean.LWout_Cor, c='grey', linestyle='--', linewidth=0.5, label='daily mean LW out')
    ax[4].set_ylim([100, 500])
    ax[4].grid('both')
    
    ax[4].set_title('Longwave radiation')
    ax[4].set_ylabel('$W/m^2$')

    if st == 'MWK':
        df_mnth_sum = df.loc[smonth:].resample('m').sum()
        ax[5].bar(df_mnth_sum.index, df_mnth_sum.Rain_Tot, width=25, color='k', label='rain, monthly sum')
        ax[5].grid('both')
    
        ax[5].set_ylabel('Rain (mm)')
        ax[5].legend(loc='upper left', ncol=1)
        ax[5].set_title('Precipitation')
    
        ax3 = ax[5].twinx()
        ax3.scatter(df_mean.index, df_mean.Snow, label='Daily mean snow height', c='grey', s=1)
        ax3.set_ylabel('Snow height (m)')
        ax3.yaxis.label.set_color('grey')
        ax3.legend(loc='upper right', ncol=1)
        ax3.set_ylim([0, 2.6])

        ax[4].legend()

    if st == 'VK':
        ax[5].scatter(df_mean.index, df_mean.Snow, label='Daily mean snow height', c='grey', s=1)
        ax[5].set_ylabel('Snow height (m)')
        ax[5].legend(loc='upper right', ncol=1)
        ax[5].grid('both')
        ax[5].set_title('Precipitation')
    
        ax[5].legend(loc='upper left', ncol=1)

        ax[3].legend(loc='center', ncol=4, bbox_to_anchor=[0.5, 0.9])
        ax[4].legend(loc='center', ncol=4, bbox_to_anchor=[0.5, 0.9])

    ax[5].xaxis.set_minor_locator(mdates.MonthLocator())
    plt.tight_layout() 
    fig.savefig('figs/'+st+'_meteo.png', dpi=300)
    return(df_mnth_p)


def plot_windrose_subplots(data, axx, color=None, **kwargs):
    """wrapper function to create subplots per axis"""
    ax = plt.gca()
    ax = WindroseAxes.from_ax(ax=ax)
    plot_windrose(data['Wdir_Corr'].values, data['Wspeed'].values, ax=ax, **kwargs)


def windplot(df1, df2):
    df1['month'] = df1.index.month
    fig = plt.figure(figsize=(8, 5))
    rect = [0.04, 0.0, 0.4, 0.9] 
    wa = WindroseAxes(fig, rect)
    fig.add_axes(wa)
    bins = np.arange(0, 25, 5)
    wa.bar(df1.Wdir, df1.Wspeed, normed=True, opening=0.8, edgecolor="white", bins=bins)
    wa.set_title('MWK')

    rect2 = [0.5, 0.0, 0.4, 0.9] 
    wa2 = WindroseAxes(fig, rect2)
    fig.add_axes(wa2)
    bins = np.arange(0, 25, 5)
    wa2.bar(df2.Wdir, df2.Wspeed, normed=True, opening=0.8, edgecolor="white", bins=bins)
    wa2.set_legend()
    wa2.set_title('VK')
    fig.savefig('figs/windroses.png', dpi=300)


def PDD(df1, df2):
    fig, ax = plt.subplots(2, 1, figsize=(8, 5))
    ax = ax.flatten()
    gl = ['AWS_MWK', 'AWS_VK']
    ln = ['--', '-']
    clr = ['k', 'grey']
    for i, df in enumerate([df1, df2]):
        if gl[i] == 'AWS_MWK':
            df = df.loc[df.index>='2021-01-01']
            param = 'Tair_Avg'
            lns = '-'
        if gl[i] == 'AWS_VK':
            df = df.loc[df.index>='2020-01-01']
            param = 'Tair_Avg'
            lns = '--'
        df_daily = df.resample('D').mean()
        df_daily['doy'] = df_daily.index.dayofyear
        # set pdd column
        df_daily['pdd'] = 0.0
        df_daily['pdd'].loc[df_daily[param]>0.0] = df_daily[param].loc[df_daily[param]>0.0]
        # cumsum, restart every year
        df_daily['cpdd'] = df_daily.groupby(df_daily.index.year)['pdd'].cumsum()

        ax[0].plot(df_daily.index, df_daily['cpdd'], label=gl[i], color='k', linestyle=ln[i])

        for y in [2021, 2022, 2023]:
            tmp = df_daily.loc[df_daily.index.year == y]
            if y == 2021:
                cl = 'grey'
            if y == 2022:
                cl = 'k'
            if y == 2023:
                cl = 'r'
            ix = pd.to_datetime(tmp.doy-1, unit='D', origin=str(2022))
            ax[1].plot(ix, tmp['cpdd'], label=gl[i]+'-'+str(y), linestyle=ln[i], color=cl)

    ax[1].set_xlim([pd.to_datetime('2022-05-01'), pd.to_datetime('2022-12-01')])
    # use formatters to specify major and minor ticks
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax[1].xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
    ax[0].set_ylabel('Cumulative PDD (°C)')
    ax[1].set_ylabel('Cumulative PDD (°C)')

    ax[0].legend()
    ax[0].grid('both')
    ax[1].legend()
    ax[1].grid('both')

    fig.savefig('figs/PDD.png', dpi=300)



def SnowPlot(ds_QUA, gl):
    fig, ax = plt.subplots(1, 1, figsize=(12,6))

    print(ds_QUA.Snow.head())
    ax.scatter(ds_QUA.index, ds_QUA.Snow, s=2, color='k', label='no filter')

    clean = ds_QUA.loc[ds_QUA.Snow_flag==0]
    ax.scatter(clean.index, clean.Snow, color='red', s=2, label='filters and manual date range')

    print('SNOW PERCENTAGE - total, includes out of date range:', gl, 100 - 100* len(clean['Snow'].dropna()) / len(ds_QUA.index))

    ax.set_ylim([0, 2.64])
    ax.set_title(gl)
    ax.set_ylabel('Snow height (m)')
    ax.legend(loc='upper right')
    ax.grid('both')
    # fig.savefig('figs/'+gl+'_snow.png')



