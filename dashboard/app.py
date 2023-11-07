import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from Electricty import MonthlyElectricity
from Temperature import TemperatureDownloader
from Population import DownloadPopulationData
from os import listdir
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from Charts import update_choropleth
from Database import Database
import os

app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title="We testen wat!"
app.description="Dit is een omschrijving 0_O"


db=Database()


LIST = os.listdir('C:\\Users\\valke\\OneDrive\\Documenten\\GitHub\\DataDetectives\\dashboard\\data')

<<<<<<< Updated upstream
for file in LIST:
    path = os.path.join('C:\\Users\\valke\\OneDrive\\Documenten\\GitHub\\DataDetectives\\dashboard\\data', file)
    with open(path):
        df = pd.read_csv(path)
    a = file.split(".")[0]
    db._load_data(a=df)
    print(file.split(".")[0])    
    
    
    

population_df = db._fetch_data("population")
print(population_df.head(10))
=======
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

def create_empty_figure(title='Select a Country in the choropleth to view data'):
    fig = go.Figure()
    fig.update_layout(title=title, showlegend=False)
    return fig

# Update the choropleth figure
@app.callback(
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
        title= f'GWH {indicator} in Europe for month {month} in the year {year}',
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
        return create_empty_figure()
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
        return create_empty_figure()

    sql_energy = f"""
            SELECT e.country, e.month, e.gwh FROM {display} as e
            WHERE e.year='{year}' AND e.indicator='{indicator}' AND e.country='{country}'
            """

    sql_temp = f"""
            SELECT t.country, t.month, t.temperature FROM {display} as t
            WHERE t.year='{year}' AND t.country='{country}'
            """

    # Create a subplot with two Y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    df_energy = db._fetch_data(sql_energy)
    fig.add_trace(
        go.Bar(df_energy, x='month', y='gwh', name = "GWH", marker_color='#08308e')
    )
    
    df_temp = db._fetch_data(sql_temp)
    fig.add_trace(go.Scatter(df_temp, x='month', y='temperature', mode='lines+markers', name='Temperature', line=dict(color='#E7243B'), yaxis='y2'))


    # Update the layout to display both Y-axes
    fig.update_layout(
        title=f'Electricity Consumption and Temperature in {country} for year {year}',
        xaxis=dict(title='Month'),
        yaxis=dict(title='GWH', side='left'),
        yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
        showlegend=True,
    )
    return fig
>>>>>>> Stashed changes

app.layout = html.Div([
    html.H1('Hello Dash!'),
    html.P('Dash converts this kind of semi-python into html'),
    html.Div([
        html.Div('Lorem ipsum 1', className='col'),
        html.Div('Lorem ipsum 2', className='col col-lg-2')
    ], className='row')
], className='container')

if __name__ == '__main__':
    print("Started")
    app.run_server(debug=True, host='172.19.0.3', port=5000)