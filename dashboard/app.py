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

    

population_df = db._fetch_data("population")
print(population_df.head(10))

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
    app.run_server(debug=True, host="0.0.0.0", port=5000)