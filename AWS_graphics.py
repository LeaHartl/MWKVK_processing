import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import AWS_plots_helpers as AWSplots


def loadFiles(gl):
    raw = pd.read_csv('AWS/AWS_'+gl+'_raw.csv', skiprows=[0,2])
    raw.set_index('TIMESTAMP', inplace=True)
    raw.index = pd.to_datetime(raw.index, format='%Y-%m-%d %H:%M:%S')

    proc = pd.read_csv('AWS/AWS_'+gl+'_proc.csv', skiprows=[0,2])
    proc.set_index('TIMESTAMP', inplace=True)
    proc.index = pd.to_datetime(proc.index, format='%Y-%m-%d %H:%M:%S')

    return(raw, proc)

# load the files produced in AWS_processing.py:
MWK_raw, MWK_proc1 = loadFiles('MWK')
print(MWK_raw.head())
print(MWK_proc1.head())
VK_raw, VK_proc1 = loadFiles('VK')

MWK_proc = MWK_proc1.copy()
VK_proc = VK_proc1.copy()


# relevant flags:
flagsMWK = ['Batt_Min_flag', 'Tair_Avg_flag', 'Hum_Avg_flag', 'Press_Avg_flag', 'Wdir_flag', 'Wspeed_flag',
         'Wspeed_Max_flag', 'SWin_Avg_flag', 'SWout_Avg_flag', 'LWin_Cor_flag', 'LWout_Cor_flag',
         'Rain_Tot_flag', 'Snow_flag']

# no precip at VK:
flagsVK = ['Batt_Min_flag', 'Tair_Avg_flag', 'Hum_Avg_flag', 'Press_Avg_flag', 'Wdir_flag', 'Wspeed_flag',
         'Wspeed_Max_flag', 'SWin_Avg_flag', 'SWout_Avg_flag', 'LWin_Cor_flag', 'LWout_Cor_flag',
         'Snow_flag']


# set data with flags to np.nan before passing to plotting functions:
for flag in flagsMWK:
    MWK_proc.loc[(MWK_proc[flag] != 0), flag[:-5]] = np.nan
for flag in flagsVK:   
    VK_proc.loc[(VK_proc[flag] != 0), flag[:-5]] = np.nan


## uncomment to print some statistics:
# print('highest MWK', MWK_proc['Tair_Avg'].loc[MWK_proc.index==MWK_proc.Tair_Avg.idxmax()])
# print('lowest MWK', MWK_proc['Tair_Avg'].loc[MWK_proc.index==MWK_proc.Tair_Avg.idxmin()])
# print('highest VK', VK_proc['Tair_Avg'].loc[VK_proc.index==VK_proc.Tair_Avg.idxmax()])
# print('lowest VK', VK_proc['Tair_Avg'].loc[VK_proc.index==VK_proc.Tair_Avg.idxmin()])

# print('max gust MWK', MWK_proc.loc[MWK_proc.index==MWK_proc.Wspeed_Max.idxmax()][['Wspeed_Max', 'Wspeed', 'Wdir']])
# print('max gust VK', VK_proc.loc[VK_proc.index==VK_proc.Wspeed_Max.idxmax()][['Wspeed_Max', 'Wspeed', 'Wdir']])

# print('max wind MWK', MWK_proc.loc[MWK_proc.index==MWK_proc.Wspeed.idxmax()][['Wspeed_Max', 'Wspeed', 'Wdir']])
# print('max wind VK', VK_proc.loc[VK_proc.index==VK_proc.Wspeed.idxmax()][['Wspeed_Max', 'Wspeed', 'Wdir']])


# make plots:

# time series of station POR:
month_T_MWK = AWSplots.timeseriesplot(MWK_proc, 'MWK')
month_T_VK = AWSplots.timeseriesplot(VK_proc, 'VK')

# PDD plot:
# AWSplots.PDD(MWK_proc, VK_proc)

# # Wind rose plot:
# AWSplots.windplot(MWK_proc, VK_proc)

# # Plot to compare filtered and unfiltered snow data:
# AWSplots.SnowPlot(MWK_proc1, 'MWK')
# AWSplots.SnowPlot(VK_proc1, 'VK')


plt.show()

