# ! /usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
# import glob
# import AWS_plots_both as AWSplots

# supress copy warning - careful 
pd.options.mode.chained_assignment = None  # default='warn'



# test = pd.read_csv('AWS/AWS_MWK_proc.csv', skiprows=2)# header=1)
# print(test)

# test = pd.read_csv('AWS/AWS_MWK_raw.csv', skiprows=2)
# print(test)

# test = pd.read_csv('AWS/AWS_VK_proc.csv', skiprows=[0,2])#, header=1)
# print(test.SWout_Avg)

# fig, ax = plt.subplots()
# ax.plot(test.Snow)
# ax.plot(test.loc[test.Snow_flag==0]['Snow'])
# plt.show()

# test = pd.read_csv('AWS/AWS_VK_raw.csv', skiprows=2)
# print(test)

    # fig, ax = plt.subplots(1, 1, figsize=(12,6))
    # ax.scatter(ds_QUA.index, ds_QUA.Snow, s=2, color='k', label='no filter')
    # ax.scatter(ds_QUA.index, ds_QUA['Snow_clean2'], color='red', s=2, label='filters and manual date range')

    # print('SNOW PERCENTAGE - total, includes out of date range:', st, 100 - 100* len(ds_QUA['Snow_clean2'].dropna()) / len(ds_QUA.index))
    # # ax.scatter(ds_QUA.index, ds_QUA['snow_d'], color='blue', s=2, label='resample ffill')
    # # ax.scatter(ds_QUA.loc[ds_QUA['Snow_flag']==6].index, ds_QUA.loc[ds_QUA['Snow_flag']==6]['Snow'], color='magenta', s=4)
    # # ax.scatter(ds_QUA.resample('d').median().index, ds_QUA.resample('d').median()['Snow_clean2'], color='green', s=10, label='daily median')
    # ax.set_ylim([0, 2.64])
    # ax.set_title(st)
    # ax.set_ylabel('Snow height (m)')
    # ax.legend(loc='upper right')
    # ax.grid('both')
    # fig.savefig('figs/'+st+'_snow.png')
    
    # # stop
    # print(dfFlags)
    # print(dfFlags.sum())
# stop


# # some checks for SW radiation
# def SWrad(ds, st):
#     ds = ds[['SWout_Avg', 'SWin_Avg', 'LWout_Cor', 'LWin_Cor', 'SWout_Avg_flag', 'SWin_Avg_flag' , 'LWin_Cor_flag', 'LWout_Cor_flag']]
#     fig, ax = plt.subplots(1, 1, figsize=(10,6))
#     ds['night_flag'] = 0
#     ds['night_flag'].loc[(ds.index.hour >=18) | (ds.index.hour <=5)] = 1

#     isweird = ds.loc[ds.SWout_Avg_flag > 1]

#     print('swout>swin, perc:', 100 *len(isweird) / len(ds))

#     isnight = ds.loc[(ds.night_flag > 0) & (ds.SWout_Avg_flag > 1)]

#     print('swout>swin & night, perc:', 100 *len(isnight) / len(ds))

#     ax.plot(ds.index, ds.SWin_Avg, c='r', label='SWin')
#     ax.plot(ds.index, ds.SWout_Avg, c='k', label='SWout')
#     ax.scatter(isweird.index, isweird.SWout_Avg, c='green', s=4, label='SWout>SWin', zorder=12)
#     ax.scatter(isnight.index, isnight.SWout_Avg, c='magenta', s=4, label='SWout>SWin, night', zorder=12)
#     # ax0 = ax[0].twinx()
#     # ax0.plot(ds.index, ds.SWout_Avg / ds.SWin_Avg)
#     ax.set_title(st)
#     ax.legend()
#     fig.savefig('figs/'+st+'_shortwave_rad.png')

#     plt.show()

# # produces some statistics and prints to csv
# def writeTablesPOR(ds_QUA, st):
#     cl = ['Tair_Avg', 'Hum_Avg', 'Press_Avg', 'SWin_Avg', 'SWout_Avg', 'LWin_Cor', 'LWout_Cor', 'Rain_Tot', 'Wdir', 'Wspeed']
#     porDF = pd.DataFrame(columns=cl, index=['firstvalid', 'lastvalid', 'percent'])
#     for c in cl:
#         porDF.loc['firstvalid', c] = ds_QUA[c].first_valid_index()
#         porDF.loc['lastvalid', c] = ds_QUA[c].last_valid_index()
#         # count flags only for out of range or erronous, not gaps:
#         porDF.loc['percent', c] = 100 * ds_QUA[c+'_flag'].loc[ds_QUA[c+'_flag'] > 1].count() / len(ds_QUA[c+'_flag'])

#     porDF.to_csv('out/'+st+'_counts_dates.csv')

# hier kennzahlen für  SW flags in der nacht, usw
# SWrad(dsMWK_CORR, 'MWK')
# SWrad(dsVK_CORR, 'VK')

# # not all snow flags included in df_Flags
# print(dfFlags_MWK[['percent_SWin', 'percent_SWout']])
# print(dfFlags_VK[['percent_SWin', 'percent_SWout']])

# write tables with period of record and percentage of flagged data to csv files in "out" folder.
# Does not include snow!
# writeTablesPOR(dsMWK_CORR, 'MWK')
# # note that this still contains rain and rain flag columns - ignore those.
# writeTablesPOR(dsVK_CORR, 'VK')





# script to deal with VK and MWK AWS data
#set file paths to raw data MWK:
fld = "AWS/mullwitzkees_code_updated_28.09.23/"
f1 = fld+"20200810-20210921_AWS_DH_ohne_NR01.dat"
f2 = fld+"20210921-20231031_AWS_DH_gesamt_mit_NR01.dat"

#set file paths VK:
fldVK = "AWS/Vek_code_updated_28.09.23/"
vkfile = fldVK+"20190919-20231031_AWS_VEK_allesbisher.dat"


## helper functions:
# read the .dat files:
def readfile(f):
    ds = pd.read_csv(f, sep = ',', skiprows=[0,2,3], parse_dates=True)
    # set date as index and fix the format. Time is in UTC (checked)
    ds.set_index('TIMESTAMP', inplace=True)
    ds.index = pd.to_datetime(ds.index, format='%Y-%m-%d %H:%M:%S')

    # convert accidental strings in numeric values
    ds = ds.astype(float)

    # ensure regular 10 minute interval
    ds_resample = ds.resample('10min').mean()
    # check how this affects the index
    ix_dif=ds.index.difference(ds_resample.index, sort=False)
    if len(ix_dif)>0:
        print('RESAMPLING ISSUE - CHECK')
    
    # Make sure that all NaN values are `np.nan` not `'NAN'` (strings)
    ds_resample = ds_resample.replace('NAN', np.nan)

    return(ds_resample, ds)


# set flag for no data:
def flagSysError(df, flag, param):
    df[flag].loc[(df[param].isnull())] = 1
    return(df)


# set flags for data outside of sensor range:
def flagRange(df, flag, param, low, high):
    if param == 'Tair_Avg':
        df[flag].loc[(df[param].values.astype(np.float64) <= low) | (df[param].values.astype(np.float64) >= high)] = 2
    else:
        df[flag].loc[(df[param].values.astype(np.float64) < low) | (df[param].values.astype(np.float64) > high)] = 2
    return(df)


# count occurence of flags
def CountFlags(df, param):
    nrs = []
    for flag in [1, 2, 3, 4, 5]:
        nr = df[param+'_flag'].loc[df[param+'_flag']==flag].shape[0]
        nrs.append(nr)
    return(nrs)


# additional processing, set flags:
def processData(ds_resample, st):
    # create a new df that includes quality flags (and excludes unneccessary columns??- add that?)
    ds_QUA = ds_resample.copy()
    ds_QUA = ds_QUA.astype(float)

    # flag battery value when battery is less than 11V, below that the logger doesn't work reliably (Martin checked the instrument documentation and that seems to be the only relevant limit)
    ds_QUA['Batt_Min_flag'] = 0
    ds_QUA.Batt_Min_flag.loc[(ds_QUA.Batt_Min.values.astype(np.float64) <= 11)] = 1

    # TEMPERATURE
    #Set flags for air temp:
    ds_QUA['Tair_Avg_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Tair_Avg_flag', 'Tair_Avg')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'Tair_Avg_flag', 'Tair_Avg', -40, 60)

    # number of incidences of each flag - write to data frame
    dfFlags = pd.DataFrame(index=[1, 2, 3, 4, 5], columns=['nr_T', 'percent_T'])
    dfFlags['nr_T'] = CountFlags(ds_QUA, 'Tair_Avg')
    dfFlags['percent_T'] = 100 * dfFlags['nr_T'] / len(ds_QUA.Tair_Avg)

    # REL HUM
    #Set flags for relative humidity:
    ds_QUA['Hum_Avg_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Hum_Avg_flag', 'Hum_Avg')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'Hum_Avg_flag', 'Hum_Avg', 0, 100)

    dfFlags['nr_Hum'] = CountFlags(ds_QUA, 'Hum_Avg')
    dfFlags['percent_Hum_Avg'] = 100 * dfFlags['nr_Hum'] / len(ds_QUA.Hum_Avg)

    # PRESSURE
    #Set flags for relative humidity:
    ds_QUA['Press_Avg_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Press_Avg_flag', 'Press_Avg')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'Press_Avg_flag', 'Press_Avg', 500, 1100)

    dfFlags['nr_Press'] = CountFlags(ds_QUA, 'Press_Avg')
    dfFlags['percent_Press_Avg'] = 100 * dfFlags['nr_Press'] / len(ds_QUA.Hum_Avg)

    # WIND
    # Set general flags for wind dir:
    ds_QUA['Wdir_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Wdir_flag', 'Wdir')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'Wdir_flag', 'Wdir', 0, 360)

    # Set general flags for wind speed:
    ds_QUA['Wspeed_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Wspeed_flag', 'Wspeed')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'Wspeed_flag', 'Wspeed', 0, 60)

    # Set general flags for wind speed:
    ds_QUA['Wspeed_Max_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Wspeed_Max_flag', 'Wspeed_Max')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'Wspeed_Max_flag', 'Wspeed', 0, 60)

    # RIMING!
    # Wind speed: flag if it i s0 for more than 1 hour consecutively. 
    # make column that is 0 if wind speed is greater than 0 and 1 otherwise:
    ds_QUA['Wspeed_0'] = 0
    ds_QUA['Wspeed_0'].where(ds_QUA['Wspeed'] != 0, 1, inplace=True)
    # make column counting consecutive ones in the above column:
    ds_QUA['consecutive'] = ds_QUA['Wspeed_0'].groupby((ds_QUA['Wspeed_0'] != ds_QUA['Wspeed_0'].shift()).cumsum()).transform('size') * ds_QUA['Wspeed_0']
    ds_QUA['shift'] = ds_QUA['Wspeed_0'] != ds_QUA['Wspeed_0'].shift()

    # set flag to 3 if windspeed is 0 for more than 6 consecutive values (1 hour)
    ds_QUA['Wspeed_flag'].loc[ds_QUA['consecutive'] > 6] = 3

    #Wind direction: flag all 3 consecutive (OR MORE) wind direction measurements that fall within a defined threshold
    # define threshold (sensor resolution = 3 deg, adjust as needed)
    dm = 3
    ds_QUA['Wdiff'] = ds_QUA['Wdir'].diff(periods=-1)
    # binary column: 0 default, 1 if diff < 3
    ds_QUA['Wdir_bin'] = 0
    ds_QUA['Wdir_bin'].loc[ds_QUA['Wdiff'].abs() < dm] = 1
    # column counting consecutive occurence of diff below threshold:
    ds_QUA['consecutive_wdir'] = ds_QUA['Wdir_bin'].groupby((ds_QUA['Wdir_bin'] != ds_QUA['Wdir_bin'].shift()).cumsum()).transform('size') * ds_QUA['Wdir_bin']

    # set flag to 3 if wind dir changes less than 3 deg for more than 3 consecutive measurements
    ds_QUA['Wdir_flag'].loc[ds_QUA['consecutive_wdir']>3] = 3

    dfFlags['nr_Wdir'] = CountFlags(ds_QUA, 'Wdir')
    dfFlags['percent_Wdir'] = 100 * dfFlags['nr_Wdir'] / len(ds_QUA.Wdir)

    dfFlags['nr_Wspeed'] = CountFlags(ds_QUA, 'Wspeed')
    dfFlags['percent_Wspeed'] = 100 * dfFlags['nr_Wspeed'] / len(ds_QUA.Wspeed)

    dfFlags['nr_Wspeed_Max'] = CountFlags(ds_QUA, 'Wspeed_Max')
    dfFlags['percent_Wspeed_Max'] = 100 * dfFlags['nr_Wspeed_Max'] / len(ds_QUA.Wspeed_Max)

    # drop the extra wind processing columns:
    ds_QUA.drop(columns=['Wspeed_0', 'consecutive', 'shift', 'Wdiff', 'Wdir_bin', 'consecutive_wdir'], inplace=True)

    # RADIATION SW
    # Set general flags for SW radiation:
    ds_QUA['SWin_Avg_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'SWin_Avg_flag', 'SWin_Avg')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'SWin_Avg_flag', 'SWin_Avg', 0, 2000)

    # flag instances where SWout>SWin: 4
    ds_QUA['SWin_Avg_flag'].loc[ds_QUA['SWout_Avg'] > ds_QUA['SWin_Avg']] = 3

    dfFlags['nr_SWin'] = CountFlags(ds_QUA, 'SWin_Avg')
    dfFlags['percent_SWin'] = 100 * dfFlags['nr_SWin'] / len(ds_QUA.SWin_Avg)

    ds_QUA['SWout_Avg_flag'] = 0
    # flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'SWout_Avg_flag', 'SWout_Avg')
    # flag values outside of sensor range: 2
    ds_QUA = flagRange(ds_QUA, 'SWout_Avg_flag', 'SWout_Avg', 0, 2000)

    # flag instances where SWout>SWin: 4
    ds_QUA['SWout_Avg_flag'].loc[ds_QUA['SWout_Avg'] > ds_QUA['SWin_Avg']] = 3

    dfFlags['nr_SWout'] = CountFlags(ds_QUA, 'SWout_Avg')
    dfFlags['percent_SWout'] = 100 * dfFlags['nr_SWout'] / len(ds_QUA.SWout_Avg)

    # RADIATION LW
    # Correction with sensor temperature: (CHECK W MARTIN)
    ds_QUA['LWin_Cor'] = ds_QUA['LWin_Avg']+5.67*10**-8 * ds_QUA['NR01K_Avg']**4
    ds_QUA['LWout_Cor'] = ds_QUA['LWout_Avg']+5.67*10**-8 * ds_QUA['NR01K_Avg']**4

    # Set general flags for LW radiation:
    ds_QUA['LWin_Cor_flag'] = 0
    # flag system error value: 1, flag no data values: 2
    ds_QUA = flagSysError(ds_QUA, 'LWin_Cor_flag', 'LWin_Cor')
    # flag values outside of sensor range: 3
    ds_QUA = flagRange(ds_QUA, 'LWin_Cor_flag', 'LWin_Cor', 0, 1000)

    ds_QUA['LWout_Cor_flag'] = 0
    # flag system error value: 1, flag no data values: 2
    ds_QUA = flagSysError(ds_QUA, 'LWout_Cor_flag', 'LWout_Cor')
    # flag values outside of sensor range: 3
    ds_QUA = flagRange(ds_QUA, 'LWout_Cor_flag', 'LWout_Cor', 0, 1000)

    dfFlags['nr_LWin'] = CountFlags(ds_QUA, 'LWin_Cor')
    dfFlags['percent_LWin'] = 100 * dfFlags['nr_LWin'] / len(ds_QUA.LWin_Cor)

    dfFlags['nr_LWout'] = CountFlags(ds_QUA, 'LWout_Cor')
    dfFlags['percent_LWout'] = 100 * dfFlags['nr_LWout'] / len(ds_QUA.LWout_Cor)


    # PRECIP (only MWK)
    # Set general flags for precipitation
    ds_QUA['Rain_Tot_flag'] = 0
    # flag system error value: 1, flag no data values: 2
    ds_QUA = flagSysError(ds_QUA, 'Rain_Tot_flag', 'Rain_Tot')
    # flag values outside of sensor range: 3
    ds_QUA = flagRange(ds_QUA, 'Rain_Tot_flag', 'Rain_Tot', 0, 50) #upper limit of range? none given on manufacturer website
    
    # flag precip values when temp below 0 
    ds_QUA['Rain_Tot_flag'].loc[(ds_QUA['Tair_Avg'] <= 0)] = 3
    # flag precip values when temp between 0 and 4 (--> look only at liquid precip, discuss what threshold T to use)
    ds_QUA['Rain_Tot_flag'].loc[(ds_QUA['Tair_Avg'] > 0) & (ds_QUA['Tair_Avg'] <= 4)] = 4

    dfFlags['nr_Rain_Tot'] = CountFlags(ds_QUA, 'Rain_Tot')
    dfFlags['percent_Rain_Tot'] = 100 * dfFlags['nr_Rain_Tot'] / len(ds_QUA.Rain_Tot)

    return(ds_QUA, dfFlags)


# deal with snow depth - requires additional QC due to sensor issues:
def processSnow(ds_QUA, m, dfFlags, sdate, edate, st):

    # Correct distance value with air temp: 
    ds_QUA['Dist_Cor'] = ds_QUA['Dist_Avg']*np.sqrt((ds_QUA['Tair_Avg']+273.15)/273.15)
    # Subtract sensor height:
    ds_QUA['Snow'] = m - ds_QUA['Dist_Cor']

    # Set flags for air temp:
    ds_QUA['Snow_flag'] = 0
    #flag no data values: 1
    ds_QUA = flagSysError(ds_QUA, 'Snow_flag', 'Snow')
    # flag values outside of sensor range (negative or larger than sensor height - sensor accuracy): 2
    ds_QUA = flagRange(ds_QUA, 'Snow_flag', 'Snow', 0, m)#-0.01)

    # flag all values where difference between consecutive measurements is large (?): 2cm
    # threshold:
    tr = 0.02
    ds_QUA['Snow_flag'].loc[ds_QUA['Snow'].diff().abs() > tr ] = 3

    # manual flag for outside of viable date range (based on visual inspection): 4
    ds_QUA.loc[(ds_QUA.index < sdate) | (ds_QUA.index > edate), 'Snow_flag'] = 4

    ds_QUA['Snow_clean1'] = ds_QUA['Snow']

    ds_QUA.loc[(ds_QUA['Snow_flag'] != 0), 'Snow_clean1'] = np.nan

    # compute daily snow height (or 48h rolling mean) and reindex to 10 minutes
    # d_snow = ds_QUA['Snow_clean1'].resample('24h').mean()
    d_snow = ds_QUA['Snow_clean1'].rolling('48h', min_periods=1, center=True).mean()
    ds_QUA['snow_d'] = d_snow.resample('10min').ffill()

    ds_QUA['Snow_flag2'] = ds_QUA['Snow_flag']

    # flag if dif greater than some value
    ds_QUA['Snow_flag2'].loc[abs(ds_QUA['snow_d']-ds_QUA['Snow_clean1']) > 0.15] = 5
    nr = ds_QUA['Snow_flag2'].loc[ds_QUA['Snow_flag2']==5].shape[0]

    subset = ds_QUA.loc[(ds_QUA.index >= sdate) & (ds_QUA.index <= edate)]

    dfFlags['nr_Snow'] = CountFlags(subset, 'Snow')
    dfFlags['percent_Snow'] = 100 * dfFlags['nr_Snow'] / len(subset.Snow)

    dfFlags.loc[5, 'nr_Snow'] = nr
    dfFlags.loc[5, 'percent_Snow'] = nr / len(ds_QUA.Snow)

    ds_QUA['Snow_clean2'] = ds_QUA['Snow_clean1']
    ds_QUA.loc[(ds_QUA['Snow_flag2'] != 0), 'Snow_clean2'] = np.nan
    ds_QUA.loc[(ds_QUA.index < sdate) | (ds_QUA.index > edate), 'Snow_clean2'] = np.nan
    
    ds_QUA['Snow_flag_All'] = ds_QUA['Snow_flag']
    ds_QUA['Snow_flag_All'].loc[ds_QUA.Snow_flag2==5] = 3

    return(ds_QUA, dfFlags)


# writes raw data to file:
def writetofile(dat, st):
    if st == 'MWK':
        header1 = '"TOA5","DH","CR3000","13179","CR3000.Std.32.05","CPU:2021_DH.CR3","10638","DH"'
        header2 = '"TIMESTAMP","RECORD","Batt_Min","Tair_Avg","Hum_Avg","Press_Avg","SWin_Avg","SWout_Avg","LWin_Avg","LWout_Avg","NR01K_Avg","Wspeed","Wdir","Wspeed_Max","Dist_Avg","Rain_Tot"'
        header3 = '"TS","RN","Volt","Celsius","%","mbar","W/m2","W/m2","W/m2","W/m2","Kelvin","m/s","degree","m/s","m","mm"'

    if st == 'VK':
        header1 = '"TOA5","VEN_direct","CR3000","12218","CR3000.Std.31.08","CPU:Ven_CR3000.CR3","4721","ven"'
        header2 = '"TIMESTAMP","RECORD","Batt_Min","Tair_Avg","Hum_Avg","Press_Avg","SWin_Avg","SWout_Avg","LWin_Avg","LWout_Avg","NR01K_Avg","Wspeed","Wdir","Wspeed_Max","Dist_Avg"'
        header3 = '"TS","RN","Volt","Celsius","%","mbar","W/m2","W/m2","W/m2","W/m2","Kelvin","m/s","degree","m/s","m"'

    fn = 'AWS/AWS_'+st+'_raw.csv'

    with open(fn, 'a') as file:
        file.write(header1+'\n')
        file.write(header2+'\n')
        file.write(header3+'\n')
        # file.write(header4+'\n')
        dat.to_csv(file, header=False, index=True, sep=',')


# writes processed data to file:
def writetofileProc(dat, st):
    if st == 'MWK':
        header1 = '"TOA5","DH","CR3000","13179","CR3000.Std.32.05","CPU:2021_DH.CR3","10638","DH"'
        header2 = '"TIMESTAMP","Batt_Min","Tair_Avg","Hum_Avg","Press_Avg","Wspeed","Wdir","Wspeed_Max","SWin_Avg","SWout_Avg","LWin_Cor","LWout_Cor","Rain_Tot","Dist_Cor","Snow","Batt_Min_flag","Tair_Avg_flag","Hum_Avg_flag","Press_Avg_flag","Wdir_flag","Wspeed_flag","Wspeed_Max_flag","SWin_Avg_flag","SWout_Avg_flag","LWin_Cor_flag","LWout_Cor_flag","Rain_Tot_flag","Snow_flag"'
        header3 = '"date time (UTC)","Volt","Celsius","%","mbar","m/s","degree","m/s","W/m2","W/m2","W/m2","W/m2","mm","m","m",,,,,,,,,,,,,'

    if st == 'VK':
        header1 = '"TOA5","VEN_direct","CR3000","12218","CR3000.Std.31.08","CPU:Ven_CR3000.CR3","4721","ven"'
        header2 = '"TIMESTAMP","Batt_Min","Tair_Avg","Hum_Avg","Press_Avg","Wspeed","Wdir","Wspeed_Max","SWin_Avg","SWout_Avg","LWin_Cor","LWout_Cor","Dist_Cor","Snow","Batt_Min_flag","Tair_Avg_flag","Hum_Avg_flag","Press_Avg_flag","Wdir_flag","Wspeed_flag","Wspeed_Max_flag","SWin_Avg_flag","SWout_Avg_flag","LWin_Cor_flag","LWout_Cor_flag","Snow_flag"'
        header3 = '"date time (UTC)","Volt","Celsius","%","mbar","m/s","degree","m/s","W/m2","W/m2","W/m2","W/m2","m","m",,,,,,,,,,,,,,'

    fn = 'AWS/AWS_'+st+'_proc.csv'

    with open(fn, 'a') as file:
        file.write(header1+'\n')
        file.write(header2+'\n')
        file.write(header3+'\n')
        dat.to_csv(file, header=False, index=True, sep=',')



# MWK - read and concatenate the two datafiles before proceeding:
df1, f1_og = readfile(f1)
df2, f2_og = readfile(f2)
dsMWK = pd.concat([df1, df2])
dsMWK_og = pd.concat([f1_og, f2_og])


# write raw data to new csv
dsMWK_og = dsMWK_og[["RECORD","Batt_Min","Tair_Avg","Hum_Avg","Press_Avg","SWin_Avg","SWout_Avg","LWin_Avg","LWout_Avg","NR01K_Avg","Wspeed","Wdir","Wspeed_Max","Dist_Avg","Rain_Tot"]]
writetofile(dsMWK_og, 'MWK')

# quick check for duplicate indices
print('number of duplicate indices MWK:', sum(dsMWK.index.duplicated()))
# rename for consistency
dsMWK_resample = dsMWK.copy()

# VK - read the file:
dsVK_resample, dsVK_og = readfile(vkfile)

# write raw data to new csv
dsVK_og = dsVK_og[["RECORD","Batt_Min","Tair_Avg","Hum_Avg","Press_Avg","SWin_Avg","SWout_Avg","LWin_Avg","LWout_Avg","NR01K_Avg","Wspeed","Wdir","Wspeed_Max","Dist_Avg"]]
writetofile(dsVK_og, 'VK')

# quick check for duplicate indices
print('number of duplicate indices VK:', sum(dsVK_resample.index.duplicated()))


# add flags, part 1:
dsMWK_CORR, dfFlags_MWK = processData(dsMWK_resample, 'MWK')
dsVK_CORR, dfFlags_VK = processData(dsVK_resample, 'VK')

# process snow data (part 2):
dsMWK_CORR, dfFlags_MWK = processSnow(dsMWK_CORR, 2.38, dfFlags_MWK,  '2019-07-01', '2022-06-02', 'MWK')
dsVK_CORR, dfFlags_VK = processSnow(dsVK_CORR, 2.64, dfFlags_VK, '2020-07-01', '2022-06-28', 'VK')

# round to appropriate number of decimals
dsMWK_CORR['Snow'] = dsMWK_CORR['Snow'].round(decimals=2)
dsVK_CORR['Snow'] = dsVK_CORR['Snow'].round(decimals=2)
dsMWK_CORR['Dist_Cor'] = dsMWK_CORR['Dist_Cor'].round(decimals=2)
dsVK_CORR['Dist_Cor'] = dsVK_CORR['Dist_Cor'].round(decimals=2)

dsMWK_CORR['LWin_Cor'] = dsMWK_CORR['LWin_Cor'].round(decimals=5)
dsMWK_CORR['LWout_Cor'] = dsMWK_CORR['LWout_Cor'].round(decimals=5)

dsVK_CORR['LWin_Cor'] = dsVK_CORR['LWin_Cor'].round(decimals=5)
dsVK_CORR['LWout_Cor'] = dsVK_CORR['LWout_Cor'].round(decimals=5)


# write files of data with flags:
cols_for_file = ['Batt_Min','Tair_Avg','Hum_Avg','Press_Avg','Wspeed','Wdir','Wspeed_Max',
'SWin_Avg','SWout_Avg','LWin_Cor','LWout_Cor','Rain_Tot','Dist_Cor','Snow', 
'Batt_Min_flag','Tair_Avg_flag','Hum_Avg_flag','Press_Avg_flag',
'Wdir_flag','Wspeed_flag','Wspeed_Max_flag','SWin_Avg_flag','SWout_Avg_flag','LWin_Cor_flag','LWout_Cor_flag',
'Rain_Tot_flag','Snow_flag_All']

mwkforfile = dsMWK_CORR[cols_for_file]

writetofileProc(mwkforfile, 'MWK')

vkforfile = dsVK_CORR[cols_for_file]
# drop 'Rain_Tot' at VK because there is no precip measurement at that station:
vkforfile.drop(columns=['Rain_Tot', 'Rain_Tot_flag'], inplace=True)

writetofileProc(vkforfile, 'VK')

