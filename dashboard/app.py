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

ec_df = db._fetch_data("SELECT * FROM electricity_consumption")
et_df = db._fetch_data("SELECT * FROM electricity_types")
pop_df = db._fetch_data("SELECT * FROM population")
tmp_df = db._fetch_data("SELECT * FROM temperature")

pop_df['year'] = pop_df['year'].astype(int) # CRACK CODE
db._load_data(population = pop_df)

print(ec_df.head(2))
print(et_df.head(2))
print(pop_df.head(2))
print(tmp_df.head(2))



df = db._fetch_data("electricity_consumption", "country", "gwh", year="=2010")
available_years = sorted(db._fetch_data("electricity_consumption", "year", distinct=True), key=int)
selected_year = 2018
selected_indicator = "consumption"

@app.callback(
    Output('selected_country_id', 'selected_country'),
    Input('choropleth', 'clickData')
)
def get_country(clickData):
    selected_Country = "" 
    if clickData is not None:
        selected_Country = clickData['points'][0]['location']
    return selected_Country






app.layout = html.Div(children=[
    html.H1('Hello Dash!'),
    html.Div(className='row', children=[
        html.Div(className='col-8', children=[
            html.Div(f'GWH {selected_indicator} distribution in Europe for {selected_year}', className="GWH"),
            dcc.Graph(className="choropleth", id="choropleth")
        ]),
        html.Div('Lorem ipsum 2', className='col-4')
    ]),
     html.Div(className='row', children=[
         html.Div(className="col-6", children=[
            dcc.RadioItems(
                id='year-radio',
                options=[{'label': str(year), 'value': year} for year in available_years],
                value=selected_year,  # Default to the first year
        ),
            dcc.Dropdown(
                id='indic-dropdown',
                options=[{'label': indic, 'value': indic} for indic in ec_df['indicator'].unique()],
                value=ec_df['indicator'].unique()[0],
                style={'width': '100%'}
        ),
            dcc.Dropdown(
                id='display-mode-dropdown',
                options=[
                    {'label': 'Total GWH', 'value': 'total'},
                    {'label': 'GWH per capita', 'value': 'per_capita'},
                ],
                value='total',  # Default to 'Total GWH'
                style={'width': '100%'}
        ),
         ]) 
    ])
])

if __name__ == '__main__':
    print("Started")
    app.run_server(debug=True, host="172.19.0.3", port=8080)
    # Casper: 172.19.0.3
    # Dagmar: 127.0.0.1
