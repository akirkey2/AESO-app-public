# -*- coding: utf-8 -*-
"""
Created on Fri May 24 13:52:32 2024

@author: Aaron Kirkey
"""


#%% Environment setup
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime
import glob
import zipfile
# import seaborn as sns
# import scipy as sp
# import sys
# from matplotlib import cm
# import pathlib
# import os
# from sklearn import preprocessing
# import plotly.io as pio
# import plotly.express as px
# from dash import Dash, html, dash_table, dcc, callback, Input, Output
# import dash
# pio.renderers.default='browser'
mpl.rcParams.update(mpl.rcParamsDefault)
plt.rc('axes', axisbelow=True)
mpl.interactive(True)
mpl.rcParams['lines.markersize'] = 5


#%% Dataframe setup
# file_path = 'C:\\Users\\Aaron Kirkey\\Documents\\GitHub\\AESO-data\\CSD Generation (Hourly) - 2024-01.csv'
files = glob.glob('CSD*.zip')

temp_dfs = []

for file in files:
    with zipfile.ZipFile(file, 'r') as zipf:
        for f in zipf.namelist():
            # If it's a CSV file, you can directly load it into a DataFrame
            if f.endswith('.csv'):
                with zipf.open(f) as file_in_zip:
                    # Read the CSV directly into a pandas DataFrame
                    temp = pd.read_csv(file_in_zip, usecols=['Date (MST)', 'Asset Name', 'Volume',
                          'Fuel Type', 'Sub Fuel Type'])
                temp_dfs.append(temp)
raw_data = pd.concat(temp_dfs, ignore_index = True)
#print(raw_data.tail)

df = raw_data.copy()

raw_data = []
temp = []

#%%
#test = df.copy()
#test = test.groupby()

#%% Reducing the df to the date(s) selected by the user in the dash
date = '2024-01-06'


def df_date_restrict(date='2024-01-01'):
    
    dft = df.loc[(df['Date (MST)'].str.contains(date))]
    dfg = dft.groupby(['Date (MST)','Fuel Type'])['Volume'].sum()
    dfg = dfg.reset_index()
    dfg = dfg.sort_values(by=['Date (MST)','Fuel Type'])
    # dftotal = df_date_range.groupby(['Date (MST)']).sum()
    # dftotal.index = pd.to_datetime(dftotal.index)
    return dfg

#%%
dft = df.loc[(df['Date (MST)'].str.contains(date))]
dfg = dft.groupby(['Date (MST)','Fuel Type'])['Volume'].sum()
dfg = dfg.reset_index()
dfg = dfg.sort_values(by=['Fuel Type','Date (MST)'])

#%%
def df_hourly(date='2024-01-05'):
    dft = df_date_restrict(date) #Get the smaller df based on date input by user
    df_temp_2 = pd.DataFrame()
    
    for i in df['Fuel Type'].unique():
        df_temp = dft.loc[(dft['Fuel Type'].str.contains(i))] 
        df_temp = df_temp.groupby(['Date (MST)'])[['Date (MST)','Volume']].sum()
        df_temp_2[i] = df_temp["Volume"]
        df_temp.index = pd.to_datetime(df_temp.index)
    df_temp_2 = df_temp_2.reset_index()
    df_temp_2 = df_temp_2.round(decimals = 0)
    df_temp_2['TOTAL'] = df_temp_2[['OTHER', 'WIND', 'GAS', 'HYDRO', 'SOLAR',
           'ENERGY STORAGE', 'COAL', 'DUAL FUEL']].sum(axis=1)
    df_temp_2 = df_temp_2[['Date (MST)','COAL','GAS','DUAL FUEL','HYDRO',
                           'SOLAR','WIND','ENERGY STORAGE','OTHER','TOTAL']]
    df_temp_2['NET'] = df_temp_2['TOTAL'] - (df_temp_2[['SOLAR','WIND','HYDRO']].sum(axis=1))
    df_temp_2['FF'] = df_temp_2[['OTHER', 'GAS','COAL', 'DUAL FUEL']].sum(axis=1)
    df_temp_2['RE'] = df_temp_2[['SOLAR','WIND','HYDRO']].sum(axis=1)
    return df_temp_2
    
#%% Make the columns that represent the percent contribution to total!!!
def df_percent(date='2024-01-05'): 
    
    dft = df_hourly(date) #Get the hourly volume dataframe
    
    df1p = pd.DataFrame()
    df1p['Date (MST)'] = dft['Date (MST)']
    
    for i in dft.columns[1:9]:
        df1p[f'{i}'] = (dft[f'{i}'] / dft['TOTAL'])*100
    df1p['TOTAL'] = df1p[['OTHER', 'WIND', 'GAS', 'HYDRO', 'SOLAR',
           'ENERGY STORAGE', 'COAL', 'DUAL FUEL']].sum(axis=1)
    df1p['RENEWABLE'] = df1p[['WIND','HYDRO','SOLAR','ENERGY STORAGE']].sum(axis=1)
    df1p['FOSSIL FUEL'] = df1p[['COAL','GAS','DUAL FUEL']].sum(axis=1)
    df1p = df1p.round(decimals = 1)
    return df1p
#%%
date = '2024-01-07'
start_date = pd.to_datetime(date).date() #Format: %Y/%m/%d
end_date = pd.to_datetime(date).date() + pd.Timedelta(days=7)

#%%
def price_ei_vol_day(date='2024-01-06'):
    start_time = datetime.now()
    dft = df.copy()
    # dft = dft[['Date (MST)', 'Asset Short Name', 'Volume',
    #    'Fuel Type', 'Sub Fuel Type']]
    dft['Date (MST)'] = pd.to_datetime(df['Date (MST)'],format='%Y-%m-%d %H:%M:%S')
    
    
    # Restricting df to desired dates, in app this value comes from the callback

    start_date = pd.to_datetime(date).date() #Format: %Y/%m/%d
    end_date = pd.to_datetime(date).date() #+ pd.Timedelta(days=7) #Same format

    # You have to use dt.date for series and .date() for individual strings 
    dft = dft.loc[(dft['Date (MST)'].dt.date >= start_date) & (dft['Date (MST)'].dt.date<= end_date)]
    dfg = dft.groupby(['Date (MST)','Fuel Type'])['Volume'].sum()
    dfg = dfg.reset_index()
    dfg = dfg.sort_values(by=['Date (MST)','Fuel Type'])

#Emission factor calculations from: https://www.nrel.gov/docs/fy21osti/80580.pdf
# Values in gCO2e/kWh, conversion explained in next cell.

#This method is used in favour of the cell above because it's more succinct and faster computationally

    """"Volumes from AESO are in MW and emission factors (above) are in 
    gCO2e/kWh. This means we have to multiply values by 1x10^3 but divide by 1x10^6
    to get tonsCO2e. This means dividing all values by 1x10^3"""

    dft['Emissions'] = np.nan

    emission_factors={'Wood/Refuse':52,'WIND':13, 'SIMPLE_CYCLE':486,'COGENERATION':486,
                  'HYDRO':24,'SOLAR':43,'Gas':486,'GAS_FIRED_STEAM':486, 'COMBINED_CYCLE':486,
                  'Gas cogen':486,'Biomass':52, 'ENERGY STORAGE':33, 'COAL':1001,
                  'DUAL FUEL':743.5, 'Oil/Gas':633,'Dual Fuel':743.5}
#The .map function simply fills out the 'Emissions' column based on 
# k,v pairs in 'emission_factors' + a little extra math I tacked on.
    dft['Emissions'] = dft['Sub Fuel Type'].map(emission_factors) * dft['Volume'] / 1000
    
    
    diff = datetime.now() - start_time
    print(f'After mapping: {diff}')
    
    df_temp = dft.copy()
    df_hourly_vol = pd.DataFrame()

    #Selecting rows of df that match each Fuel Type and then summing their volume and ghgs
    for i in dft['Fuel Type'].unique():
        #print(i) #for debugging
        df_temp = dft.loc[(dft['Fuel Type'] == i)]
        df_hourly_vol[i]= df_temp.groupby('Date (MST)')['Volume'].sum()
        df_hourly_vol[f'{i}_ghg'] = df_temp.groupby('Date (MST)')['Emissions'].sum()
    df_hourly_vol = df_hourly_vol.reset_index()
    
    #making total volume column
    fuel_types = [i for i in dft['Fuel Type'].unique()]
    df_hourly_vol['Total Load'] = df_hourly_vol[fuel_types].sum(axis=1)
    #making hourly total ghg column
    ghg_types  = [x for x in df_hourly_vol.columns if 'ghg' in x]
    df_hourly_vol['Total_ghg'] = df_hourly_vol[ghg_types].sum(axis=1)
    
    #Calculating Emission Intensity (ie gCO2e/kWh)
    df_hourly_vol['EI'] = (df_hourly_vol['Total_ghg'] / df_hourly_vol['Total Load']) * 1000
    #Making columns for renewable volume and FF volume
    df_hourly_vol['Renewable Gen'] = df_hourly_vol.filter(items=['WIND','SOLAR','HYDRO']).sum(axis=1)
    df_hourly_vol['Fossil Fuel Gen'] = df_hourly_vol.filter(items=['OTHER','GAS','COAL','DUAL FUEL']).sum(axis=1)
    df_hourly_vol['Net Load'] = df_hourly_vol['Total Load'] - (df_hourly_vol['Renewable Gen'])
    
    
    diff = datetime.now() - start_time
    print(f'After EI math: {diff}')
    
    
    # Getting price data
    file = 'P&A Table_data.csv'
    
    price_data=pd.read_csv(file)
    
    df_price = price_data
    df_price = df_price.set_index('Date - MST')
    df_price2 = df_price.pivot(columns='Measure Names',values='Measure Values')
    df_price2 = df_price2.reset_index()
    df_price2 = df_price2.rename(columns = {'Date - MST': 'Date (MST)'})
    df_price2['Date (MST)'] = pd.to_datetime(df_price2['Date (MST)'],format='%m/%d/%Y %I:%M:%S %p')
    df_price2 = df_price2.reset_index(drop=True)
    df_price2 = df_price2[['Date (MST)','Avg. Price']]
    df_price2 = df_price2.loc[(df_price2['Date (MST)'].dt.date >= start_date) & (df_price2['Date (MST)'].dt.date<= end_date)]
    
    #Merging Generation hourly dataset with the price dataset
    
    df_hourly_vol = pd.merge(df_hourly_vol,df_price2,how='left',on='Date (MST)')
    df_hourly_vol['RE_percent'] = ((df_hourly_vol['Renewable Gen'] / df_hourly_vol['Total Load']) *100).round(decimals = 1)


    diff = datetime.now() - start_time
    print(f'After price math: {diff}')
    return dfg, df_hourly_vol
#%%
def price_ei_vol_week(start_date='2024-01-02',end_date=start_date):
    start_time = datetime.now()
    dft = df.copy()
    diff = datetime.now() - start_time
    print(f'Copying df: {diff}')
    dft['Date (MST)'] = pd.to_datetime(df['Date (MST)'],format='%Y-%m-%d %H:%M:%S')
    
    
    # Restricting df to desired dates, in app this value comes from the callback

    start_date = pd.to_datetime(start_date).date() #Format: %Y/%m/%d
    end_date = pd.to_datetime(end_date).date()  #Same format

    # You have to use dt.date for series and .date() for individual strings 
    dft = dft.loc[(dft['Date (MST)'].dt.date >= start_date) & (dft['Date (MST)'].dt.date<= end_date)]

    dfg = dft.groupby(['Date (MST)','Fuel Type'])['Volume'].sum()
    dfg = dfg.reset_index()
    
    diff = datetime.now() - start_time
    print(f'Filtering df & making dfg: {diff}')
    
#Emission factor calculations from: https://www.nrel.gov/docs/fy21osti/80580.pdf
# Values in gCO2e/kWh, conversion explained in next cell.

#This method is used in favour of the cell above because it's more succinct and faster computationally

    """"Volumes from AESO are in MW and emission factors (above) are in 
    gCO2e/kWh. This means we have to multiply values by 1x10^3 but divide by 1x10^6
    to get tonsCO2e. This means dividing all values by 1x10^3"""

    dft['Emissions'] = np.nan

    emission_factors={'Wood/Refuse':52,'WIND':13, 'SIMPLE_CYCLE':486,'COGENERATION':486,
                  'HYDRO':24,'SOLAR':43,'Gas':486,'GAS_FIRED_STEAM':486, 'COMBINED_CYCLE':486,
                  'Gas cogen':486,'Biomass':52, 'ENERGY STORAGE':33, 'COAL':1001,
                  'DUAL FUEL':743.5, 'Oil/Gas':633,'Dual Fuel':743.5}
#The .map function simply fills out the 'Emissions' column based on 
# k,v pairs in 'emission_factors' + a little extra math I tacked on.
    diff = datetime.now() - start_time
    print(f'After mapping: {diff}')

    dft['Emissions'] = dft['Sub Fuel Type'].map(emission_factors) * dft['Volume'] / 1000

    df_temp = dft.copy()
    df_hourly_vol = pd.DataFrame()

    #Selecting rows of df that match each Fuel Type and then summing their volume and ghgs
    for i in dft['Fuel Type'].unique():
        df_temp = dft.loc[(dft['Fuel Type'] == i)]
        df_hourly_vol[i]= df_temp.groupby('Date (MST)')['Volume'].sum()
        df_hourly_vol[f'{i}_ghg'] = df_temp.groupby('Date (MST)')['Emissions'].sum()
    df_hourly_vol = df_hourly_vol.reset_index()
    
    #making total volume column
    fuel_types = [i for i in dft['Fuel Type'].unique()]
    df_hourly_vol['Total Load'] = df_hourly_vol[fuel_types].sum(axis=1)
    #making hourly total ghg column
    ghg_types  = [x for x in df_hourly_vol.columns if 'ghg' in x]
    df_hourly_vol['Total_ghg'] = df_hourly_vol[ghg_types].sum(axis=1)
    
    #Calculating Emission Intensity (ie gCO2e/kWh)
    df_hourly_vol['EI'] = (df_hourly_vol['Total_ghg'] / df_hourly_vol['Total Load']) * 1000
    #Making columns for renewable volume and FF volume
    df_hourly_vol['Renewable Gen'] = df_hourly_vol.filter(items=['WIND','SOLAR','HYDRO']).sum(axis=1)
    df_hourly_vol['Fossil Fuel Gen'] = df_hourly_vol.filter(items=['OTHER','GAS','COAL','DUAL FUEL']).sum(axis=1)
    df_hourly_vol['Net Load'] = df_hourly_vol['Total Load'] - (df_hourly_vol['Renewable Gen'])
    
    diff = datetime.now() - start_time
    print(f'After EI math: {diff}')
    # Getting price data
    file = 'P&A Table_data.csv'
    
    price_data=pd.read_csv(file)
    
    df_price = price_data
    df_price = df_price.set_index('Date - MST')
    df_price2 = df_price.pivot(columns='Measure Names',values='Measure Values')
    df_price2 = df_price2.reset_index()
    df_price2 = df_price2.rename(columns = {'Date - MST': 'Date (MST)'})
    df_price2['Date (MST)'] = pd.to_datetime(df_price2['Date (MST)'],format='%m/%d/%Y %I:%M:%S %p')
    df_price2 = df_price2.reset_index(drop=True)
    df_price2 = df_price2[['Date (MST)','Avg. Price']]
    df_price2 = df_price2.loc[(df_price2['Date (MST)'].dt.date >= start_date) & (df_price2['Date (MST)'].dt.date<= end_date)]
    
    #Merging Generation hourly dataset with the price dataset
    
    df_hourly_vol = pd.merge(df_hourly_vol,df_price2,how='left',on='Date (MST)')
    df_hourly_vol['RE_percent'] = ((df_hourly_vol['Renewable Gen'] / df_hourly_vol['Total Load']) *100).round(decimals = 1)
    diff = datetime.now() - start_time
    print(f'After incorporating price data: {diff}')
    
    return df_hourly_vol, dfg

