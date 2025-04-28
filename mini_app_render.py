 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:38:59 2024

@author: aaronkirkey
"""

#%% Environment setup
import pandas as pd
import os
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Input, Output
from dash import no_update
import dash_bootstrap_components as dbc
from datetime import date
import gunicorn

# Define a global template with a centered title
pio.templates["custom_template"] = pio.templates["plotly_white"]
pio.templates["custom_template"]["layout"]["title"] = {
    "x": 0.5,  # Centers the title
    "xanchor": "center"
}
#%%
color_map = {
    'Other': '#93C1A8',  # Pale green
    'Coal': '#000000',   # Black
    'Dual Fuel': '#936400',  # Dark Grey
    'Gas': '#9E8653',    # Brown
    'Hydro': '#1F77B4',  # Blue
    'Wind': '#2CA02C',   # Green
    'Solar': '#FDB813',  # Yellow
    'Energy Storage': '#C24141',  # Red
}

fuel_types = [
    'Coal', 'Dual Fuel', 'Gas', 'Other',
    'Energy Storage', 'Hydro', 'Solar', 'Wind'
]

fuel_dict = {
    'Coal': 'Fossil Fuel',
    'Dual Fuel': 'Fossil Fuel',
    'Gas': 'Fossil Fuel',
    'Hydro': 'Renewable',
    'Solar': 'Renewable',
    'Wind': 'Renewable',
    'Other': 'Other',
    'Energy Storage': 'Other'
}
#%% Dataframe setup

df_hourly_vol = pd.read_csv('assets/mini_df.csv')
df_hourly_vol['Date (MST)'] = pd.to_datetime(df_hourly_vol['Date (MST)'], format ='%Y-%m-%d %H:%M:%S')

#%%
start_date='2024-01-01'
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
#%%

# Set this template as the default
pio.templates.default = "custom_template"

app = Dash(__name__,external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server
app.title = 'AESO Energy Dash'
app.layout = html.Div(style={'backgroundColor':'#818894'},
                      children=[
    html.Div([html.H1(children='AESO Energy Dash', style={'textAlign': 'center', 'fontSize': 48,'color':'white'}),
              html.Br(),
              html.Div(children="""*Disclaimer: This dashboard and contents are in no way 
             affiliated with the AESO and serves only as a personal project to 
             improve my data science and data viz skills with respect to grid
             data. For questions, comments or improvement ideas, please contact
             me at: akirkey2@gmail.com with the subject line 'AESO dash project'.
             Thank you for your interest!""", style={'color':'white','margin-left':'20px'})]),
    html.Br(),

    html.Div([

        dcc.Tabs([
            dcc.Tab(children=[
                dbc.Col(dbc.Card(children=[
                    html.Div(children='Choose date range:',
                         style={'fontSize': 18,'color':'black'}),
                html.Div(
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date(2024, 1, 1),
                        max_date_allowed=date(2024, 12, 31),
                        initial_visible_month=date(2024, 1, 1),  # Default month
                        start_date=date(2024, 1, 1),
                        end_date=date(2024, 1, 4)
                        )
                    ) # closes div around date picker
                ], className="shadow-sm m-3"), #closes dbc card
                width = 2
            ),#closes dbc col
                html.Div(id="date-picker-container"),  # Placeholder for dynamic updates

                                 
                                 # This Div contains first 2 graphs
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
                                                       dbc.CardBody([dcc.Graph(id='total_gen_load')], className="p-0"),
                                                       className="shadow-sm m-2"
                                                   ),
                                                   width=6
                                               ),

                                               dbc.Col(
                                                   dbc.Card(
                                                       dbc.CardBody([dcc.Graph(id='storage_volume')], className='p-0'),
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
                                                       dbc.CardBody([dcc.Graph(id='gen_price')], className="p-0"),
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
                html.H2(children='Generated Electricity and Emissions', style={'textAlign': 'Left', 'fontSize': 40,'color':'white','margin-left':'20px'}),
                 html.Br(),
                
                dbc.Container(
                           dbc.Row([
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([html.Img(src=app.get_asset_url("Emissions Intensity AESO 232425.png"),style={'width': 'auto', 'height': 'auto'})], className="p-0"),
                                       className="shadow-sm m-2"
                                   ),
                                   width=6  # Takes up 8/12 of the row (70% equivalent)
                               ),
                               dbc.Col(
                                   dbc.Card(
                                       dbc.CardBody([html.P(["""Electricity in Alberta remains among the dirtiest of all the provinces in large part due to a lack of
                                                            hydro power that other provinces such as Ontario, British Columbia, Quebec and Manitoba boast. That being said, AESO is 
                                                            making strides in reducing the emissions intensity (EI) of its generated power as shown in the figure to the left."""
                                                            ,html.Br(), html.Br(),
                                                            
                                                     """The average EI of power generated on AESO in 2023 was 454 gCO2e/kWh. This was reduced to 406 gCO2e/kWh in
                                                     2024 representing an 11% reduction in a single year. EI in 2025 has so far been reduced to 390 gCO2e/kWh (14% reduction compared to 2023) 
                                                     despite the earliest months of the year being the dirtiest."""
                                                     ,html.Br(), html.Br(),
                                                     
                                                     """Also noticeable in the figure is the month-to-month variation in EI. There are 3 major factors for this phenomenon:"""
                                                     ,html.Br(),html.Br(),
                                                     html.Strong('1. Grid Asset Mix:'),""" More coal will raise EI and more renewables will lower it. A phase out of coal and dual fuel power plants 
                                                     was initiated in 2024-01 and completed by 2024-06 """
                                                     ,html.Br(),html.Br(),
                                                     html.Strong('2. Wind & Solar Generation: '), """"As critics of renewables like to point out "renewables only work when the sun 
                                                     shines and the wind blows". Some day, weeks, or months are windier and/or sunnier than others. For example, in 2023-12, 2024-04 and 2025-01
                                                     considerably more wind power was generated on AESO than in the months before or after them, resulting in a corresponding dip in EI.
                                                     Likewise, May, June and July (05, 06, 07) are the sunniest months of the year and as such, solar generation peaks in those months."""
                                                     ,html.Br(),html.Br(),
                                                     html.Strong('3. Total Load (Electricity Demand):'), """ In moments of moderate load, renewables outcompete fossil fuels on price and are thus preferentially dispatched onto AESO. 
                                                     However, during peak load events, all generating assets must be dispatched meaning more expensive gas (and previously coal) plants operate at their maximum output and since the
                                                     energy mix on AESO is dominated by fossil fuels, this increases EI. Peak loads are typically in winter in cold climates and
                                                     the summer in hot climates due to the energy used in heating and cooling our living spaces. This manifests as an increase 
                                                     in EI during very hot or very cold spells. Peak load on AESO tends to be in the winter, with hotter periods seeing a small bump as well."""])], className='p-0'),
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
                
                ], label='Stats & Analysis **Work in Progress**'),
        ]),  # Closing dcc.Tabs
        html.Br(),
    ]),
])  # this closes out the app layout


# Callback for the daily tab


@callback(
    Output('asset_gen_multi', 'figure'),
    Output('gen_pie_multi', 'figure'),
    Output('total_gen_load', 'figure'),
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
    df = date_restrict(start_date, end_date)
    df_pie = df[fuel_types].sum().reset_index(name='Sum')
    df_pie['Source'] = df_pie['index'].map(fuel_dict)
    df_pie['percent'] = (df_pie['Sum'] / df_pie['Sum'].sum())*100
    ffg = df_pie.loc[df_pie['Source']=='Fossil Fuel']['percent'].sum()
    reg = df_pie.loc[df_pie['Source']=='Renewable']['percent'].sum()
     # Create figures
    gen_multi = px.area(df, x='Date (MST)', y=list(color_map.keys()), color_discrete_map=color_map, 
                          title='Generation by Asset Type', labels={"y": "Generation Volume MW"})
    gen_multi.add_hline(y=df['Total Generation'].mean(),
         line_dash="dash",
         label=dict(
             text='Mean Total Generation',
             textposition="end",
             font=dict(size=14, color="black"),
             yanchor="bottom",
         ))
    gen_multi.update_layout(yaxis_title='Generation (MW)', xaxis_title='Date & Time',
                            legend_title_text='Fuel Type')
    gen_pie_multi = px.pie(df_pie,values='percent',names='index',color='index',
                            color_discrete_map=color_map, title='Total Generation by Asset Type')
    gen_pie_multi.update_traces(texttemplate='%{value:.1f}%')
    gen_pie_multi.add_annotation(text=f"Fossil Fuels:{ffg:.1f}%, Renewables:{reg:.1f}%",
                   xref="paper", yref="paper", font={'size':14},
                   x=0.15, y=-0.1, showarrow=False)
    gen_pie_multi.update_layout(margin=dict(t=60, b=60, l=95, r=60))

    gen_load_fig = px.line(df, x='Date (MST)', y=['Total Generation', 'Total Load'], 
                          color_discrete_sequence=['black', '#636EFA'], labels={"y": "Volume MWh"})
    # gen_load_fig.add_trace(go.Scatter(
    #                         x=df['Date (MST)'],
    #                         y=df['Total Generation'],
    #                         mode='lines',
    #                         name='Total Generation',
    #                         fill='tonexty',
    #                         line=dict(color='black'),
    #                         fillcolor='rgba(255, 0, 0, 0.2)'  # Transparent fill
    #                   ))
    
    mask = df['Total Load'] > df['Total Generation']

    # Find continuous segments where condition is true
    segments = []
    current = []

    for i in range(len(df)):
        if mask.iloc[i]:
            current.append(i)
        else:
            if current:
                segments.append(current)
                current = []
    if current:
        segments.append(current)

    # Create figure and add base traces

    # Add shaded regions
    for seg in segments:
        x = list(df['Date (MST)'].iloc[seg]) + list(df['Date (MST)'].iloc[seg][::-1])
        y = list(df['Total Load'].iloc[seg]) + list(df['Total Generation'].iloc[seg][::-1])
        
        gen_load_fig.add_trace(go.Scatter(
            x=x,
            y=y,
            fill='toself',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255,0,0,0.3)',
            hoverinfo='skip',
            name='Overload Area',
            showlegend=False
        ))
    gen_load_fig.update_layout(title='Total Generation and AESO Internal Load',
                           yaxis_title='Volume (MW)', yaxis_range=[0, None],
                           xaxis_title='Date & Time', legend_title_text='',
                           legend=dict(
                                            yanchor="top",
                                            y=0.32,
                                            xanchor="left",
                                            x=0.85
                                        ))

    price_fig = px.line(df, x='Date (MST)', y='Price')
    price_fig.add_hline(y=df['Price'].mean(),
        line_dash="dash",
        label=dict(
            text='Mean Price',
            textposition="end",
            font=dict(size=14, color="black"),
            yanchor="bottom",
        ))
    price_fig.update_layout(title='Hourly Average Price',
                            yaxis_title='Average Hourly Price ($/MWh)',
                            xaxis_title='Date & Time')

    storage_fig = px.area(df, x='Date (MST)', y='Energy Storage')
    storage_fig.update_layout(title='Hourly Energy Storage Charge/Discharge',
                              yaxis_title='Energy Storage Volume (MW)',
                              xaxis_title='Date & Time')

    EI_fig = px.scatter(df, x='Date (MST)', y='EI',
                        color='RE_percent', color_continuous_scale=['#ce3d3d', '#f1c232', '#3aa00d'])
    EI_fig.add_hline(y=df['EI'].mean(),
        line_dash="dash",
        label=dict(
            text='Mean EI',
            textposition="end",
            font=dict(size=14, color="black"),
            yanchor="bottom",
        ))
    EI_fig.update_layout(title='Emission Intensity of Generated Electricity',
                        yaxis_title='Emission Intensity (gCO2e/kWh)',
                        xaxis_title='Date & Time',
                        coloraxis_colorbar_title='% Renewables',
                        coloraxis_colorbar_title_font_size=12)


    return gen_multi, gen_pie_multi, gen_load_fig, price_fig, storage_fig, EI_fig, start_date

#%%
# The following code is for running locally in a browser
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
