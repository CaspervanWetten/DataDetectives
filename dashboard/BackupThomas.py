import pandas as pd
import pycountry
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Load the CSV file
df = pd.read_csv('dashboard\data\electricity.csv')

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
        dcc.Graph(id='bar-chart2')
    ], style={'width': '48%', 'display': 'inline-block'})
])


@app.callback(
    Output('choropleth', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value')
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
    Input('choropleth', 'clickData')
)
def display_bar_chart(selected_year, selected_month, clickData):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']
    
    filtered_df = df[(df['Year'] == selected_year) & (df['indic'] == 'Consumption') & (df['geo\TIME_PERIOD'] == selected_country)]

    fig = px.bar(filtered_df, x='Month', y='GWH', title=f'Electricity Consumption in {selected_country} for year {selected_year}')

    return fig

@app.callback(
    Output('bar-chart2', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value'),
    Input('choropleth', 'clickData')
)
def display_bar_chart(selected_year, selected_month, clickData):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']
    
    filtered_df = df[(df['Year'] == selected_year) & (df['indic'] == 'Production') & (df['geo\TIME_PERIOD'] == selected_country)]

    fig = px.bar(filtered_df, x='Month', y='GWH', title=f'Electricity Production in {selected_country} for year {selected_year}')

    return fig


print("123")
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=7767)
