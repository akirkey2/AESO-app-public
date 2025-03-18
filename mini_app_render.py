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
from dash import no_update
import dash_bootstrap_components as dbc
import datetime as dt
from datetime import date
from datetime import datetime
import mini_app_data_render
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
    'OTHER':'#93C1A8', #Pale green
    'COAL': '#000000',  # Black
    'DUAL FUEL':'#936400', #Dark Grey
    'GAS': '#9E8653',  # Brown
    'HYDRO': '#1F77B4',  # Blue
    'WIND': '#2CA02C',  # Green
    'SOLAR': '#FDB813',  # Yellow
    'ENERGY STORAGE':'#C24141', #Red
}

fuel_types = ['COAL','DUAL FUEL', 'GAS', 'OTHER',
              'ENERGY STORAGE','HYDRO', 'SOLAR','WIND']

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
                #html.Br(),                 html.Br(),            
                                 
                                 # This Div is a graph with title, left adjusted beside the following Div
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
                                 ], label='Hourly Interactive'),
            
            
            
        dcc.Tab(children=[
                html.Br(),
                dbc.Container(
                           dbc.Row([
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([html.Img(src=app.get_asset_url("Figure_1.png"),style={'width': 'auto', 'height': 'auto'})], className="p-0"),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6  # Takes up 8/12 of the row (70% equivalent)
                               ),
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([html.P("""When sorting plotting average hourly price vs. percent renewable generation we can see that the highest
                                                            hourly prices tend to coincide with other renewable energy generation, which should be too surprising
                                                            (marginal cost of RE is low) but it is nice to see it bear out in real-world data.
                                                            
                                                            Additionally, the histogram on top of the scatter shows us that hourly prices are clustered on the low-end.
                                                            The scatter can be misleading in this way as it's hard to quickly understand what the mean and median power prices may be.
                                                            Mean: $63, Median: $31, 25th P: $19, 75thP: $48.
                                                     """)], className='p-0'),
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
                                       dbc.CardBody([html.Img(src=app.get_asset_url("re_price_fig4.png"),style={'width': 'auto', 'height': 'auto'})], className="p-0"),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6  # Takes up 8/12 of the row (70% equivalent)
                               ),
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([html.P("""When graphed another way, we can see that power prices really do fall with higher renewable 
                                                            energy penetration on the grid. NEAT.
                                                     """)], className='p-0'),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6  
                               )
                           ])
                       ,fluid=True),
                
                ], label='Stats & Analysis'),
        ]),  # Closing dcc.Tabs
        html.Br(),
    ]),
])  # this closes out the app layout


# Callback for the daily tab


@callback(
    Output('asset_gen_multi', 'figure'),
    Output('gen_pie_multi', 'figure'),
    Output('clean_fossil_gen', 'figure'),
    Output('gen_price', 'figure'),
    Output('storage_volume', 'figure'),
    Output('EI_graph', 'figure'),
    Output('my-date-picker-range', 'initial_visible_month'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)
def update_multi(start_date, end_date):
    # Ensure both dates are selected before proceeding
    if not start_date or not end_date:
        return no_update  # Prevents update until both dates are selected

    # Ensure start_date is before end_date
    if start_date > end_date:
        return no_update  # Prevent update if invalid range is selected

    # Print for debugging
    print(f"Date Range Selected: {start_date} --> {end_date}")

    # Filter data based on selected date range
    tester = mini_app_data_render.date_restrict(start_date, end_date)
    df_pie = tester[fuel_types].sum().reset_index(name='Sum')

    # Create figures
    gen_multi = px.area(tester, x='Date (MST)', y=list(color_map.keys()), color_discrete_map=color_map, 
                         title='Generation by asset type', labels={"y": "Generation Volume MWh"})
    gen_multi.update_layout(yaxis_title='Generation (MWh)', xaxis_title='Date')

    gen_pie_multi = px.pie(df_pie, values='Sum', names='index', color='index',
                           color_discrete_map=color_map, title='% generation by asset type')

    clean_ff_fig = px.line(tester, x='Date (MST)', y=['Total Load', 'Net Load'], color_discrete_sequence=[
                           'black', 'gray'], labels={"y": "Generation Volume MWh"})
    clean_ff_fig.update_layout(title='% Generation from Renewable vs. Fossil Fuel sources',
                               yaxis_title='Generation Volume (MW)', yaxis_range=[0, None])

    price_fig = px.line(tester, x='Date (MST)', y='Price')
    price_fig.update_layout(title='Hourly Average Price',
                            yaxis_title='Average Hourly Price ($/MW)',
                            xaxis_title='Time of Day')

    storage_fig = px.area(tester, x='Date (MST)', y='ENERGY STORAGE')
    storage_fig.update_layout(title='Hourly Energy Storage Charge/Discharge',
                              yaxis_title='Energy Storage Volume (MW)',
                              xaxis_title='Time of Day')

    EI_fig = px.scatter(tester, x='Date (MST)', y='EI',
                        color='RE_percent', color_continuous_scale=['#D62728', 'yellow', 'green'])
    EI_fig.update_layout(title='Emission Intensity of Generated Electricity',
                        yaxis_title='Emission Intensity (tonsCO2e/MWh)',
                        xaxis_title='Time of Day',
                        coloraxis_colorbar_title='% Renewables',
                        coloraxis_colorbar_title_font_size=12)

    return gen_multi, gen_pie_multi, clean_ff_fig, price_fig, storage_fig, EI_fig, start_date



# The following code is for running locally in a browser
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
