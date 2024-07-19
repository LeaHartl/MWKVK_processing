import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import glob
import csv as cf
import AWS_plots_helpers as AWSplots

# supress copy warning - careful 
pd.options.mode.chained_assignment = None  # default='warn'

# MWK AWS data set:
# https://doi.pangaea.de/10.1594/PANGAEA.965646
# VK AWS data set:
# https://doi.pangaea.de/10.1594/PANGAEA.965647
# --> Download a zip file of all data sets in the collection and unpack the zip file. 

# set the file paths to the unpacked .tab files:
folder_MWK = 'pangaea_dl/MWK_meteorology/datasets/'
folder_VK = 'pangaea_dl/VK_meteorology/datasets/'

# load the quality controlled data from the yearly files:
def loadfiles(folder, gl):
    dfs = []
    fls = glob.glob(folder+gl+'_proc*.tab')
    # this is a loop to identify the header line in the pangaea format.
    for f in fls:
        with open(f, 'r') as fin:
            reader = cf.reader(fin)
            for idx, row in enumerate(reader):
                if row[0].startswith('*/'):
                    headerline = idx+1
                    print(row)
                    print(idx)
                    print('header found')
   
        data = pd.read_csv(f, header = headerline, parse_dates=True, delimiter='\t', index_col=0)
        dfs.append(data)

    data_merged = pd.concat(dfs).sort_index()
    return(data_merged)

dataMWK = loadfiles(folder_MWK, 'MWK')
dataVK = loadfiles(folder_VK, 'VK')

# print as reality check:
print(dataMWK.head())
print(dataVK.head())

# dictionary to translate column headers in pangaea file to original names (required for the plotting function, change as needed)
namedict = {'Date/Time (UTC)':'TIMESTAMP',
            'Ubat min [V] (Batt_min; minimum voltage las...)': 'Batt_Min',
            'TTT [°C] (Temp_Avg; 10 minute average, ...)': 'Tair_Avg',
            'RH [%] (Hum_Avg; 10 minute average, C...)': 'Hum_Avg',
            'PPPP [hPa] (Press_Avg; 10 minute average)': 'Press_Avg',
            'SWD [W/m**2] (SWin_Avg; Incoming shortwave ...)': 'SWin_Avg',
            'SWU [W/m**2] (SWout_Avg; Reflected/outgoing...)': 'SWout_Avg',
            'LWD [W/m**2] (LWin_Cor; Incoming longwave r...)': 'LWin_Cor',
            'LWU [W/m**2] (LWout_Cor; Outgoing longwave ...)': 'LWout_Cor',
            'ff [m/s] (Wspeed; 10 minute average, An...)': 'Wspeed',
            'dd [deg] (Wdir; 10 minute average, Anem...)': 'Wdir',
            'ff max [m/s] (Wspeed; 10 minute maximum val...)': 'Wspeed_Max',
            'Precip [mm] (Rain_Tot; unheated)': 'Rain_Tot',
            'Dist [mm] (Dist_Cor; calculated by corre...)': 'Dist_Cor',
            'Snow h [m] (Snow; calcualted by subtracti...)': 'Snow',
            'QF Ubat (Batt_Min_flag, see documentation)': 'Batt_Min_flag',
            'QF air temp (Temp_Avg_flag, see documentation)': 'Tair_Avg_flag',
            'QF RH (Hum_Avg_flag, see documentation)': 'Hum_Avg_flag',
            'QF atmos press (Press_Avg_flag, see documenta...)': 'Press_Avg_flag',
            'QF wind dir (Wdir_flag, see documentation)': 'Wdir_flag',
            'QF wind speed (Wspeed_flag; mean, see docume...)': 'Wspeed_flag',
            'QF wind speed (Wspeed_flag; max, see documen...)': 'Wspeed_Max_flag',
            'QF SWD (SWin_Avg_flag, see documentation)': 'SWin_Avg_flag',
            'QF SWU (SWout_Avg_flag, see documenta...)': 'SWout_Avg_flag',
            'QF LWD (LWin_Cor_flag, see documentation)': 'LWin_Cor_flag',
            'QF LWU (LWout_Cor_flag, see documenta...)': 'LWout_Cor_flag', 
            'QF precip (Rain_Tot_flag, see documentation)': 'Rain_Tot_flag',
            'QF snow h (see documentation)': 'Snow_flag'
            }

dataMWK = dataMWK.rename(mapper=namedict, axis=1)
dataVK = dataVK.rename(mapper=namedict, axis=1)

print(dataVK.head())

# deal with quality flags:
# relevant flags:
flagsMWK = ['Batt_Min_flag', 'Tair_Avg_flag', 'Hum_Avg_flag', 'Press_Avg_flag', 'Wdir_flag', 'Wspeed_flag',
         'Wspeed_Max_flag', 'SWin_Avg_flag', 'SWout_Avg_flag', 'LWin_Cor_flag', 'LWout_Cor_flag',
         'Rain_Tot_flag', 'Snow_flag']

# no precip at VK:
flagsVK = ['Batt_Min_flag', 'Tair_Avg_flag', 'Hum_Avg_flag', 'Press_Avg_flag', 'Wdir_flag', 'Wspeed_flag',
         'Wspeed_Max_flag', 'SWin_Avg_flag', 'SWout_Avg_flag', 'LWin_Cor_flag', 'LWout_Cor_flag',
         'Snow_flag']


# set data with flags to np.nan before passing to plotting functions:
QC_MWK = dataMWK.copy()
QC_VK = dataVK.copy()

for flag in flagsMWK:
    QC_MWK.loc[(QC_MWK[flag] != 0), flag[:-5]] = np.nan

for flag in flagsVK:   
    QC_VK.loc[(QC_VK[flag] != 0), flag[:-5]] = np.nan



# pass the data to the plotting functions:
AWSplots.timeseriesplot(QC_VK, 'VK')
AWSplots.timeseriesplot(QC_MWK, 'MWK')

# PDD plot:
AWSplots.PDD(dataMWK, dataVK)

# Wind rose plot:
AWSplots.windplot(dataMWK, dataVK)

# Plot to compare filtered and unfiltered snow data:
# AWSplots.SnowPlot(MWK_proc1, 'MWK')
# AWSplots.SnowPlot(VK_proc1, 'VK')

plt.show()


