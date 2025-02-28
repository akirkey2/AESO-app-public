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
pio.renderers.default='browser'

#%%  Dash stuff
# datte = '2024-01-06' # Placeholder value
app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.SANDSTONE])
app.title = 'AESO Energy Dash'
app.layout = html.Div([
    html.Div([html.H1(children='AESO Energy Dash', style={'textAlign': 'center', 'fontSize': 48}),
              html.Br(),
              html.Div(children="""*Disclaimer: This web-dash and contents are in no way 
             affiliated with the AESO and serves only as a personal project to 
             improve my data science and data viz skillset with respect to grid
             data. For questions, comments or improvement ideas, please contact
             me at: akirkey2@gmail.com with the subject line 'AESO dash project'.
             Thank you for your interest!""")]),
    html.Br(),
    html.Br(),
    html.Br(),

    html.Div([

        dcc.Tabs([
            dcc.Tab(children=[
                 html.Br(),
                 html.Br(),
                 html.Div(children='Choose Date: ', style={'fontSize': 20}),
                 dcc.DatePickerSingle(  # This is a drop-down calendar that updates the elements on the page
                     id='date-picker-single',
                     min_date_allowed=date(2024, 1, 1),
                     max_date_allowed=date(2024, 6, 30),
                     initial_visible_month=date(2024, 1, 1),
                     date=date(2024, 1, 1),
                     display_format='Y-M-D'),
                 html.Br(),
                 html.Br(),
                 # Visual feedback on page displaying date
                 html.Div(children='Date chosen: (for debugging)*',
                          style={'fontSize': 20}),
                 dcc.Markdown(id='date_display', children=''),
                 html.Br(),
                 # html.Div(children ='Hourly Data',style={'fontSize': 32,'font-weight':'bold','textAlign':'center'}),
                 html.Br(),
                 html.Br(),
                 # This Div is a graph with title, left adjusted beside the following Div
                 html.Div(children=[
                     html.Div(children='Hourly generation on AESO by asset & fuel type', style={
                              'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     html.Div(dcc.Graph(id='asset_gen'),
                              style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center'})
                 ],
                     style={'display': 'inline-block', 'width': '70%', 'verticalAlign': 'top', 'textAlign': 'center'}),

                 html.Div(children=[
                     html.Div(children='Generation by source', style={
                              'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     html.Div(dcc.Graph(id='gen_pie_daily'), style={
                         'display': 'inline-block', 'width': '100%', 'textAlign': 'center'}),
                 ],
                     style={'display': 'inline-block', 'width': '30%', 'verticalAlign': 'top', 'textAlign': 'center'}),

                 # This Div is a graph with title, right adjusted beside the previous Div
                 html.Div(children=[
                     html.Div(children='% Generation from Renewable vs. Fossil Fuel sources', style={
                              'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     html.Div(dcc.Graph(id='clean_fossil_gen'),
                              style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center'})
                 ],
                     style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top', 'textAlign': 'center'}),

                 # This Div is a graph with title, left adjusted beside the following Div
                 html.Div(children=[
                     html.Div(children='Hourly Marginal Price', style={
                              'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     html.Div(dcc.Graph(id='gen_price'),
                              style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center'})
                 ],
                     style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top', 'textAlign': 'center'}),

                 # This Div is a graph with title, right adjusted beside the previous Div
                 html.Div(children=[
                     html.Div(children='Hourly Energy Storage Charge/Discharge',
                              style={'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     html.Div(dcc.Graph(id='storage_volume'),
                              style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center'})
                 ],
                     style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top', 'textAlign': 'center'}),
                 html.Div(children=[
                     html.Div(children='Emission Intensity of Generated Electricity (tonsCO2e/MWh)',
                              style={'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     html.Div(dcc.Graph(id='EI_graph'),
                              style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center'})
                 ],
                     style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top', 'textAlign': 'center'}),


                 # Reference Tables
                 html.Div(children='Hourly Statistics', style={
                          'fontSize': 32, 'font-weight': 'bold', 'textAlign': 'center'}),
                 html.Br(),

                 # This Div contains a table and a title and is left adjusted beside following Div
                 html.Div(children=[
                     html.Div(children='Contribution on the grid (MW)', style={
                              'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     dash_table.DataTable(
                         id='summary_table',
                         page_size=24,
                         css=[{'selector': 'table', 'rule': 'width: 800px; height: 300px; margin: 0 auto; overflow: auto;'},
                              # Adjusting font size for table cells
                              {'selector': 'td',
                               'rule': 'font-size: 12px;'},
                              {'selector': 'th',
                               'rule': 'font-size: 12px; font-weight: bold;'}
                              ]
                     )
                 ],
                     style={'display': 'inline-block', 'width': '49%', 'verticalAlign': 'top', 'textAlign': 'center'}),


                 # This Div contains a table and a title and is right adjusted beside previous Div
                 html.Div(children=[
                     html.Div(children='% Contribution on the grid', style={
                              'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                     dash_table.DataTable(
                         id='percent_table',
                         page_size=24,
                         css=[{'selector': 'table', 'rule': 'width: 800px; height: 300px; margin: 0 auto; overflow: auto;'},
                              # Adjusting font size for table cells
                              {'selector': 'td',
                               'rule': 'font-size: 12px;'},
                              {'selector': 'th',
                               'rule': 'font-size: 12px; font-weight: bold;'}
                              ]
                     )
                 ],
                     style={'display': 'inline-block', 'width': '49%', 'verticalAlign': 'top', 'textAlign': 'center'}),
                 ],
                label='Single Day'),
            dcc.Tab(children=[
                html.Br(),
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(2024, 1, 1),
                    max_date_allowed=date(2024, 6, 30),
                    initial_visible_month=date(2024, 1, 1),
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 1, 4)
                ),
                html.Br(),
                # Visual feedback on page displaying date
                html.Div(children='Dates chosen: (for debugging)*',
                         style={'fontSize': 20}),
                dcc.Markdown(id='date_range_display', children=''),
                html.Br(),

                html.Div(children=[
                    html.Div(children='Generation by asset type', style={
                             'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                    html.Div(dcc.Graph(id='asset_gen_multi'),
                             style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center'}),
                ],
                    style={'display': 'inline-block', 'width': '70%', 'verticalAlign': 'top', 'textAlign': 'center'}),


                html.Div(children=[
                    html.Div(children='% generation by asset type', style={
                             'fontSize': 22, 'font-weight': 'bold', 'textAlign': 'center'}),
                    html.Div(dcc.Graph(id='gen_pie_multi'), style={
                        'display': 'inline-block', 'width': '100%', 'textAlign': 'center'}),
                ],
                    style={'display': 'inline-block', 'width': '30%', 'verticalAlign': 'top', 'textAlign': 'center'}),

            ], label='Multi-Day'),
        ]),  # Closing dcc.Tabs
        html.Br(),
    ]),
])  # this closes out the app layout


# Callback for the daily tab
@callback(
    Output(component_id='date_display', component_property='children'),
    Output('summary_table', component_property='data'),
    Output('percent_table', 'data'),
    Output('asset_gen', 'figure'),
    Output('clean_fossil_gen', 'figure'),
    Output('gen_price', 'figure'),
    Output('storage_volume', 'figure'),
    Output('EI_graph', 'figure'),
    Output('gen_pie_daily', 'figure'),

    Input(component_id='date-picker-single', component_property='date'))
# Calls functions with updated date to make dash reactive to selected date
def update_date(user_selected):
    # The function argument comes from the component property of the Input
    print(user_selected)
    df_daily = app_data_new.price_ei_vol_day(user_selected)

    summary_data = app_data_new.df_hourly(user_selected).to_dict('records')
    percent_data = app_data_new.df_percent(user_selected).to_dict('records')
    asset_gen_fig = px.area(df_daily[0], x='Date (MST)', y="Volume", color="Fuel Type", labels={
                            "y": "Generation Volume MWh"})
    asset_gen_fig.update_layout(yaxis_title='Generation Volume (MW)')
    clean_ff_fig = px.line(df_daily[1], x='Date (MST)', y=['Total Load', 'Net Load'], color_discrete_sequence=[
                           'black', 'gray'], range_y=[0, None], labels={"y": "Generation Volume MWh"})
    clean_ff_fig.update_layout(yaxis_title='Generation Volume (MW)')
    price_fig = px.line(df_daily[1], x='Date (MST)', y='Avg. Price')
    price_fig.update_layout(yaxis_title='Average Hourly Price ($/MW)')
    storage_fig = px.area(app_data_new.df_hourly(
        user_selected), x='Date (MST)', y='ENERGY STORAGE')
    storage_fig.update_layout(yaxis_title='Energy Storage Volume (MW)')
    EI_fig = px.scatter(df_daily[1], x='Date (MST)', y='RE_percent',
                        color='EI', color_continuous_scale=['green', 'yellow', '#D62728'])
    EI_fig.update_layout(yaxis_title='% Generation from Renewables')
    # title='% Generation over timeframe')
    gen_pie_daily = px.pie(df_daily[0], values='Volume', names='Fuel Type')
    # The returned object is assigned to the component property of the Output
    return user_selected, summary_data, percent_data, asset_gen_fig, clean_ff_fig, price_fig, storage_fig, EI_fig, gen_pie_daily


@callback(  # WORKING HERE TO CHANGE THE OUTPUT TEXT. REFER TO EXAMPLE ON PLOTLY FORUM
    Output('date_range_display', 'children'),
    Output('asset_gen_multi', 'figure'),
    Output('gen_pie_multi', 'figure'),
    # Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    renge = f"{start_date}   -->   {end_date}"
    print(renge)
    if start_date <= end_date:
        df_multi = app_data_new.price_ei_vol_week(start_date, end_date)
        gen_multi = px.area(df_multi[1], x='Date (MST)', y="Volume", color="Fuel Type", labels={
                            "y": "Generation Volume MWh"})
        # , title='% Generation over timeframe')
        gen_pie_multi = px.pie(df_multi[1], values='Volume', names='Fuel Type')
    else:
        gen_multi = 'LOADING...'
        gen_pie_multi = 'LOADING...'
        # multi_gen = px.area(app_data_new.price_ei_vol_week(start_date,end_date=start_date)[1], x='Date (MST)', y="Volume", color="Fuel Type",labels={"y": "Generation Volume MWh"})
        # gen_pie_multi = px.pie(app_data_new.price_ei_vol_week(start_date,end_date=start_date)[1], values='Volume', names='Fuel Type', title='% Generation over timeframe')
    return renge, gen_multi, gen_pie_multi

# @callback(
#     Output('asset_gen_multi','figure'),
#     Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date')
#     )
# def update_multi(start_date,end_date):
#     gen_fig_multi = px.area(app_data_new.price_ei_vol_day(start_date,end_date), x='Date (MST)', y="Volume", color="Fuel Type",labels={"y": "Generation Volume MWh"})
#     return gen_fig_multi


# The following code is for running locally in a browser
if __name__ == '__main__':
    app.run_server(port=2222)

#This is for running the dash on Ploomber.io
# server = app.server
    