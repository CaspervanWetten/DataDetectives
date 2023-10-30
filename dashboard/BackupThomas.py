import pandas as pd
import pycountry
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots 
import eurostat as es

# Load the CSV files for both electricity and population
electricity_df = pd.read_csv('dashboard\data\electricity.csv')
population_df = pd.read_csv('dashboard\data\population.csv')  
population_df = population_df.sort_values(by=['Country', 'Date'])
temperature_df = pd.read_csv(r"dashboard\data\temperature.csv")
temperature_df['Date'] = pd.to_datetime(temperature_df['Date'])


# Function to convert alpha-2 Country codes to alpha-3
def convert_alpha2_to_alpha3(alpha2_code):
    try:
        return pycountry.countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

# Apply the alpha-3 Country codes
electricity_df['Country'] = electricity_df['Country'].apply(convert_alpha2_to_alpha3)

# Determine the minimum and maximum temperature in the dataset
min_GWH = electricity_df['GWH'].min()
max_GWH = electricity_df['GWH'].max()

# Extract year and month from the date
electricity_df['Date'] = pd.to_datetime(electricity_df['Date'])
electricity_df['Year'] = electricity_df['Date'].dt.year
electricity_df['Month'] = electricity_df['Date'].dt.month

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize selected year and Country
selected_year = electricity_df['Year'].min()
selected_Country = ""  # Initialize to an empty string

# Get a list of available years
available_years = electricity_df['Year'].unique()











def TypesOfEnergy():
    try: 
        df = es.get_data_df("ten00122")
        df.drop(columns=['freq','nrg_bal','unit'], inplace=True)
        return df
    except Exception as e:
        return f"quit with {e} as error"

df2 = TypesOfEnergy()
df2.fillna(0, inplace=True)
#change column name to country and also energy_kind
df2 = df2.rename(columns={'geo\\TIME_PERIOD': 'country'})
df2 = df2.rename(columns={'siec': 'energy'})

belgiumdf = df2[df2['country'] == 'AL']
unique_values = belgiumdf['energy'].unique()

#remap all energy values 
unique_energy_values = df2['energy'].unique()

# Define a mapping of old values to new values
value_mapping = {
    'C0000X0350-0370': 'Solid fossil fuels',
    'C0350-0370': 'Manufactured gases',
    'P1000': 'Peat and peat products',
    'S2000': 'Oil shale and oil sands',
    'O4000XBIO': 'Oil and petroleum products (excluding biofuel portion)',
    'G3000': 'Natural gas',
    'RA000': 'Renewables and biofuels',
    'W6100_6220': 'Non-renewable waste',
    'N900H': 'Nuclear heat',
    'H8000': 'Heat',
    'E7000': 'Electricity',
    'TOTAL': 'Total'
}
# Replace the values in the DataFrame
df2['energy'] = df2['energy'].replace(value_mapping)

#remove the total attribute for our plots
df2 = df2[df2['energy'] != 'Total']
df_pivot = df2.melt(id_vars=['energy', 'country'], var_name='year', value_name='consumption')
grouped = df_pivot.groupby(['energy', 'year'])['consumption'].sum().unstack()
energy_groups = df2.groupby('energy')
print(df2.head())
#Land selectie toevoegen===========================================================================================================================================================





























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
            id='indic-dropdown',
            options=[{'label': indic, 'value': indic} for indic in electricity_df['indic'].unique()],
            value=electricity_df['indic'].unique()[0],
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
        )
        
        
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div(children=[
        dcc.Graph(id='bar-chart1'),
        dcc.Graph(id='bar-chart2'),
        dcc.Graph(id="combined-chart1"),
        dcc.Graph(id='combined-chart2'),
        dcc.Graph(id='energy-pie-chart'),
        dcc.Dropdown(
        id='year-dropdown',
        options=[
            {'label': year, 'value': year}
            for year in df2.columns if year.isnumeric()
        ],
        value='2011'
        )
    ], style={'width': '48%', 'display': 'inline-block'})
])

# Function to create an empty figure with a title
def create_empty_figure(title='Select a Country in the choropleth to view data'):
    fig = go.Figure()
    fig.update_layout(title=title, showlegend=False)
    return fig

# Calculate GWH per capita
def calculate_gwh_per_capita(electricity_df, population_df, selected_year, selected_month, selected_indic):
    # Filter the electricity data
    filtered_electricity = electricity_df[(electricity_df['Year'] == selected_year) &
                              (electricity_df['Month'] == selected_month) &
                              (electricity_df['indic'] == selected_indic)]
    
    # Filter the population data
    filtered_population = population_df[(population_df['Date'] == selected_year)]
    
    # Merge the filtered datasets on the 'Country' column
    merged_data = pd.merge(filtered_electricity, filtered_population, on='Country', how='left')
    
    # Calculate GWH per capita
    merged_data['GWH_per_capita'] = merged_data['GWH'] / merged_data['Population']
    
    return merged_data

def calculate_total_gwh(electricity_df, selected_year, selected_month, selected_indic):
    filtered_df = electricity_df[(electricity_df['Year'] == selected_year) &
                     (electricity_df['Month'] == selected_month) &
                     (electricity_df['indic'] == selected_indic)]
    
    total_gwh = filtered_df['GWH'].sum()
    
    return total_gwh


# Update the choropleth figure
@app.callback(
    Output('choropleth', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value'),
    Input('indic-dropdown', 'value'),
    Input('display-mode-dropdown', 'value')
)
def update_choropleth(selected_year, selected_month, selected_indic, display_mode):
    if display_mode == 'total':
        filtered_df = electricity_df[(electricity_df['Year'] == selected_year) &
                         (electricity_df['Month'] == selected_month) &
                         (electricity_df['indic'] == selected_indic)]
        total_gwh = calculate_total_gwh(electricity_df, selected_year, selected_month, selected_indic)
    else:
        # Calculate GWH per capita
        merged_data = calculate_gwh_per_capita(electricity_df, population_df, selected_year, selected_month, selected_indic)
        filtered_df = merged_data
        
        total_gwh = 0  # You can set a default value here

    fig = px.choropleth(filtered_df, 
                        locations="Country", 
                        color='GWH' if display_mode == 'total' else 'GWH_per_capita',
                        hover_name="Country",
                        color_continuous_scale="Emrld"
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
    selected_Country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_Country = clickData['points'][0]['location']

        # Filter the electricity data for the selected year and Country
        filtered_df = electricity_df[(electricity_df['Year'] == selected_year) & (electricity_df['indic'] == 'Consumption') & (electricity_df['Country'] == selected_Country)]

        # Calculate the average monthly temperature for the selected Country and year
        temperature_data_for_Country = calculate_average_monthly_temperature(selected_Country, selected_year)

        # Extract the months and corresponding average temperatures
        months = temperature_data_for_Country.index
        temperatures = temperature_data_for_Country.values

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
            title=f'Electricity Consumption and Temperature in {selected_Country} for year {selected_year}',
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
    selected_Country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_Country = clickData['points'][0]['location']
    
        filtered_df_production = electricity_df[(electricity_df['Year'] == selected_year) & (electricity_df['indic'] == 'Production') & (electricity_df['Country'] == selected_Country)]

        # Filter the temperature data for the selected Country and year
        temperature_data_for_Country = calculate_average_monthly_temperature(selected_Country, selected_year)

        # Extract the months and corresponding average temperatures
        months = temperature_data_for_Country.index
        temperatures = temperature_data_for_Country.values

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
            title=f'Energy Production and Temperature in {selected_Country} for year {selected_year}',
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
    selected_Country = ""
    if clickData is not None:
        selected_Country = clickData['points'][0]['location']

        # Filter the GWH data for the selected Country and years and sum GWH values for each year
        filtered_df = electricity_df[(electricity_df['indic'] == 'Consumption') & (electricity_df['Country'] == selected_Country)]
        gwh_by_year = filtered_df.groupby('Year')['GWH'].sum().reset_index()

        # Filter the population data for the selected Country and years
        population_data = population_df[population_df['Country'] == selected_Country]

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
            title=f'Energy Consumption versus Population in {selected_Country}',
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
    selected_Country = ""
    if clickData is not None:
        selected_Country = clickData['points'][0]['location']

        filtered_df_production = electricity_df[(electricity_df['indic'] == 'Production') & (electricity_df['Country'] == selected_Country)]
        filtered_df_consumption = electricity_df[(electricity_df['indic'] == 'Consumption') & (electricity_df['Country'] == selected_Country)]

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
            title=f'Energy Production and Consumption in {selected_Country} Over the Years',
            xaxis_title='Year',
            yaxis_title='GWH',
        )
    else:
        return create_empty_figure()

    return fig

# Calculate the average monthly temperature for each month in the selected year
def calculate_average_monthly_temperature(selected_Country, selected_year):
    # Filter the temperature data for the selected Country and year
    temperature_data_for_Country = average_temperature_by_month[
        (average_temperature_by_month['Country'] == selected_Country) &
        (average_temperature_by_month['Date'].dt.year == selected_year)
    ]

    # Group the data by month and calculate the average temperature
    average_monthly_temperature = temperature_data_for_Country.groupby(temperature_data_for_Country['Date'].dt.month)['Temperature'].mean()

    return average_monthly_temperature





# Define a callback function to update the pie chart based on the selected year
@app.callback(
    Output('energy-pie-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_pie_chart(selected_year):
    fig = px.pie(df2, names='energy', values=selected_year, title=f'Energy Source Distribution in {selected_year}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=7767)

