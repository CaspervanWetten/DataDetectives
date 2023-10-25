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
temperature_df = pd.read_csv(r"dashboard\data\temperature.csv")
temperature_df['Date'] = pd.to_datetime(temperature_df['Date'])

# Function to convert alpha-2 country codes to alpha-3
def convert_alpha2_to_alpha3(alpha2_code):
    try:
        return pycountry.countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

# Apply the alpha-3 country codes
df['geo\TIME_PERIOD'] = df['geo\TIME_PERIOD'].apply(convert_alpha2_to_alpha3)

# Determine the minimum and maximum temperature in the dataset
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
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div(children=[
        dcc.Graph(id='bar-chart1'),
        dcc.Graph(id='bar-chart2'),
        dcc.Graph(id="combined-chart1"),
        dcc.Graph(id='combined-chart2')
    ], style={'width': '48%', 'display': 'inline-block'})
])

# Function to create an empty figure with a title
def create_empty_figure(title='Select a country in the choropleth to view data'):
    fig = go.Figure()
    fig.update_layout(title=title, showlegend=False)
    return fig

# Update the choropleth figure
@app.callback(
    Output('choropleth', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value')
)
def update_choropleth(selected_year, selected_month):
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

# Calculate the average temperature for each month
average_temperature_by_month = temperature_df.copy()  # Create a copy of the original data
average_temperature_by_month['Date'] = pd.to_datetime(average_temperature_by_month['Date'])

# Function to display the first bar chart
@app.callback(
    Output('bar-chart1', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value'),
    Input('choropleth', 'clickData')
)
def display_bar_chart(selected_year, selected_month, clickData):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']

        # Filter the electricity data for the selected year and country
        filtered_df = df[(df['Year'] == selected_year) & (df['indic'] == 'Consumption') & (df['geo\TIME_PERIOD'] == selected_country)]

        # Calculate the average monthly temperature for the selected country and year
        temperature_data_for_country = calculate_average_monthly_temperature(selected_country, selected_year)

        # Extract the months and corresponding average temperatures
        months = temperature_data_for_country.index
        temperatures = temperature_data_for_country.values

        # Create a subplot with two Y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add the primary bar chart for electricity consumption
        fig.add_trace(
            go.Bar(x=filtered_df['Month'], y=filtered_df['GWH'], name='GWH', marker_color='#08308e')
        )

        # Add the secondary line chart for temperature
        fig.add_trace(
            go.Scatter(x=months, y=temperatures, mode='lines+markers', name='Temperature', line=dict(color='#E7243B')),
            secondary_y=True
        )

        # Update the layout to display both Y-axes
        fig.update_layout(
            title=f'Electricity Consumption and Temperature in {selected_country} for year {selected_year}',
            xaxis=dict(title='Month'),
            yaxis=dict(title='GWH', side='left'),
            yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
            showlegend=True,
        )
    else:
        return create_empty_figure()

    return fig

# Function to display the second bar chart
@app.callback(
    Output('bar-chart2', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value'),
    Input('choropleth', 'clickData')
)
def display_bar_chart2(selected_year, selected_month, clickData):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']
    
        filtered_df_production = df[(df['Year'] == selected_year) & (df['indic'] == 'Production') & (df['geo\TIME_PERIOD'] == selected_country)]

        # Filter the temperature data for the selected country and year
        temperature_data_for_country = calculate_average_monthly_temperature(selected_country, selected_year)

        # Extract the months and corresponding average temperatures
        months = temperature_data_for_country.index
        temperatures = temperature_data_for_country.values

        fig = go.Figure()

        # Add the bar chart for energy production
        fig.add_trace(
            go.Bar(x=filtered_df_production['Month'], y=filtered_df_production['GWH'], name='Energy Production', marker_color='#08308e')
        )

        # Add the line chart for temperature
        fig.add_trace(
            go.Scatter(x=months, y=temperatures, mode='lines+markers', name='Temperature', line=dict(color='#E7243B'), yaxis='y2')
        )

        # Update the layout to display both Y-axes
        fig.update_layout(
            title=f'Energy Production and Temperature in {selected_country} for year {selected_year}',
            xaxis=dict(title='Month'),
            yaxis=dict(title='GWH', side='left'),
            yaxis2=dict(title='Temperature (°C)', side='right', overlaying='y', showgrid=False),
            showlegend=True,
        )
    
    else:
        return create_empty_figure()

    return fig

# Function to update the first combined chart
@app.callback(
    Output('combined-chart1', 'figure'),
    Input('choropleth', 'clickData')
)
def update_combined_chart(clickData):
    selected_country = ""
    if clickData is not None:
        selected_country = clickData['points'][0]['location']

        # Filter the GWH data for the selected country and years and sum GWH values for each year
        filtered_df = df[(df['indic'] == 'Consumption') & (df['geo\TIME_PERIOD'] == selected_country)]
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

        # Add the bar chart for normalized energy consumption
        bar_trace = go.Bar(
            x=gwh_by_year['Year'],
            y=gwh_by_year['GWH_normalized'],
            name='Normalized Energy Consumption',
            marker=dict(color='#08308e')
        )

        # Add the line chart for normalized population as a scatter plot on the same subplot
        line_trace = go.Scatter(
            x=population_data['Date'],
            y=population_data['Population_normalized'],
            mode='lines+markers',
            name='Normalized Population',
            marker=dict(color='#E7243B')
        )

        fig.add_trace(bar_trace)
        fig.add_trace(line_trace)

        fig.update_layout(
            title=f'Energy Consumption versus Population in {selected_country}',
            xaxis_title='Year',
            yaxis_title='Normalized Values (0-1)',
        )
    else:
        return create_empty_figure()

    return fig

# Function to update the second combined chart
@app.callback(
    Output('combined-chart2', 'figure'),
    Input('choropleth', 'clickData')
)
def update_combined_chart2(clickData):
    selected_country = ""
    if clickData is not None:
        selected_country = clickData['points'][0]['location']

        filtered_df_production = df[(df['indic'] == 'Production') & (df['geo\TIME_PERIOD'] == selected_country)]
        filtered_df_consumption = df[(df['indic'] == 'Consumption') & (df['geo\TIME_PERIOD'] == selected_country)]

        # Group and aggregate production and consumption data by year
        production_by_year = filtered_df_production.groupby('Year')['GWH'].sum().reset_index()
        consumption_by_year = filtered_df_consumption.groupby('Year')['GWH'].sum().reset_index()

        fig = make_subplots(rows=1, cols=1)

        # Add the bar chart for energy production
        production_trace = go.Bar(
            x=production_by_year['Year'],
            y=production_by_year['GWH'],
            name='Energy Production',
            marker=dict(color='#08308e')
        )

        # Add the bar chart for energy consumption
        consumption_trace = go.Bar(
            x=consumption_by_year['Year'],
            y=consumption_by_year['GWH'],
            name='Energy Consumption',
            marker=dict(color='#E7243B')
        )

        fig.add_trace(production_trace)
        fig.add_trace(consumption_trace)

        fig.update_layout(
            title=f'Energy Production and Consumption in {selected_country} Over the Years',
            xaxis_title='Year',
            yaxis_title='GWH',
        )
    else:
        return create_empty_figure()

    return fig

# Calculate the average monthly temperature for each month in the selected year
def calculate_average_monthly_temperature(selected_country, selected_year):
    # Filter the temperature data for the selected country and year
    temperature_data_for_country = average_temperature_by_month[
        (average_temperature_by_month['Country'] == selected_country) &
        (average_temperature_by_month['Date'].dt.year == selected_year)
    ]

    # Group the data by month and calculate the average temperature
    average_monthly_temperature = temperature_data_for_country.groupby(temperature_data_for_country['Date'].dt.month)['Temperature'].mean()

    return average_monthly_temperature

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=7767)
