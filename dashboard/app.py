import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from Charts import Choropleth
from Database import Database
from time import sleep


app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title="We testen wat!"

db = Database()

if False:
    db._update_database()

ec_df = db._fetch_data("electricity_consumption")
et_df = db._fetch_data("electricity_types")
pop_df = db._fetch_data("population")
tmp_df = db._fetch_data("temperature")

df = db._fetch_data("electricity_consumption", False, "Country", "GWH", Year="=2010")
possible_years = sorted(db._fetch_data("electricity_consumption", True, "Year"), key=int)
selected_year = 2018
selected_indicator = "consumption"

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
    app.run_server(debug=False, host="0.0.0.0", port=8080)
    # Casper: http://172.19.0.3:5000/
    # Dagmar: http://127.0.0.1:5000/

    
# marks = []