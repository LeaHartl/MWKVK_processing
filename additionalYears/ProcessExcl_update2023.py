import numpy as np
import pandas as pd
import Uncertainties as unc
import datetime as dt

# supress copy warning - careful!
pd.options.mode.chained_assignment = None  # default='warn'

# read BS and MS' excel files of stake, pit & probe point mass balance data
# reformat to match the tabular format of GLAMOS and export


# make table with annual point MB data FOR THE STAKES:
def makeTableAnnual(yrs, fname, gl):
    stks_annual = []

    for yr in yrs:
        # account for different sheet naming convention in the Excel files:
        if gl == 'VK':
            temp = pd.read_excel(fname, str(yr-1)+'-'+str(yr), header=1)
        if gl == 'MWK':
            temp = pd.read_excel(fname, str(yr), header=1)

        basics = pd.DataFrame(columns=['name'])
        basics['name'] = temp['Name']
        basics['x_pos'] = temp['POINT_X']
        basics['y_pos'] = temp['POINT_Y']
        if gl == 'VK':
            basics['z_pos'] = temp['POINT_Z']
        if gl == 'MWK':
            basics['z_pos'] = temp['dgm08']

        # 4 stands for estimated from closest measurement
        basics['position_quality'] = 4

        # raw mass balance in cm ice is not available for the fixed dates because only the final
        # corrected values was documented.
        basics['mb_raw'] = np.nan 

        # mm WE value interpolated from last observation to end of hydrol. year.
        # this is always in the second to last column in the excel files. Make sure there are no
        # inconsistencies in the file to get the correct column!!
        if gl == 'VK':
            basics['mb_we'] = temp[temp.columns.values[-2]].astype(float)
        # In Martin's file the unit needs to be adjusted:
        if gl == 'MWK':
            basics['mb_we'] = temp[temp.columns.values[-2]].astype(float)*10

        # correct for inconsistent sign in stake excel file (value should always be negative, no positive STAKE data)
        basics['mb_we'].loc[basics['mb_we'] > 0] = basics['mb_we']*-1

        # deal with densities: the fixed date mb we value is derived based on a combination of ice and fresh snow densities.
        # exact density is unknown for the fixed dates:
        basics['density'] = np.nan
        # quality flag for ice & snow density combinatinon.
        # this is associated with ~10% raw mb uncertainty. we don't have raw uncertainty, so we will apply this to mb we value.
        basics['density_quality'] = 5
        
        # fixed start and end dates:
        basics['date0'] = int(str(yr-1)+'1001')
        basics['date1'] = int(str(yr)+'0930')

        basics['period'] = (pd.to_datetime(basics['date1'].astype(str), format='%Y%m%d') - pd.to_datetime(basics['date0'].astype(str), format='%Y%m%d')).dt.days

        # print(basics)
        stks_annual.append(basics)
    stks_annual = pd.concat(stks_annual)

    # aditional quality flags and uncertainty-related columns: 
    stks_annual['measurement_quality'] = 5 # 5 is for "reconstructed value (other reason)" to indicate extrapolation to fixed date
    stks_annual['measurement_type'] = 1 # 1 is for stake
    stks_annual['mb_error'] = np.nan # initialize column - this is filled in a later step in Uncertainties.py
    stks_annual['reading_error'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    stks_annual['density_error'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    stks_annual['date_quality'] = 1 # start date and end date exactly known for fixed date stakes.

    # set values for colums that always stay the same:
    # source: who provided the data? BS = Bernd Seiser, MSW = Martin Stocker-Waldhuber
    if gl == 'VK':
        stks_annual['source'] = 'BS' 
    if gl == 'MWK':
        stks_annual['source'] = 'MSW' 

    # set time to 12 (same as in the Swiss data)
    stks_annual['time0'] = 1200
    stks_annual['time1'] = 1200

    stks_annual = stks_annual[['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality',
                               'x_pos', 'y_pos', 'z_pos', 'position_quality', 'mb_raw', 'density',
                               'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                               'mb_error', 'reading_error', 'density_error', 'source']]

    stks_annual = stks_annual.reset_index(drop=True)
    return (stks_annual)


# make table with intermediate MB data FOR THE STAKES:
def makeTableIntermediate(yrs, fname, tabletype, gl):
    stks_interm = []

    for yr in yrs:
        if gl == 'VK':
            temp = pd.read_excel(fname, str(yr-1)+'-'+str(yr), header=1)
        if gl == 'MWK':
            temp = pd.read_excel(fname, str(yr), header=1)
        lencol = len(temp.columns.values)
        # dts: number of dates with measurements = number of colums minus 6 columns that are always
        # present (name, position, corrected value, etc)
        dts = lencol - 6

        intdata = []
        for i, d in enumerate(np.arange(0, dts)):
            basics = pd.DataFrame(columns=['name'])
            basics['name'] = temp['Name']
            basics['x_pos'] = temp['POINT_X']
            basics['y_pos'] = temp['POINT_Y']
            if gl == 'VK':
                basics['z_pos'] = temp['POINT_Z']
            if gl == 'MWK':
                basics['z_pos'] = temp['dgm08']

            # 2 stands for measured by handheld GPS, 4 for estimated from previous measurement - see read me of swiss file and discuss what flag is most appropriate
            basics['position_quality'] = 4
            # for intermediate stake data, density is always density of ice:
            basics['density'] = 0.9 * 1000 
            basics['density_quality'] = 1# 1 stands for ice density
            basics['date_quality'] = 1  # dates exactly known

            # this value refers to the number of columns to skip in the excel file. Needs to be set
            # manually. make sure it is correct and consistent in the excel files!
            offset = 4

            # change this to have it at the end, start out w cumulative value, delete nan values, then make period value!
            # check if data is supposed to be cumulative or per period (excel files contain
            # cumulative values, period values need to be computed from the cumulative values)
            basics['mb_raw_cu'] = temp[temp.columns.values[offset+i]] * -1

            # get end date column for the period: 
            basics['dateEnd'] = temp.columns.values[offset+i]

            if gl == 'VK':
                basics['mb_we_cu'] = basics['mb_raw_cu']*10 * basics['density']/1000 
                # convert to date time
                basics['date_val'] = pd.to_datetime(basics['dateEnd'])
            if gl == 'MWK':
                basics['mb_we_cu'] = basics['mb_raw_cu']*10 * basics['density']/1000 
                # convert to date time
                # check for double date format // may need some adjusting // manually adjusted in xlsx file.
                if len(basics['dateEnd'].astype(str).iloc[0]) < 13:
                    basics['date_val'] = pd.to_datetime(basics['dateEnd'])
                else:
                    # print(basics['dateEnd'])
                    basics['date_val'] = pd.to_datetime(basics['dateEnd'].str[3:],format='%d.%m.%Y')
            
            basics['yr'] = yr
            basics['season'] =  (basics['yr']-1).astype(str)+'-'+basics['yr'].astype(str)

            intdata.append(basics)

        intdata_y = pd.concat(intdata)
        stks_interm.append(intdata_y)

    stks_interm = pd.concat(stks_interm)
    # drop nan values (empty cells in the excel files)
    stks_interm.dropna(subset=['mb_raw_cu'], inplace=True)

    stks_interm['mb_raw'] = np.nan
    stks_interm['d0'] = np.nan

    # print(stks_interm.head())
    for seas in stks_interm.season.unique():
        inter = stks_interm.loc[stks_interm.season == seas]
        
        for st in inter.name.unique():
            inter2 = inter.loc[inter.name==st]

            inter2['cs'] = inter2['mb_raw_cu'].ffill(0).diff()
            inter2['cs2'] = inter2['cs']
            inter2['cs2'].loc[inter2['mb_raw_cu'].isna()] = np.nan

            inter2['d0'] = pd.to_datetime(inter2['date_val'].shift(1))

            stks_interm['mb_raw'].loc[(stks_interm.season == seas) & (stks_interm.name==st)] = inter2['cs2'].values
            stks_interm['d0'].loc[(stks_interm.season == seas) & (stks_interm.name==st)] = inter2['d0'].values
            
    stks_interm['mb_we'] = stks_interm['mb_raw']*10 * stks_interm['density']/1000 
    stks_interm.dropna(subset=['d0'], inplace=True)
    stks_interm['d0'] = pd.to_datetime(stks_interm['d0'])
    stks_interm['period'] = (stks_interm['date_val'] - stks_interm['d0']).dt.days

    # aditional quality flags and uncertainty-related columns: 
    stks_interm['measurement_quality'] = 1 # 1 is for "typical reading uncertainty"
    stks_interm['measurement_type'] = 1 # 1 is for stake
    stks_interm['mb_error'] = np.nan # initialize column - this is filled in a later step in Uncertainties.py
    stks_interm['reading_error'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    stks_interm['density_error'] = np.nan # # initialize column - this is filled in a later step in Uncertainties.py
    stks_interm['date_quality'] = 1 # start date and end date exactly known for fixed date stakes.
    
    # set values for columns that always stay the same:
    if gl == 'VK':
        stks_interm['source'] = 'BS'
    if gl == 'MWK':
        stks_interm['source'] = 'MSW'

    # set time to 12 (same as in the Swiss data)
    stks_interm['time0'] = 1200
    stks_interm['time1'] = 1200

    # format dates to match swiss version
    stks_interm['date0'] = stks_interm['d0'].dt.strftime('%Y%m%d').astype(int)

    stks_interm['date1'] = stks_interm['date_val'].dt.strftime('%Y%m%d').astype(int)

    if tabletype == 'cumul':
        stks_interm = stks_interm[['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality',
                               'x_pos', 'y_pos', 'z_pos', 'position_quality', 'mb_raw_cu', 'density',
                               'density_quality', 'mb_we_cu', 'measurement_quality', 'measurement_type',
                               'mb_error', 'reading_error', 'density_error', 'source']]

    if tabletype == 'period':
        stks_interm = stks_interm[['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality',
                               'x_pos', 'y_pos', 'z_pos', 'position_quality', 'mb_raw', 'density',
                               'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                               'mb_error', 'reading_error', 'density_error', 'source']]

    stks_interm = stks_interm.reset_index(drop=True)
    return (stks_interm)


# make table with intermediate and seasonal/annual data FOR THE SNOW PITS
def makeTablePits(fname, tabletype, season, gl):
    if gl == 'VK':
        when = ['Frühjahresschächte', 'Herbstschächte']
    if gl == 'MWK':
        when = ['Frühjahrsschächte', 'Herbstschächte']

    if season == 'herbst':
        w = when[1]
    if season == 'winter':
        w = when[0]
    
    temp = pd.read_excel(fname, w, header=0)
    basics = pd.DataFrame(columns=['name'])
    basics['name'] = temp['NAME']
    basics['x_pos'] = temp['POINT_X']
    basics['y_pos'] = temp['POINT_Y']
    if gl == 'VK':
        basics['z_pos'] = temp['dgm12']
    if gl == 'MWK':
        basics['z_pos'] = temp['dgm08']
        
    basics['position_quality'] = 2 # 2 stands for measured by handheld GPS - see swiss file
    
    basics['density'] = temp['Dichte [kg/m^3]']
    

    # FIXED DATE SPRING: get mb we value extrapolated to fixed date value for SPRING
    if (tabletype == 'fixed') & (season == 'winter'):
        basics['density_quality'] = 3 # 3 stands for estimated from nearby measured snow density - see swiss file
        
        basics['date0'] = (temp['Jahr'].astype(int)-1).astype(str)+'1001'
        if gl == 'VK':    
            basics['date_val'] = '01.05.' + temp['Jahr'].astype(str)
        if gl == 'MWK':
            basics['date_val'] = '05/01/' + temp['Jahr'].astype(str)

        basics['date_quality'] = 1 # for start and end date exactly known (see swiss docs)
        basics['mb_raw'] = np.nan
        basics['mb_we'] = temp['korrigierter Wasserwert [mm]']

        basics['measurement_quality'] = 5 # 5 is for "reconstructed value (other reason)" - using this to indicate extrapolation to fixed date.


    # FLOATING DATE SPRING: get values as measured
    if (tabletype == 'period') & (season == 'winter'):
        basics['density_quality'] = 2 # 2 stands for measured snow density - see swiss file
        # end date of period is measurement date:
        basics['date_val'] = temp['Datum']
        # start date is estimated as October 1.
        basics['date0'] = (temp['Jahr'].astype(int)-1).astype(str)+'1001'
        # date quality: start date estimated/unknown, end date exactly known
        basics['date_quality'] = 3
        basics['mb_raw'] = temp['Tiefe [m]']*1000 #snow depth, convert to mm
        basics['mb_we'] = basics['mb_raw'] * basics['density']/1000 # convert to mm WE
        # reality check to see if computed value matches value in excel file:
        basics['mb_we_f'] = temp['Wasserwert [mm]'] # read from file to check in matches mb_we

        basics['measurement_quality'] = 1 # 1 is for "typical reading uncertainty"
        if (gl=='VK'): # set to "reconstructed value" for first VK winter season
            basics.loc[basics.date_val.dt.year==2012]['measurement_quality'] = 5

    # FIXED DATE AUTUMN: get mb we value extrapolated to fixed date value for AUTUMN
    if (tabletype == 'fixed') & (season == 'herbst'):
        basics['density_quality'] = 3 # see above
        basics['date0'] = (temp['Jahr'].astype(int)-1).astype(str)+'1001'
        if gl == 'VK':
            basics['date_val'] = '30.09.' + temp['Jahr'].astype(str)
        if gl == 'MWK':
            basics['date_val'] = '09/30/' + temp['Jahr'].astype(str)

        basics['date_quality'] = 1

        basics['mb_raw'] = np.nan
        basics['mb_we'] = temp['korrigierter Wasserwert [mm]']

        # if there is no density value, adjust density quality flag to "estimated from nearby values"
        basics['density_quality'].loc[basics['density'].isnull()] = 3 
 
        if gl == 'VK':
            # VK only: this column in the excel file contains no data values if the snow value is firn & new snow
            # and ablation values or -99999 if the snow value is nothing or only new snow.
            basics['check'] = temp['Eisablation [mm] an den Schachtpositionen']

            # do not use new snow only data as seasonal/annual fixed date point ablation value (if
            # there is a negative value in the check column, set mb_we to nan)
            basics['mb_we'].loc[~basics['check'].isnull()] = np.nan

        # 5 is for "reconstructed value (other reason)" - using this to indicate extrapolation to fixed date
        basics['measurement_quality'] = 5 

        basics.dropna(subset=['mb_we'], inplace=True)


    # FLOATING DATE AUTUMN: get values as measured
    if (tabletype == 'period') & (season == 'herbst'):
        basics['density_quality'] = 2 # 2 stands for measured snow density - see swiss file
        # end date of period is measurement date:
        basics['date_val'] = temp['Datum']

        basics['mb_raw'] = temp['Tiefe [m]']*1000#snow depth, convert to mm
        basics['mb_we'] = basics['mb_raw'] * basics['density']/1000 # convert to mm WE
        # reality check to see if computed value matches value in excel file:
        basics['mb_we_f'] = temp['Wasserwert [mm]'] # read from file to check in matches mb_we

        # THIS MAY NEED ADJUSTMENT! HOW TO DEAL WITH AUTUMN NEW SNOW?
        if gl == 'VK':
            # this column in the excel file contains no data values if the snow value is firn & new snow
            # and ablation values or -99999 if the snow value is nothing or only new snow.
            basics['check'] = temp['Eisablation [mm] an den Schachtpositionen']

            # do not use new snow only data as seasonal/annual fixed date point ablation value (if
            # there is a negative value in the check column, set mb_we to nan)
            #basics['mb_we'].loc[basics['check'] < 0] = np.nan

        # start date unknown
        basics['date0'] = np.nan

        # date quality: start date estimated/unknown, end date exactly known
        basics['date_quality'] = 3

        basics.dropna(subset=['mb_we'], inplace=True)
        basics['measurement_quality'] = 1 # 1 is for "typical reading uncertainty"

    # careful with different date formats
    if gl == 'VK':
        basics['period'] = (pd.to_datetime(basics['date_val'], format='%d.%m.%Y') - pd.to_datetime(basics['date0'], format='%Y%m%d')).dt.days
        # format end date to match Swiss table
        basics['date1'] = pd.to_datetime(basics['date_val'], format='%d.%m.%Y').dt.strftime('%Y%m%d').astype(int)
        # set values for colums that always stay the same:
        # source: who provided the data?
        basics['source'] = 'BS' 
    if gl == 'MWK':
        basics['period'] = (pd.to_datetime(basics['date_val'], format='%m/%d/%Y') - pd.to_datetime(basics['date0'], format='%Y%m%d')).dt.days
        # format end date to match Swiss table
        basics['date1'] = pd.to_datetime(basics['date_val'], format='%m/%d/%Y').dt.strftime('%Y%m%d').astype(int)
        # set values for colums that always stay the same:
        # source: who provided the data?
        basics['source'] = 'MWS' 

    # snow pit mass balance cannot be negative
    basics['mb_we'].loc[basics['mb_we'] < 0] = np.nan

    
    basics['measurement_type'] = 2 # 2 is for snow pit and probing
        
    basics['mb_error'] = np.nan # not sure
    basics['reading_error'] = np.nan # not sure
    basics['density_error'] = np.nan # not sure

    # set time to 12 (same as in the Swiss data)
    basics['time0'] = 1200
    basics['time1'] = 1200

    pitdata = basics[['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality', 'x_pos',
                      'y_pos', 'z_pos', 'position_quality', 'mb_raw', 'density', 'density_quality',
                      'mb_we', 'measurement_quality', 'measurement_type', 'mb_error', 'reading_error',
                      'density_error', 'source']]

    pitdata.dropna(subset=['mb_we'], inplace=True)
    pitdata = pitdata.reset_index(drop=True)

    return(pitdata)


def writetofile(dat, what, gl, forheader, y):
    if what == 'annual':
        header1 = '# Mass Balance; '+forheader+' annual fixed date'
        fn = gl+'/'+gl+'_annual_pits_stakes_fixeddate_'+y+'.csv'
    if what == 'seasonal':
        header1 = '# Mass Balance; '+forheader+' winter fixed date'
        fn = gl+'/'+gl+'_winter_pits_fixeddate_'+y+'.csv'
    if what == 'period':
        header1 = '# Mass Balance; '+forheader+' intermediate'
        fn = gl+'/'+gl+'_intermediate_pits_stakes_'+y+'.csv'
    if what == 'cumul':
        header1 = '# Mass Balance; '+forheader+' intermediate'
        fn = gl+'/'+gl+'_intermediate_stakes_cumul_'+y+'.csv'

    header2 = '# name; date0; time0; date1; time1; period; date_quality; x_pos ; y_pos ; z_pos ; position_quality; mb_raw ; density ;  density_quality ; mb_we ; measurement_quality ; measurement_type ; mb_error ; reading_error ; density_error ; source'
    header3 = '# (-);  (yyyymmdd); (hhmm) ; (yyyymmdd); (hhmm) ; (d) ; (#) ; (m) ; (m) ; (m a.s.l.) ; (#) ; (cm) ; (kg m-3) ; (#) ; (mm w.e.) ; (#) ; (#) ; (mm w.e.) ; (mm w.e.) ; (mm w.e.) ; (-)'
    header4 = '# IGF / OEAW; production-date 20231108 ; reference ; http://www.mountainresearch.at'

    with open(fn, 'a') as file:
        file.write(header1+'\n')
        file.write(header2+'\n')
        file.write(header3+'\n')
        file.write(header4+'\n')
        dat.to_csv(file, header=False, index=False, sep='\t')



# -----------------------------
# Generate the tables:
# -----------------------------
# set file paths:
# make array of years - each year has a sheet in the excel table with the stake data. this will later be used to loop through the sheets.
# -----------
# VK:
yrsVK = np.arange(2012, 2024)
fnameVK = 'VK/Pegeldaten_gesammelt_v5_2023.xlsx'
# manually fixed date format in excel file (if two days, alway used second date)
fpitsVK = 'VK/Schachtdaten-gesammelt_VEK_LH_2023.xlsx'
# -----------
# MWK:
yrsMWK = np.arange(2007, 2024)
fnameMWK = 'MWK/Pegel_v3_LH_2023.xlsx'
# manually fixed date format in excel file (if two days, alway used second date)
fpitsMWK = 'MWK/Schaechte_LH_2023.xlsx'
# -----------

# call functions for both glaciers:
for gl in ['VK', 'MWK']:

    if gl == 'VK':
        fpits = fpitsVK
        yrs = yrsVK
        fn = fnameVK
        forheader = 'Venedigerkees; 10460;'
    if gl == 'MWK':
        fpits = fpitsMWK
        yrs = yrsMWK
        fn = fnameMWK
        forheader = 'Mullwitzkees; 578;'

    pits_fixed_winter = makeTablePits(fpits, 'fixed', 'winter', gl)
    pits_fixed_annual = makeTablePits(fpits, 'fixed', 'herbst', gl)

    pits_int_winter = makeTablePits(fpits, 'period', 'winter', gl)
    pits_int_herbst = makeTablePits(fpits, 'period', 'herbst', gl)

    stks_annual = makeTableAnnual(yrs, fn, gl)

    stks_int = makeTableIntermediate(yrs, fn, 'period', gl)
    # stop
    stks_int_cu = makeTableIntermediate(yrs, fn, 'cumul', gl)


    # concatenate annual stakes and pits:
    data_annual = pd.concat([stks_annual, pits_fixed_annual])

    # concatenate intermediate stakes and pits:
    # add filler value for missing date of fall pits:
    pits_int_herbst['date0'] = 'NAN'
    pits_int_herbst['time0'] = 'NAN'
    pits_int_herbst['period'] = 'NAN'
    # print(pits_int_herbst)
    # stop
    
    data_int = pd.concat([stks_int, pits_int_winter, pits_int_herbst])
    

    # fixed date winter with uncertainties:
    data_winter_u = unc.uncertainties(pits_fixed_winter, 'pits')
    # fixed date annual with uncertainties:
    data_annual_u = unc.uncertainties(data_annual, 'annual')

    # intermediate with uncertainties:
    data_int_u = unc.uncertainties(data_int, 'inter')



    writetofile(data_annual_u, 'annual', gl, forheader, '2023')
    writetofile(data_winter_u, 'seasonal', gl, forheader, '2023')
    writetofile(data_int_u, 'period', gl, forheader, '2023')
    writetofile(stks_int_cu, 'cumul', gl, forheader, '2023')





