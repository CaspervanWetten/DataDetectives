import dash
import pycountry
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from Predictions import generate_fig
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots 
from Database import Database
from time import sleep

def convert_alpha3_full_name(alpha3_code):
    try:
        return pycountry.countries.get(alpha_3=alpha3_code).name
    except Exception as e:
        print(e)
        return ""


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

def create_empty_figure(title='Select a Country in the choropleth to view data'):
    fig = go.Figure()
    fig.update_layout(title='Select a Country in the choropleth to view data', showlegend=False)
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
    sleep(0.2)
    fig = px.choropleth(df, 
                        locations="country", 
                        color='gwh',
                        hover_name="country",
                        color_continuous_scale="Emrld",
                        scope="europe",
                        #range_color='gwh',
                        title=f"{indicator} for {year} and {display}"
                        )

    fig.update_geos(
        visible=True, resolution=50,
        showcountries=True, countrycolor="Black",
        fitbounds="locations",
        center=dict(lat=51.1657, lon=10.4515),
        projection_scale=15,
        oceancolor='rgba(0,0,255,1)'       
    )
    #TODO Add display check to change title
    fig.update_layout(
        autosize=True,
        geo=dict(
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        title= f'GWH {indicator} in Europe for the month {month} in the year {year}',
        dragmode=False,
        # plot_bgcolor='rgba(39, 41, 83, 1)',
        # paper_bgcolor='rgba(39, 41, 83, 1)',
        width=1800, 
        height=700
        )

    return fig

@app.callback(
    Output('bar-chart-energy-population', 'figure'),
    [Input('country', 'children')]
)
def update_bar_chart_energy_population(country):
    if not country:
        return create_empty_figure("Select a Country to Display Data")

    # Fetch electricity consumption data for the selected country for all years
    sql_energy_consumption = f"""
        SELECT year, SUM(gwh) AS total_consumption
        FROM electricity_consumption
        WHERE country='{country}'
        GROUP BY year
    """
    consumption_data = db._fetch_data(sql_energy_consumption)
    sleep(0.5)

    # Fetch population data for the selected country for all years from the population dataset
    sql_population = f"""
        SELECT year, population
        FROM population
        WHERE country='{country}'
        
    """
    population_data = db._fetch_data(sql_population)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=consumption_data['year'], y=consumption_data['total_consumption'], name='Total Consumption (GWh)', marker_color='#08308e'))
    
    fig.add_trace(go.Scatter(x=population_data['year'], y=population_data['population'], mode='lines+markers', name='Population', line=dict(color='#E7243B'), marker=dict(size=8), yaxis='y2'))
    country = convert_alpha3_full_name(country)
    fig.update_layout(
        title=f'Electricity Consumption and Population in {country} for All Years',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Total Consumption (GWh)', side='left'),
        yaxis2=dict(title='Total Population', side='right', overlaying='y', showgrid=False),
        showlegend=True,
    )

    return fig

@app.callback(
    Output('predicted', 'figure'),
    [Input('indic-dropdown', 'value'),
    Input('country', 'children'),
    Input('display-mode-dropdown', 'value')]
)
def update_predicted(indicator, country, display):
    if country == "":
        return create_empty_figure("")
    sql = f"""
        SELECT * 
        FROM {display}
        WHERE country = '{country}' AND indicator = '{indicator}'
        """
    df = db._fetch_data(sql)
    sleep(0.5)
    
    results = generate_fig(df)
    country = convert_alpha3_full_name(country)
    display_dict = {
        "energy_capita" : "Electricity consumption per capita",
        "electricity_consumption" : "Electricity"
    }
    # print(df.head(35))
    display = display_dict[display]
    fig = px.line(results, x = "DATE",y ="gwh", color = "predict", title=f"Prediction of the {display} {indicator} for {country} for the coming year" )
    return fig

@app.callback(
    Output('bar-chart-consumption-temp', 'figure'),
    [Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value'),
    Input('country', 'children')]
)
def update_bar_energy_temperature_consumption(year, display, country):
    if country == "":
        return create_empty_figure("")
    sql_energy = f"""
            SELECT e.country, e.month, e.gwh FROM {display} as e
            WHERE e.year='{year}' AND e.indicator = 'Consumption' AND e.country='{country}'
            """
 
    sql_temp = f"""
            SELECT t.country, t.month, t.temperature FROM temperature as t
            WHERE t.year='{year}' AND t.country='{country}'
            """
    df_temp = db._fetch_data(sql_temp)
    df_energy = db._fetch_data(sql_energy)
    sleep(0.5)
 
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df_energy['month'], y=df_energy['gwh'], name='GWH', marker_color='#08308e',text=df_energy['gwh'],textposition='inside',textangle=0))
    fig.add_trace(go.Scatter(x=df_temp['month'], y=df_temp['temperature'], mode='lines+markers', name='Temperature', line=dict(color='#E7243B'), yaxis='y2'))
    country = convert_alpha3_full_name(country)
    fig.update_layout(
        title=f'Electricity Consumption and Temperature in {country} for year {year}',
        xaxis=dict(title='Month'),
        yaxis=dict(title='GWH', side='left'),
        yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
        showlegend=True,
    )
    
    return fig


@app.callback(
    Output('bar-chart-production-temp', 'figure'),
    [Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value'),
    Input('country', 'children')]
)
def update_bar_energy_temperature_production(year, display, country):
    if country == "":
        return create_empty_figure("")
    sql_energy = f"""
            SELECT e.country, e.month, e.gwh FROM {display} as e
            WHERE e.year='{year}' AND e.indicator = 'Production' AND e.country='{country}'
            """
 
    sql_temp = f"""
            SELECT t.country, t.month, t.temperature FROM temperature as t
            WHERE t.year='{year}' AND t.country='{country}'
            """
    df_temp = db._fetch_data(sql_temp)
    df_energy = db._fetch_data(sql_energy)
    sleep(0.5)
 
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df_energy['month'], y=df_energy['gwh'], name='GWH', marker_color='#08308e',text=df_energy['gwh'],textposition='inside',textangle=0))
    fig.add_trace(go.Scatter(x=df_temp['month'], y=df_temp['temperature'], mode='lines+markers', name='Temperature', line=dict(color='#E7243B'), yaxis='y2'))
    country = convert_alpha3_full_name(country)
    fig.update_layout(
        title=f'Electricity Production and Temperature in {country} for year {year}',
        xaxis=dict(title='Month'),
        yaxis=dict(title='GWH', side='left'),
        yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
        showlegend=True,
    )
    
    return fig


@app.callback(
    Output('bar-chart-import-temp', 'figure'),
    [Input('year-radio', 'value'),
    Input('display-mode-dropdown', 'value'),
    Input('country', 'children')]
)
def update_bar_energy_temperature_imports(year, display, country):
    if country == "":
        return create_empty_figure("")
    sql_energy = f"""
            SELECT e.country, e.month, e.gwh FROM {display} as e
            WHERE e.year='{year}' AND e.indicator = 'Imports' AND e.country='{country}'
            """
 
    sql_temp = f"""
            SELECT t.country, t.month, t.temperature FROM temperature as t
            WHERE t.year='{year}' AND t.country='{country}'
            """
    df_temp = db._fetch_data(sql_temp)
    df_energy = db._fetch_data(sql_energy)
    sleep(0.5)
 
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df_energy['month'], y=df_energy['gwh'], name='GWH', marker_color='#08308e',text=df_energy['gwh'],textposition='inside',textangle=0))
    fig.add_trace(go.Scatter(x=df_temp['month'], y=df_temp['temperature'], mode='lines+markers', name='Temperature', line=dict(color='#E7243B'), yaxis='y2'))
    country = convert_alpha3_full_name(country)
    fig.update_layout(
        title=f'Electricity Imports and Temperature in {country} for year {year}',
        xaxis=dict(title='Month'),
        yaxis=dict(title='GWH', side='left'),
        yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
        showlegend=True,
    )
    
    return fig


@app.callback(
    Output('bar-chart-production-vs-consumption', 'figure'),
    [Input('year-radio', 'value'),
     Input('display-mode-dropdown', 'value'),
     Input('country', 'children')]
)
def update_production_vs_consumption(year, display, country):
    if country == "":
        return create_empty_figure("")
    
    sql_production_consumption = f"""
        SELECT e.country, e.indicator, e.month, e.gwh FROM {display} as e
        WHERE e.year='{year}' AND e.indicator IN ('Production', 'Consumption') AND e.country='{country}'
        """
    df_production_consumption = db._fetch_data(sql_production_consumption)
    sleep(0.5)

    country = convert_alpha3_full_name(country)
    fig = px.bar(
    data_frame=df_production_consumption,
    x="month",
    y="gwh",
    color="indicator",
    barmode="group",
    color_continuous_scale="Emrld",
    title=f'Electricity Production vs. Consumption in {country} for year {year}',
    labels={"month": "Month", "gwh": "GWH"},
    range_color="Emrld",
    color_discrete_map={
        "Production": "#08308e",
        "Consumption": "#E7243B"
    }
    )

    return fig

#custom made color scale
indicator_colors = {
    'Solid fossil fuels': 'rgb(25, 25, 112)',  # Midnight Blue
    'Manufactured gases': 'rgb(0, 0, 128)',  # Navy
    'Peat and peat products': 'rgb(0, 0, 205)',  # Medium Blue
    'Oil shale and oil sands': 'rgb(0, 0, 255)',  # Blue
    'Oil and petroleum products (excluding biofuel portion)': 'rgb(70, 130, 180)',  # Steel Blue
    'Natural gas': 'rgb(100, 149, 237)',  # Cornflower Blue
    'Renewables and biofuels': 'rgb(135, 206, 235)',  # Sky Blue
    'Non-renewable waste': 'rgb(106, 90, 205)',  # Slate Blue
    'Nuclear heat': 'rgb(123, 104, 238)',  # Medium Slate Blue
    'Heat': 'rgb(147, 112, 219)',  # Medium Purple
    'Electricity': 'rgb(138, 43, 226)'  # Blue Violet
}


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('year-radio', 'value'),
     Input('country', 'children'),
     Input('indicator-checkboxes', 'value')]
)
def update_pie_chart(year, country, selected_indicators):
    if country == "":
        return create_empty_figure("")
    sql = f"""
        SELECT indicator, ktoe
        FROM electricity_types
        WHERE year='{year}' AND country='{country}'
        """
    data = db._fetch_data(sql)
    filtered_data = data[data['indicator'].isin(selected_indicators)]
    country = convert_alpha3_full_name(country)
    fig = px.pie(
        filtered_data,
        names='indicator',
        values='ktoe',
        title=f'Electricity Type Distribution in {country} for the year {year}',
        color='indicator',  
        color_discrete_map=indicator_colors 
    )
    if selected_indicators == []:
        fig = px.pie(
        title=f'There is no detailed source breakdown available for {country} in {year}',
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

@app.callback(
    Output('indicator-checkboxes', "value"),
    [Input('year-radio', 'value'),
     Input('country', 'children'),]
)
def get_used_sources(year, country):
    sql = f"""
        SELECT indicator, ktoe
        FROM electricity_types
        WHERE year='{year}' AND country='{country}'
        """
    data = db._fetch_data(sql)
    options = data[data['ktoe'] != 0]['indicator'].unique().tolist()
    if "Total" in options:
        options.remove("Total")
    return options

@app.callback(
    Output('average-consumption-change', 'children'),
    [Input('year-radio', 'value'),
     Input('country', 'children')]
)
def update_average_consumption_change(year, country):
    if country == "":
        return ""

    sql_consumption_current = f"""
        SELECT SUM(gwh) as total_consumption
        FROM electricity_consumption
        WHERE year = '{year}' AND indicator='Consumption' AND country='{country}'
    """
    consumption_current = db._fetch_data(sql_consumption_current).iloc[0]
 
    sql_consumption_previous = f"""
        SELECT SUM(gwh) as total_consumption
        FROM electricity_consumption
        WHERE year = '{int(year) - 1}' AND indicator='Consumption' AND country='{country}'
    """
    consumption_previous = db._fetch_data(sql_consumption_previous).iloc[0]

    change = (consumption_current - consumption_previous) / consumption_previous * 100
    sleep(0.5)

    return f'Change in consumption for {year} vs. previous year: {change:.2f}%'


@app.callback(
    Output('average-production-change', 'children'),
    [Input('year-radio', 'value'),
     Input('country', 'children')]
)
def update_average_production_change(year, country):
    if country == "":
        return ""

    sql_production_current = f"""
        SELECT SUM(gwh) as total_production
        FROM electricity_consumption
        WHERE year = '{year}' AND indicator='Production' AND country='{country}'
    """
    production_current = db._fetch_data(sql_production_current).iloc[0]

    sql_production_previous = f"""
        SELECT SUM(gwh) as total_production
        FROM electricity_consumption
        WHERE year = '{int(year) - 1}' AND indicator='Production' AND country='{country}'
    """
    production_previous = db._fetch_data(sql_production_previous).iloc[0]

    change = (production_current - production_previous) / production_previous * 100

    return f'Change in production for {year} vs. previous year: {change:.2f}%'

@app.callback(
    Output('average-import-change', 'children'),
    [Input('year-radio', 'value'),
     Input('country', 'children')]
)
def update_average_import_change(year, country):
    if country == "":
        return ""

    sql_import_current = f"""
        SELECT SUM(gwh) as total_import
        FROM electricity_consumption
        WHERE year = '{year}' AND indicator='Imports' AND country='{country}'
    """
    import_current = db._fetch_data(sql_import_current).iloc[0]

    sql_import_previous = f"""
        SELECT SUM(gwh) as total_import
        FROM electricity_consumption
        WHERE year = '{int(year) - 1}' AND indicator='Imports' AND country='{country}'
    """
    import_previous = db._fetch_data(sql_import_previous).iloc[0]


    change = (import_current - import_previous) / import_previous * 100

    return f'Change in imports for {year} vs. previous year: {change:.2f}%'



app.layout = html.Div(children=[
    html.H1('Data Detectives Dashboard'),
    html.Div(className='row', children=[
        html.Div(className='col', children=[
            html.Br(),
            dcc.Loading(id="loading-choro", type="default", children=dcc.Graph(id="choropleth", className="choropleth", figure=update_choropleth(indicator, month, year, display_choro)))]),     
        ]),
    html.Nav(className="navbar sticky-top bg-dark", children=[
                dcc.Slider(
                        id='year-radio',
                        min=min(available_years),
                        max=max(available_years),
                        marks={int(year) : str(year) for year in available_years},
                        value=year,
                        step=1,
                        className='selectors navbar-improved'),
                        ]),
     html.Div(className='row', children=[
        html.Div(className="col-12", children=[
            dcc.Slider(
                id='month-slider',
                marks={month: str(month) for month in range(1, 13)},
                step=1,
                value = 6,
                className='selectors'
             ),
            dcc.Dropdown(
                id='indic-dropdown',
                options=[{'label': indic, 'value': indic} for indic in ec_df['indicator'].unique()],
                value=ec_df['indicator'].unique()[0],
                searchable=False,
                className='selectors'
            ),
            dcc.Dropdown(
                id='display-mode-dropdown',
                options=[
                    {'label': 'Total GWH', 'value': 'electricity_consumption'},
                    {'label': 'GWH per capita', 'value': 'energy_capita'},
                ],
                value='electricity_consumption',
                searchable=False,
                className='selectors'
            ),
            html.Div(id="country-container", children=[
                'You have selected:',
                html.Div(id='country')
            ]),
            html.Div(id='average-consumption-change', className='text-display'),html.Div(id='average-production-change', className='text-display'),
            html.Div(id='average-import-change', className='text-display')
        ])
    ]),
    html.Div(className='row', children=[
        html.Div(className='col-6', children=[
            html.Br(),
            dcc.Loading(id="loading-bar-1", type="default", children=dcc.Graph(id='bar-chart-energy-population', className="bars")),
            html.Br(),
            dcc.Loading(id="loading-bar-3", type="default", children=dcc.Graph(id='bar-chart-production-temp', className="bars")),
            html.Br(),
            dcc.Loading(id="loading-bar-5", type="default", children=dcc.Graph(id='bar-chart-production-vs-consumption', className="bars")),
            dcc.Checklist(id='indicator-checkboxes',)
        ]),
        html.Div(className='col-6', children=[
            html.Br(),
            dcc.Loading(id="loading-bar-2", type="default", children=dcc.Graph(id='bar-chart-consumption-temp', className="bars")),
            html.Br(),
            dcc.Loading(id="loading-bar-4", type="default", children=dcc.Graph(id='bar-chart-import-temp', className="bars")),
            html.Br(),
            dcc.Loading(id="loading-pie-chart", type="default", children=dcc.Graph(id='pie-chart', className="bars"))
        ])
    ]),
    html.Div(className='row', children=[
        html.Hr(),
        dcc.Loading(dcc.Graph(id='predicted', className='bars'))
    ])
])

if __name__ == '__main__':
    print("Started")
    app.run_server(debug=True, host="172.19.0.3", port=8080)
    # Casper: 172.19.0.3
    # Thomas: 127.0.0.1:8080
    # Alle andere: 127.0.0.1



   