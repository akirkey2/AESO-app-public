#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:38:59 2024

@author: aaronkirkey
"""

#%% Environment setup
import pandas as pd
import numpy as np
import matplotlib as mpl 
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
import glob
import sys
from matplotlib import cm
import pathlib
import os
from sklearn import preprocessing
import plotly.io as pio
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Input, Output
import dash
import dash_bootstrap_components as dbc
import app_data_new
import datetime as dt
from datetime import date
from datetime import datetime
import gunicorn


#%%  Dash stuff
# datte = '2024-01-06' # Placeholder value

# Define a global template with a centered title
pio.templates["custom_template"] = pio.templates["plotly_white"]
pio.templates["custom_template"]["layout"]["title"] = {
    "x": 0.5,  # Centers the title
    "xanchor": "center"
}

color_map = {
    'SOLAR': '#FDB813',  # Yellow
    'HYDRO': '#1F77B4',  # Blue
    'WIND': '#2CA02C',  # Green
    'GAS': '#9E8653',  # Brown
    'COAL': '#000000',  # Black
    'DUAL FUEL':'#936400', #Dark Grey
    'OTHER':'#93C1A8', #Pale green
    'ENERGY STORAGE':'#C24141', #Red
}


# Set this template as the default
pio.templates.default = "custom_template"

app = Dash(__name__)
server = app.server
app = Dash(external_stylesheets=[dbc.themes.SANDSTONE])
app.title = 'AESO Energy Dash'
app.layout = html.Div(style={'backgroundColor':'#818894'},
                      children=[
    html.Div([html.H1(children='AESO Energy Dash', style={'textAlign': 'center', 'fontSize': 48,'color':'white'}),
              html.Br(),
              html.Div(children="""*Disclaimer: This web-dash and contents are in no way 
             affiliated with the AESO and serves only as a personal project to 
             improve my data science and data viz skillset with respect to grid
             data. For questions, comments or improvement ideas, please contact
             me at: akirkey2@gmail.com with the subject line 'AESO dash project'.
             Thank you for your interest!""", style={'color':'white'})]),
    html.Br(),

    html.Div([

        dcc.Tabs([
            dcc.Tab(children=[
                 html.Br(),
                 dbc.Container(
                        dbc.Row([
                            dbc.Col(
                                dbc.Label('Choose date:', style={'color':'white','fontSize': 17,'color':'white'}),
                                width=12  # Takes up the full row width
                            ),
                            dbc.Col(
                                dcc.DatePickerSingle(  # Drop-down calendar
                                    id='date-picker-single',
                                    min_date_allowed=date(2024, 1, 1),
                                    max_date_allowed=date(2024, 12, 31),
                                    initial_visible_month=date(2024, 1, 1),
                                    date=date(2024, 1, 1),
                                    display_format='Y-M-D'
                                ),
                                width=12  # Takes up the full row width below the label
                            )
                        ])
                    ,fluid=True),
                 # Visual feedback on page displaying date
                 #html.Div(children='Date chosen: (for debugging)*',
                 #         style={'fontSize': 20}),
                # dcc.Markdown(id='date_display', children=''),
                 # html.Div(children ='Hourly Data',style={'fontSize': 32,'font-weight':'bold','textAlign':'center'}),
                 html.Br(),            
                 
                 # This Div is a graph with title, left adjusted beside the following Div
                 dbc.Container(
                            dbc.Row([
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody([dcc.Graph(id='asset_gen')], className="p-0"),
                                        className="shadow-sm m-2"
                                    ),
                                    width=8  # Takes up 8/12 of the row (70% equivalent)
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody([dcc.Graph(id='gen_pie_daily')], className='p-0'),
                                        className="shadow-sm m-2"
                                    ),
                                    width=4  # Takes up 4/12 of the row (30% equivalent)
                                )
                            ])
                        ,fluid=True),

                dbc.Container(
                           dbc.Row([
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([dcc.Graph(id='clean_fossil_gen')], className="p-0"),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6
                               ),
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([dcc.Graph(id='gen_price')], className='p-0'),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6
                               )
                           ])
                       ,fluid=True),


                dbc.Container(
                           dbc.Row([
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([dcc.Graph(id='storage_volume')], className="p-0"),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6
                               ),
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([dcc.Graph(id='EI_graph')], className='p-0'),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6
                               )
                           ])
                       ,fluid=True),
                html.Br(),
                 ],
                label='Single Day'),
            dcc.Tab(children=[
                html.Br(),
                html.Div(children='Chose date range:',
                         style={'fontSize': 17}),
                html.Div(
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date(2024, 1, 1),
                        max_date_allowed=date(2024, 12, 31),
                        initial_visible_month=date(2024, 1, 1),  # Default month
                        start_date=date(2024, 1, 1),
                        end_date=date(2024, 1, 4)
                    )
                ),
                html.Div(id="date-picker-container"),  # Placeholder for dynamic updates
                html.Br(),
                # Visual feedback on page displaying date
                #html.Div(children='Dates chosen: (for debugging)*',
               #          style={'fontSize': 20}),
                #dcc.Markdown(id='date_range_display', children=''),
                #html.Br(),
                 dbc.Container(
                            dbc.Row([
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody([dcc.Graph(id='asset_gen_multi')], className="p-0"),
                                        className="shadow-sm m-2"
                                    ),
                                    width=8  # Takes up 8/12 of the row (70% equivalent)
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody([dcc.Graph(id='gen_pie_multi')], className='p-0'),
                                        className="shadow-sm m-2"
                                    ),
                                    width=4  # Takes up 4/12 of the row (30% equivalent)
                                )
                            ])
                        ,fluid=True),

            ], label='Multi-Day'),
        dcc.Tab(children=[
                html.Br(),
                
                
                
                
                
                
                
                ], label='Stats & Analysis'),
        ]),  # Closing dcc.Tabs
        html.Br(),
    ]),
])  # this closes out the app layout


# Callback for the daily tab
@callback(
    #Output(component_id='date_display', component_property='children'),
    #Output('summary_table', component_property='data'),
    #Output('percent_table', 'data'),
    Output('asset_gen', 'figure'),
    Output('clean_fossil_gen', 'figure'),
    Output('gen_price', 'figure'),
    Output('storage_volume', 'figure'),
    Output('EI_graph', 'figure'),
    Output('gen_pie_daily', 'figure'),
    Output('date-picker-single','initial_visible_month'),

    Input(component_id='date-picker-single', component_property='date'))
# Calls functions with updated date to make dash reactive to selected date
def update_daily(date='2024-01-01'):
    # The function argument comes from the component property of the Input
    print(date)
    date = date
    tester = app_data_new.date_restrict_daily(date)
    #df_daily = app_data_new.price_ei_vol_day(user_selected)
    #summary_data = app_data_new.df_hourly(user_selected).to_dict('records')
    #percent_data = app_data_new.df_percent(user_selected).to_dict('records')
    asset_gen_fig = px.area(tester[0], x='Date (MST)', y="Volume", color="Fuel Type", color_discrete_map=color_map, 
                            title='Hourly generation on AESO by asset & fuel type', labels={
                            "y": "Generation Volume MWh"})
    asset_gen_fig.update_layout(yaxis_title='Generation Volume (MW)',
                                xaxis_title='Time of Day')
    
    clean_ff_fig = px.line(tester[1], x='Date (MST)', y=['Total Load', 'Net Load'], color_discrete_sequence=[
                           'black', 'gray'], range_y=[0, None], labels={"y": "Generation Volume MWh"})
    clean_ff_fig.update_layout(title = '% Generation from Renewable vs. Fossil Fuel sources',
                               yaxis_title='Generation Volume (MW)')
    
    price_fig = px.line(tester[1], x='Date (MST)', y='Avg. Price')
    price_fig.update_layout(title='Hourly Marginal Price',
                            yaxis_title='Average Hourly Price ($/MW)',
                            xaxis_title='Time of Day')
    
    storage_fig = px.area(tester[1], x='Date (MST)', y='ENERGY STORAGE')
    storage_fig.update_layout(title = 'Hourly Energy Storage Charge/Discharge',
                              yaxis_title='Energy Storage Volume (MW)',
                              xaxis_title='Time of Day')
    
    EI_fig = px.scatter(tester[1], x='Date (MST)', y='RE_percent',
                        color='EI', color_continuous_scale=['green', 'yellow', '#D62728'])
    EI_fig.update_layout(title='Emission Intensity of Generated Electricity (tonsCO2e/MWh)',
                        yaxis_title='% Generation from Renewables',
                        xaxis_title='Time of Day')
    
    gen_pie_daily = px.pie(tester[0], values='Volume', names='Fuel Type', color = 'Fuel Type',
                           color_discrete_map=color_map, title='Generation by source')
    
    # The returned object is assigned to the component property of the Output
    #removed user_selected from the return below since i dont want it on the page for debugging anymore.
    return asset_gen_fig, clean_ff_fig, price_fig, storage_fig, EI_fig, gen_pie_daily, date


@callback(  # WORKING HERE TO CHANGE THE OUTPUT TEXT. REFER TO EXAMPLE ON PLOTLY FORUM
    #Output('date_range_display', 'children'),
    Output('asset_gen_multi', 'figure'),
    Output('gen_pie_multi', 'figure'),
    Output('my-date-picker-range', 'initial_visible_month'),
    
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_multi(start_date='2024-01-01', end_date='2024-01-03'):
    renge = f"{start_date}   -->   {end_date}"
    print(renge)
    if start_date <= end_date:
        tester = app_data_new.date_restrict(start_date,end_date)
        gen_multi = px.area(tester[0], x='Date (MST)', y="Volume", color="Fuel Type", 
                            color_discrete_map=color_map, title = 'Generation by asset type', 
                            labels={"y": "Generation Volume MWh"})
        gen_multi.update_layout(yaxis_title='Generation (MWh)',
                                xaxis_title='Date')

        gen_pie_multi = px.pie(tester[0], values='Volume', names='Fuel Type', color = 'Fuel Type',
                               color_discrete_map=color_map, title='% generation by asset type')
    else:
        gen_multi = 'LOADING...'
        gen_pie_multi = 'LOADING...'


    return gen_multi, gen_pie_multi, start_date




# The following code is for running locally in a browser
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

#This is for running the dash on Ploomber.io
# server = app.server
    
