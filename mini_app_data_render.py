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
import seaborn as sns
import sys
import plotly.express as px

mpl.rcParams.update(mpl.rcParamsDefault)
plt.rc('axes', axisbelow=True)
mpl.interactive(True)
mpl.rcParams['lines.markersize'] = 5


#%% Dataframe setup

df_hourly_vol = pd.read_csv('assets/mini_df.csv')
df_hourly_vol['Date (MST)'] = pd.to_datetime(df_hourly_vol['Date (MST)'], format ='%Y-%m-%d %H:%M:%S')

#%%
start_date='2024-01-01'
date = '2024-01-02'
def date_restrict(start_date='2024-01-01',end_date=start_date):
    print('Function date_restrict() called')
    # Restricting df to desired dates, in app this value comes from the callback
        
    start_date = pd.to_datetime(start_date).date() #Format: %Y-%m-%d
    end_date = pd.to_datetime(end_date).date()  #Same format

    # You have to use .dt.date for series and .date() for individual strings
    df_hourly = df_hourly_vol.loc[(df_hourly_vol['Date (MST)'].dt.date >= start_date) 
                                  & (df_hourly_vol['Date (MST)'].dt.date <= end_date)]
    
    #df_stacked = dfg.loc[(dfg['Date (MST)'].dt.date >= start_date) 
    #                    & (dfg['Date (MST)'].dt.date <= end_date)]
    
    return  df_hourly

#%% Cell for running fxns

