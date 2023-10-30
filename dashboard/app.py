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
from Charts import Choropleth
from Database import Database

app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title="We testen wat!"
app.description="Dit is een omschrijving 0_O"

# db = Database()
# df = db._fetch_data("electricity", False, "Country", "GWH", Year="=2010")
# possible_years = sorted(db._fetch_data("electricity", True, "Year"), key=int)
# print(df.head())
selected_year = 2018
selected_indicator = "consumption"
df = pd.DataFrame()

app.layout = html.Div(children=[
    html.H1('Hello Dash!'),
    html.Div(className='row', children=[
        html.Div(className='col-8', children=[
            html.Div(f'GWH {selected_indicator} distribution in Europe for {selected_year}', className="GWH"),
            dcc.Graph(className="choropleth", id="choropleth", figure=Choropleth(df))
        ]),
        html.Div('Lorem ipsum 2', className='col-4')
    ]),
     html.Div(className='row', children=[
         html.Div(className="col-6") 
    ])
])



# @app.callback(
#     Output(component_id='choropleth'),
#     Input(component_id='chloroslider', component_property="value")
# )
# def update_choropleth(selected_year):
#     df = db._fetch_data("electricity", False, "Country", "GWH", Year=f"={selected_year}")
#     Choropleth(df)

if __name__ == '__main__':
    print("Started")
    app.run_server(debug=True, host='0.0.0.0', port=5000)
    # http://127.0.0.1:5000/

    
# marks = []