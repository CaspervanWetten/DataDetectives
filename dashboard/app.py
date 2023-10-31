import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
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

if False:
    db._update_database_csv()

ec_df = db._fetch_data("electricity_consumption")
et_df = db._fetch_data("electricity_types")
pop_df = db._fetch_data("population")
tmp_df = db._fetch_data("temperature")

print(ec_df.head(2))
print(et_df.head(2))
print(pop_df.head(2))
print(tmp_df.head(2))

df = db._fetch_data("electricity_consumption", "country", "gwh", year="=2010")
print(df.head(2))
possible_years = sorted(db._fetch_data("electricity_consumption", "year", distinct=True), key=int)
print(possible_years)
selected_year = 2018
selected_indicator = "consumption"

# @app.callback(
#     Output('selected_country_id', 'selected_country'),
#     Input('choropleth', 'clickData')
# )
# def get_country(clickData):
#     #code

# @app.callback(
#     Output("selected_year", "selected_year")
#     Input("IETS`")
# )
# def get_year(iets):


# @app.callback(
#     Output("dataframe")
#     Input("selected_country_ID", "selected_country")

# )
# def get_dataframe(selected_year, selected_country,):
#     sql = f"""

#         """
#     db._fetch_data(sql)


# @app.calllback(
#         Output("")
#         Input(Dataframe)
# )
# def update_choropleth():










app.layout = html.Div(children=[
    html.H1('Hello Dash!'),
    html.Div(className='row', children=[
        html.Div(className='col-8', children=[
            html.Div(f'GWH {selected_indicator} distribution in Europe for {selected_year}', className="GWH"),
            dcc.Graph(className="choropleth", id="choropleth", figure=update_choropleth(df))
        ]),
        html.Div('Lorem ipsum 2', className='col-4')
    ]),
     html.Div(className='row', children=[
         html.Div(className="col-6") 
    ])
])

if __name__ == '__main__':
    print("Started")
    app.run_server(debug=True, host="172.19.0.3", port=8080)
    # Casper: 172.19.0.3
    # Dagmar: 127.0.0.1
