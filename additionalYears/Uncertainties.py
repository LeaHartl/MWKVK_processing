import numpy as np
import pandas as pd



# supress copy warning - careful 
pd.options.mode.chained_assignment = None  # default='warn'

# script to apply uncertainties based on quality flages, following the approach of GLAMOS and Geibel et al

# df to be passed to this function needs to have flags set for date quality, measurement quality,
# measurement type, density quality. Position uncertainty is ignored in error calculation as per GLAMOS approach.
def uncertainties(df, datatype):
    # set up dictionaries of quality flags and associated uncertainty values as given in GLAMOS readme document
    # these "quality types" contribute to the reading error: date quality, measurement type, measurement quality
    # date quality
    # date quality (need to figure out how to deal with this for winter data): 
    q_date = {0: np.nan,# start and end dates estimated/unknown14; 2500-3000m: 31cm; 3000-3500m: 22cm
              1: 0, # start and end dates exactly known
              2: np.nan, # start date exactly known, end date estimated/unknown 14; (based on elevation):
              3: np.nan, # start date estimated/unknown, end date exactly known 14; 1500-2500 m: 36 cm 
              # 4: np.nan# fixed date (dates known but values extrapolated)
              }

    # density quality
    q_density = {0: 10,# quality/source unknown 10%
                 1: 2, # Ice density, uncertainty 2%
                 2: 5, # Measured snow/firn/ice density, uncertainty 5%
                 3: 8, # Density of snow/firn estimated from nearby measurements, uncertainty 8%
                 4: 10, # Density of snow/firn estimated without nearby measurements 
                 5: 10, # water equivalent based on combination of fresh snow density and ice density
                        # GLAMOS: raw balance error:min 5 cm, max 15 cm, 10 % otherwise
                        # we don't have raw balance for most of the fixed date values. Suggestion: Always 10%
                }
                 

    # measurement type: our data set contains only only stakes, pits and probing
    q_mtype = {0: 10,# unknown
               1: 5,# stake
               2: 10,# snowpit / coring /
               3: 15, # depth probing  --> separate category! different from GLAMOS!
               # 3: 5,
               # 4: 5, # GPR, check Geibel et al 2022 for details, should be 5% of snow depth. not relevant for our case.
               # 5: 150,# in Geibel et al fehlt nummer 5, Reihenfolge is 467. 5 steht für Snow line
               # 6: 1.5
               }

    # measurement quality
    q_mqual = {0: 30, # quality/source unknown, additional quality error contributing to uncertainty: 30cm.
               1: 0, # typical reading uncertainty 
               2: 20, # high reading uncertainty 
               3: 30, # reconstructed value/exceeds minimum measurement range (e.g. stake completely melted-out)
               4: 30, # reconstructed value/exceeds maximum measurement range (e.g. stake buried by snow) 
               5: 30, # reconstructed value (other reason)
               }

    # uncertainties from measurement quality and type: map quality column to respective dictionaries
    df['mqual_unc'] = df['measurement_quality'].map(q_mqual) *10
    df['mtype_unc'] = df['measurement_type'].map(q_mtype)

    # date uncertainty depends on elevation of measurement point. Same values as GLAMOS 
    # create date uncertainty column and map it to date quality dictionary (this covers the standard
    # case of both dates known)
    df['date_unc'] = df['date_quality'].map(q_date)
    # if quality flag is 3 (start date unknown - relevant for winter data)
    # AND location is below 2500m, uncertainty = 36cm
    df['date_unc'].loc[(df['date_quality'].astype(int) == 3) & (df['z_pos'].astype(float) < 2500)] = 360
    # if quality flag is 3 AND location is between 2500 and 3000, uncertainty = 31cm
    df['date_unc'].loc[(df['date_quality'] == 3) & (df['z_pos'] >= 2500) & (df['z_pos'] < 3000)] = 310
    # if quality flag is 3 AND location is between 3000 and 3500, uncerrtainty = 22cm
    df['date_unc'].loc[(df['date_quality'] == 3) & (df['z_pos'] >= 3000) & (df['z_pos'] < 3500)] = 220

    # combine the various uncertainties to make reading error:
    # reading error = squ(date error^2 + measurement type error^2 + meas. quality error^2)
    df['reading_error'] = np.sqrt(df['date_unc']**2 + df['mtype_unc']**2
                                  + df['mqual_unc']**2)# * df['density_error']**2)

    # density uncertainty and error (...):
    # percentage uncertainty, map quality columb to density dictionary:
    df['density_unc'] = df['density_quality'].map(q_density)  
    # convert to mm we:
    df['density_error'] = ((df['density_unc']/100) * df['mb_we']).abs()

    # mass balance error: reading error plus density error:
    # mb error = squ(reading error^2 + density error^2) CHECK ABOUT THIS - does reading error need to be squared again?
    df['mb_error'] = np.sqrt(df['reading_error']**2 + df['density_error']**2)

    df['mb_raw'] = df['mb_raw'].round(1)
    df['mb_we'] = df['mb_we'].round(1)
    df['mb_error'] = df['mb_error'].round(1)
    df['reading_error'] = df['reading_error'].round(1)
    df['density_error'] = df['density_error'].round(1)
    df['density_unc'] = df['density_unc'].round(1)

    # optional print as reality check
    # print(df[['name', 'mb_we', 'date_unc', 'measurement_quality', 'mtype_unc', 'measurement_type' ,'mb_error', 'reading_error','density_error']])
    # print(df[['mb_error', 'reading_error']].mean())



    if datatype == 'probe':
        # put columns in the correct order
        colnames = ['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality', 'x_pos', 'y_pos', 'z_pos',
                'position_quality', 'mb_raw', 'density', 'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                'mb_error', 'reading_error', 'density_error', 'source', 'probe_flag']

    else:
        # put columns in the correct order
        colnames = ['name', 'date0', 'time0', 'date1', 'time1', 'period', 'date_quality', 'x_pos', 'y_pos', 'z_pos',
                'position_quality', 'mb_raw', 'density', 'density_quality', 'mb_we', 'measurement_quality', 'measurement_type',
                'mb_error', 'reading_error', 'density_error', 'source']

    df = df.reindex(columns=colnames)

    return(df)

