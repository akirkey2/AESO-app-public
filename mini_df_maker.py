#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:05:05 2025

@author: aaronkirkey
"""

#%% Environment setup
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import zipfile
import gc


#%% For making temp_master.csv that contains the temp/wind/dew point data from Calgary 2023-2024 
import pandas as pd
import glob
df_list = []
folder = glob.glob('assets/temp_data/*.csv')
for f in folder:
    temp = pd.read_csv(f, usecols=['Date/Time (LST)','Temp (°C)',
                                   'Hmdx','Dew Point Temp (°C)','Wind Spd (km/h)'])
    df_list.append(temp)
df = pd.concat(df_list)

df['Date/Time (LST)'] = pd.to_datetime(df['Date/Time (LST)'],format='%Y-%m-%d %H:%M')
df = df.sort_values(['Date/Time (LST)'])
df = df.rename(columns={"Date/Time (LST)": "Date (MST)"}) 
df.to_csv('assets/temp_master.csv',index=False)

#%% Generation data master dataset
# file_path = 'C:\\Users\\Aaron Kirkey\\Documents\\GitHub\\AESO-data\\CSD Generation (Hourly) - 2024-01.csv'
files = glob.glob('assets/gen_data/CSD*.zip')

chunk_size = 10000
df_list = []

for file in files:
    with zipfile.ZipFile(file, 'r') as zipf:
        for f in zipf.namelist():
            # If it's a CSV file, you can load it  directly into a DataFrame
            if f.endswith('.csv'):
                with zipf.open(f) as file_in_zip:
                    # Read the CSV directly into a pandas DataFrame
                    for chunk in pd.read_csv(file_in_zip, usecols=['Date (MST)', 'Asset Name', 'Volume',
                          'Fuel Type', 'Sub Fuel Type'],chunksize = chunk_size):
                        df_list.append(chunk)
                
df = pd.concat(df_list, ignore_index = True)

del df_list
gc.collect()
df_hourly_vol = []
start_date = '2024-01-01'
date = '2024-01-02'

#%% Prepping dataframe

def df_math():
    print("Function df_math() called")
    global df_hourly_vol
    # global dfg
    start_time = datetime.now()
    diff = datetime.now() - start_time
    print(f'Copying df: {diff}')
    df['Date (MST)'] = pd.to_datetime(df['Date (MST)'],format='%Y-%m-%d %H:%M:%S')
    
    

    # dfg = (
        # dft
        # .groupby(['Date (MST)','Fuel Type'])['Volume'].sum()
        # .reset_index()
        # )
    
    # diff = datetime.now() - start_time
    # print(f'After dfg: {diff}')
    
#Emission factor calculations from: https://www.nrel.gov/docs/fy21osti/80580.pdf
# Values in gCO2e/kWh, conversion explained in next cell.

#This method is used in favour of the cell above because it's more succinct and faster computationally

    """"Volumes from AESO are in MW and emission factors (above) are in 
    gCO2e/kWh. This means we have to multiply values by 1x10^3 but divide by 1x10^6
    to get tonsCO2e/MWh. This means dividing all values by 1x10^3"""

    df['Emissions'] = np.nan

    emission_factors={'Wood/Refuse':52,'WIND':13, 'SIMPLE_CYCLE':486,'COGENERATION':486,
                  'HYDRO':24,'SOLAR':43,'Gas':486,'GAS_FIRED_STEAM':486, 'COMBINED_CYCLE':486,
                  'Gas cogen':486,'Biomass':52, 'ENERGY STORAGE':33, 'COAL':1001,
                  'DUAL FUEL':743.5, 'Oil/Gas':633,'Dual Fuel':743.5}
#The .map function simply fills out the 'Emissions' column based on 
# k,v pairs in 'emission_factors' + a little extra math I tacked on.
    diff = datetime.now() - start_time
    print(f'After mapping: {diff}')

    df['Emissions'] = df['Sub Fuel Type'].map(emission_factors) * df['Volume'] / 1000

    df_temp = df.copy()
    df_hourly_vol = pd.DataFrame()

    #Selecting rows of df that match each Fuel Type and then summing their volume and ghgs
    fuel_types = [i for i in df['Fuel Type'].unique()]
    for i in fuel_types:
        df_temp = df.loc[(df['Fuel Type'] == i)]
        df_hourly_vol[i]= df_temp.groupby('Date (MST)')['Volume'].sum()
        df_hourly_vol[f'{i}_ghg'] = df_temp.groupby('Date (MST)')['Emissions'].sum()
    df_hourly_vol = df_hourly_vol.reset_index()
    
    
    #Time check
    diff = datetime.now() - start_time
    print(f'After init df_hourly_vol + populating with ghgs: {diff}')
    
    
    #making total volume column
    fuel_types = [i for i in df['Fuel Type'].unique()]
    df_hourly_vol['Total Generation'] = df_hourly_vol[fuel_types].sum(axis=1)
    #making hourly total ghg column
    ghg_types  = [x for x in df_hourly_vol.columns if 'ghg' in x]
    df_hourly_vol['Total_ghg'] = df_hourly_vol[ghg_types].sum(axis=1)
    
    #Calculating Emission Intensity (ie gCO2e/kWh)
    df_hourly_vol['EI'] = (df_hourly_vol['Total_ghg'] / df_hourly_vol['Total Generation']) * 1000
    #Making columns for renewable volume and FF volume
    df_hourly_vol['Renewable Gen'] = df_hourly_vol.filter(items=['WIND','SOLAR','HYDRO']).sum(axis=1)
    df_hourly_vol['Fossil Fuel Gen'] = df_hourly_vol.filter(items=['OTHER','GAS','COAL','DUAL FUEL']).sum(axis=1)
    df_hourly_vol['Net Generation'] = df_hourly_vol['Total Generation'] - (df_hourly_vol['Renewable Gen'])
    
    
    #Time check
    diff = datetime.now() - start_time
    print(f'After EI math : {diff}')
    
    
    # Getting price data
    file = 'assets/price_data/P&A Table_Full Data_data.csv' 
    df_price = pd.read_csv(file)
    df_price = df_price.rename(columns={'Date - MST':'Date (MST)','AIL':'Total Load'})
    df_price['Date (MST)'] = pd.to_datetime(df_price['Date (MST)'], format ='%m/%d/%Y %I:%M:%S %p')
    df_price = (
                df_price
                .sort_values(by=['Date (MST)'])
                .reset_index(drop=True)[['Date (MST)','Price','Total Load']]
                )
    #Merging Generation hourly dataset with the price dataset
    df_hourly_vol = pd.merge(df_hourly_vol,df_price,how='left',on='Date (MST)')
    df_hourly_vol['RE_percent'] = ((df_hourly_vol['Renewable Gen'] / df_hourly_vol['Total Generation']) *100).round(decimals = 1)
    print(df_hourly_vol.head())
    
    #Incorporating temp data (pincher creek for temp and windspeed)
    temp_master = pd.read_csv('assets/temp_master.csv')
    temp_master['Date (MST)'] = pd.to_datetime(temp_master['Date (MST)'], format ='%Y-%m-%d %H:%M:%S')
    # temp_master = temp_master.loc[temp_master['Date (MST)'].dt.date >= pd.to_datetime('2024-01-01').date()]
    df_hourly_vol = pd.merge(df_hourly_vol,temp_master,how='left',on='Date (MST)')
    
    
    #Time check
    diff = datetime.now() - start_time
    print(f'After incorporating price data: {diff}')
    df_hourly_vol = df_hourly_vol.rename(columns={
    'OTHER': 'Other',
    'OTHER_ghg': 'Other_ghg',
    'WIND': 'Wind',
    'WIND_ghg': 'Wind_ghg',
    'GAS': 'Gas',
    'GAS_ghg': 'Gas_ghg',
    'HYDRO': 'Hydro',
    'HYDRO_ghg': 'Hydro_ghg',
    'SOLAR': 'Solar',
    'SOLAR_ghg': 'Solar_ghg',
    'ENERGY STORAGE': 'Energy Storage',
    'ENERGY STORAGE_ghg': 'Energy Storage_ghg',
    'COAL': 'Coal',
    'COAL_ghg': 'Coal_ghg',
    'DUAL FUEL': 'Dual Fuel',
    'DUAL FUEL_ghg': 'Dual Fuel_ghg'
    })
    
    return df_hourly_vol

d = df_math()


#%% df date_restrict
start_date='2024-01-01'
date = '2024-12-31'
def date_restrict(start_date='2024-01-01',end_date='2024-12-31'):
    print('Function date_restrict() called')
    # Restricting df to desired dates, in app this value comes from the callback
        
    start_date = pd.to_datetime(start_date).date() #Format: %Y/%m/%d
    end_date = pd.to_datetime(end_date).date()  #Same format

    # You have to use .dt.date for series and .date() for individual strings
    df_hourly = df_hourly_vol.loc[(df_hourly_vol['Date (MST)'].dt.date >= start_date) 
                                  & (df_hourly_vol['Date (MST)'].dt.date <= end_date)]
    
    #df_stacked = dfg.loc[(dfg['Date (MST)'].dt.date >= start_date) 
    #                    & (dfg['Date (MST)'].dt.date <= end_date)]
    
    return  df_hourly

#%% Cell for running fxns
data = date_restrict()

#%% For 2024 mini_df
f_name = 'mini_df.csv'
date_restrict().to_csv(f'assets/{f_name}',index=False)
print(f'Exporting of: {f_name} successful')

#%% Total mini_df
# f_name = '232425_mini_df.csv'
# df_math().to_csv(f'assets/{f_name}',index=False)
# print(f'Exporting of: {f_name} successful')
