import pandas as pd
import pycountry
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

# Load the CSV files for both electricity and population
df = pd.read_csv('dashboard\data\electricity.csv')
population_df = pd.read_csv('dashboard\data\population.csv')
population_df = population_df.sort_values(by=['country', 'Date'])

# Function to convert alpha-2 country codes to alpha-3
def convert_alpha2_to_alpha3(alpha2_code):
    try:
        return pycountry.countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

# Apply the alpha-3 country codes
df['geo\TIME_PERIOD'] = df['geo\TIME_PERIOD'].apply(convert_alpha2_to_alpha3)

# Determine the minimum and maximum GWH in the dataset
min_GWH = df['GWH'].min()
max_GWH = df['GWH'].max()

# Extract year and month from the date
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

app = dash.Dash(__name__)

# Initialize selected year and country
selected_year = df['Year'].min()
selected_country = ""  # Initialize to an empty string

# Get a list of available years
available_years = df['Year'].unique()

# Define the layout with two columns
app.layout = html.Div(children=[
    html.Div(children=[
        dcc.Graph(id='choropleth'),
        dcc.RadioItems(
            id='year-radio',
            options=[{'label': str(year), 'value': year} for year in available_years],
            value=selected_year,  # Default to the first year
        ),
        dcc.Slider(
            id='month-slider',
            marks={month: str(month) for month in range(1, 13)},
            step=None,
        ),
        dcc.Dropdown(
            id='data-type-dropdown',
            options=[
                {'label': 'Production', 'value': 'Production'},
                {'label': 'Consumption', 'value': 'Consumption'},
            ],
            value='Consumption',  # Default to Consumption
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div(children=[
        dcc.Graph(id='bar-chart1'),
        dcc.Graph(id='bar-chart2'),
        dcc.Graph(id="combined-chart1")
    ], style={'width': '48%', 'display': 'inline-block'})
])

@app.callback(
    Output('choropleth', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value'),
)
def update_figure(selected_year, selected_month):
    filtered_df = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

    # Compute the minimum and maximum GWH values for the selected month from filtered_df
    min_GWH = filtered_df['GWH'].min()
    max_GWH = filtered_df['GWH'].max()

    fig = px.choropleth(filtered_df,
                        locations="geo\TIME_PERIOD",
                        color="GWH",
                        hover_name="geo\TIME_PERIOD",
                        color_continuous_scale='Viridis'
                        )

    fig.update_geos(
        visible=True, resolution=50, scope="europe",
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Blue"
    )

    fig.update_layout(
        title={
            'text': f'GWH distribution in Europe for month {selected_month} and year {selected_year}',
            'x': 0.5,
            'y': 0.98
        },
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        height=1000, margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

@app.callback(
    Output('bar-chart1', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value'),
    Input('choropleth', 'clickData'),
    Input('data-type-dropdown', 'value')  # Add this input
)
def display_bar_chart(selected_year, selected_month, clickData, data_type):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']

    # Filter the DataFrame based on the selected data type
    filtered_df = df[(df['Year'] == selected_year) & (df['indic'] == data_type) & (df['geo\TIME_PERIOD'] == selected_country)]

    fig = px.bar(filtered_df, x='Month', y='GWH', title=f'Electricity {data_type} in {selected_country} for year {selected_year}')

    return fig

@app.callback(
    Output('combined-chart1', 'figure'),
    Input('choropleth', 'clickData'),
    Input('data-type-dropdown', 'value')  # Add this input
)
def update_combined_chart(clickData, data_type):
    selected_country = ""
    if clickData is not None:
        selected_country = clickData['points'][0]['location']

    # Filter the DataFrame based on the selected data type
    filtered_df = df[(df['indic'] == data_type) & (df['geo\TIME_PERIOD'] == selected_country)]
    gwh_by_year = filtered_df.groupby('Year')['GWH'].sum().reset_index()

    # Filter the population data for the selected country and years
    population_data = population_df[population_df['country'] == selected_country]

    # Normalize the GWH data between 0 and 1
    max_gwh = gwh_by_year['GWH'].max()
    min_gwh = gwh_by_year['GWH'].min()
    gwh_by_year['GWH_normalized'] = (gwh_by_year['GWH'] - min_gwh) / (max_gwh - min_gwh)

    # Normalize the population data between 0 and 1
    max_population = population_data['Population'].max()
    min_population = population_data['Population'].min()
    population_data['Population_normalized'] = (population_data['Population'] - min_population) / (max_population - min_population)

    fig = make_subplots(rows=1, cols=1)

    # Add the bar chart for normalized energy consumption or production
    bar_trace = go.Bar(
        x=gwh_by_year['Year'],
        y=gwh_by_year['GWH_normalized'],
        name=f'Normalized Electricity {data_type}'
    )

    # Add the line chart for normalized population as a scatter plot on the same subplot
    line_trace = go.Scatter(
        x=population_data['Date'],
        y=population_data['Population_normalized'],
        mode='lines+markers',
        name='Normalized Population',
    )

    fig.add_trace(bar_trace)
    fig.add_trace(line_trace)

    fig.update_layout(
        title=f'Normalized Electricity {data_type} and Population in {selected_country}',
        xaxis_title='Year',
        yaxis_title='Normalized Values (0-1)',
    )

    return fig

if __name__ == '__main__':
    print("ga")
    app.run_server(debug=True, host='127.0.0.1', port=7768)
