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

max_gwh = max(db._fetch_data("SELECT gwh FROM electricity_consumption"))
min_gwh = min(db._fetch_data("SELECT gwh FROM electricity_consumption"))

available_years = sorted(db._fetch_data("SELECT DISTINCT year FROM electricity_consumption"), key=int)
year = 2018
indicator = "Consumption"
display_choro = "electricity_consumption"
country=""

def create_empty_figure(title=''):
    fig = go.Figure()
    fig.update_layout(title=title, showlegend=False)
    return fig

# Update the choropleth figure
@app.callback(
    Output('choropleth', 'figure'),
    [Input('indic-dropdown', 'value'),
    Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value')]
)
def update_choropleth(indicator, year, display):
    sql = f"""
            SELECT country, gwh FROM {display} 
            WHERE year='{year}' AND indicator='{indicator}'
            """
    df = db._fetch_data(sql)
    sleep(0.1)
    fig = px.choropleth(df, 
                        locations="country", 
                        color='gwh',
                        hover_name="country",
                        color_continuous_scale="Emrld",
                        scope="europe",
                        range_color=(min_gwh, max_gwh)
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
        margin = dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=4,
                autoexpand=True
            ),
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
            SELECT e.country, e.month, e.gwh, t.temperature FROM {display} as e
            INNER JOIN temperature as t ON e.country=t.country AND e.year=t.year AND e.month=t.month
            WHERE e.year='{year}' AND e.indicator='{indicator}' AND e.country='{country}'
            """
    df = db._fetch_data(sql)
    fig = px.bar(df, x='month', y='gwh', 
                 title=f"Energy {indicator} for {country} in {year}",
                 labels={"gwh" : f"Energy {indicator} in Gigawatt hours"},
                 color="gwh",
                 text_auto='.2s',
                 color_continuous_scale="Emrld",
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
            dcc.Loading(id="loading-choro", type="default", children=dcc.Graph(id="choropleth", figure=update_choropleth(indicator, year, display_choro)))]),
        html.Div(className='col-6 col-xs-12', children=[
            html.Br(),
            dcc.Loading(id="loading-bar-1", type="default", children=dcc.Graph(id='bar-chart-1'))
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
    # Alle andere: 127.0.0.1
