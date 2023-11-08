import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots 
from Database import Database
from time import sleep
from datetime import datetime


app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title="Datadatectives dashboard"

db = Database()

if False:
    db._update_database()

if False:
    db._update_database_csv()

if False:
    db._to_csv()

ec_df = db._fetch_data("SELECT * FROM electricity_consumption")
temp_df = db._fetch_data("SELECT * FROM temperature")

max_gwh = max(db._fetch_data("SELECT gwh FROM electricity_consumption"))
min_gwh = min(db._fetch_data("SELECT gwh FROM electricity_consumption"))

available_years = sorted(db._fetch_data("SELECT DISTINCT year FROM electricity_consumption"), key=int)
year = 2018
indicator = "Consumption"
display_choro = "electricity_consumption"
month = 2
country=""

def create_empty_figure(title=''):
    fig = go.Figure()
    fig.update_layout(title=title, showlegend=False)
    return fig

# Update the choropleth figure
@app.callback(
    Output('choropleth', 'figure'),
    [Input('indic-dropdown', 'value'),
    Input('month-slider', 'value'),
    Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value')]
)
def update_choropleth(indicator, month, year, display):
    sql = f"""
            SELECT country, gwh FROM {display} 
            WHERE year='{year}' AND indicator='{indicator}' AND month='{month}'
            """
    df = db._fetch_data(sql)
    sleep(0.1)
    fig = px.choropleth(df, 
                        locations="country", 
                        color='gwh',
                        hover_name="country",
                        color_continuous_scale="Emrld",
                        scope="europe",
                        range_color=(min_gwh, max_gwh),
                        title=f"{indicator} for {year} and {display}"
                        )

    fig.update_geos(
        visible=True, resolution=50,
        showcountries=True, countrycolor="Black",
        fitbounds="locations",
        center=dict(lat=51.1657, lon=10.4515),
        projection_scale=15         
    )

    fig.update_layout(
        autosize=False,
        geo=dict(
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        title= f'GWH {indicator} in Europe for the month {month} in the year {year}',
        width=800,
        dragmode=False
        )

    return fig

@app.callback(
    Output('bar-chart-1', 'figure'),
    [Input('indic-dropdown', 'value'),
    Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value'),
    Input('country', 'children')]
)
def update_monthly_energy(indicator, year, display, country):
    if country=="":
        return create_empty_figure("Select a Country in the choropleth to view data")
    sql = f"""
            SELECT e.country, e.month, e.gwh FROM {display} as e
            WHERE e.year='{year}' AND e.indicator='{indicator}' AND e.country='{country}'
            """
            
    df = db._fetch_data(sql)
    fig = px.bar(df, x='month', y='gwh', 
                 title=f"Energy {indicator} for {country} in {year}",
                 labels={"gwh" : f"Energy {indicator} in Gigawatt hours"},
                 color="gwh",
                 # TODO zorg ervoor dat de maanden goed staan, dit is alleen soms
                 text="month",
                 text_auto='.2s',
                 color_continuous_scale="Emrld",
                 )
    return fig
 

@app.callback(
    Output('bar-chart-temp', 'figure'),
    [Input('indic-dropdown', 'value'),
    Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value'),
    Input('country', 'children')]
)
def update_bar_energy_temperature(indicator, year, display, country):
    if country == "":
        return create_empty_figure("")

    sql_energy = f"""
            SELECT e.country, e.month, e.gwh FROM {display} as e
            WHERE e.year='{year}' AND e.indicator='{indicator}' AND e.country='{country}'
            """

    sql_temp = f"""
            SELECT t.country, t.month, t.temperature FROM temperature as t
            WHERE t.year='{year}' AND t.country='{country}'
            """
    
    # Create a subplot with two Y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df_energy = db._fetch_data(sql_energy)
       # Add the primary bar chart for electricity consumption
    fig.add_trace(go.Bar(x=df_energy['month'], y=df_energy['gwh'], name='GWH', marker_color='#08308e'))
    
    df_temp = db._fetch_data(sql_temp)
    print(df_temp)
       # Add the secondary line chart for temperature
    fig.add_trace(go.Scatter(x=df_temp['month'], y=df_temp['temperature'], mode='lines+markers', name='Temperature', line=dict(color='#E7243B'), yaxis='y2'))

    

    # Update the layout to display both Y-axes
    fig.update_layout(
        title=f'Electricity Consumption and Temperature in {country} for year {year}',
        xaxis=dict(title='Month'),
        yaxis=dict(title='GWH', side='left'),
        yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
        showlegend=True,
    )
    
    
    return fig

 





@app.callback(
    Output('country', 'children'),
    Input('choropleth', 'clickData'), 
    suppress_callback_exceptions=True
)
def get_country(clickData):
    if clickData == None:
        return ""   
    country = clickData["points"][0]['location']
    return country 





app.layout = html.Div(children=[
    html.H1('Hello Dash!'),
    html.Div(className='row', children=[
        html.Div(className='col-6 col-xs-12', children=[
            html.Br(),
            dcc.Loading(id="loading-choro", type="default", children=dcc.Graph(id="choropleth", figure=update_choropleth(indicator, month, year, display_choro)))]),
        html.Div(className='col-6 col-xs-12', children=[
            html.Br(),
            dcc.Loading(id="loading-bar-1", type="default", children=dcc.Graph(id='bar-chart-1')),
            html.Br(),
            dcc.Loading(id="loading-bar-2", type="default", children=dcc.Graph(id='bar-chart-temp'))
        ])
    ]),
     html.Div(className='row', children=[
        html.Div(className="col-6 col-xs-12", children=[
            dcc.Slider(
                id='year-radio',
                min=min(available_years),
                max=max(available_years),
                marks={int(year) : str(year) for year in available_years},
                value=year,
                step=1,
            ),
             dcc.Slider(
            id='month-slider',
            marks={month: str(month) for month in range(1, 13)},
            step=1,
             ),
            dcc.Dropdown(
                id='indic-dropdown',
                options=[{'label': indic, 'value': indic} for indic in ec_df['indicator'].unique()],
                value=ec_df['indicator'].unique()[0],
                searchable=False
            ),
            dcc.Dropdown(
                id='display-mode-dropdown',
                options=[
                    {'label': 'Total GWH', 'value': 'electricity_consumption'},
                    {'label': 'GWH per capita', 'value': 'consumption_capita'},
                ],
                value='electricity_consumption',
                searchable=False
            ),
            html.Div(id="country")
        ])
    ])
])

if __name__ == '__main__':
    print("Started")
    app.run_server(debug=False, host="0.0.0.0", port=8080)
    # Casper: 172.19.0.3
    # Thomas: 127.0.0.1:8080
    # Alle andere: 127.0.0.1
