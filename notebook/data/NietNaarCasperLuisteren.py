import pandas as pd
import pycountry
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Load the CSV file
df = pd.read_csv('notebook\data\TemperatureData.csv')

# Function to convert alpha-2 country codes to alpha-3
def convert_alpha2_to_alpha3(alpha2_code):
    try:
        return pycountry.countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        print(f"Kan de code niet vinden: {alpha2_code}")
        return None

# Apply the alpha-3 country codes
df['Country'] = df['Country'].apply(convert_alpha2_to_alpha3)

# Determine the minimum and maximum temperature in the dataset
min_temp = df['Temperature'].min()
max_temp = df['Temperature'].max()
df['Date'] = pd.to_datetime(df['Date'])

# Extract year and month from the date
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

app = dash.Dash(__name__)

# Initialize selected year and country
selected_year = df['Year'].min()
selected_country = ""  # Initialize to an empty string

# Get a list of available years
available_years = df['Year'].unique()

# Define the layout using Bootstrap and HTML
app.layout = html.Div([
    # Create a Bootstrap row
    html.Div([
        # Left column (Choropleth map)
        html.Div([
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
        ], className='col-md-6'),  # Bootstrap class for a 6-column width

        # Right column (Other plots)
        html.Div([
            dcc.Graph(id='pie-chart'),
            dcc.Graph(id='histogram'),
            dcc.Graph(id='line-chart'),
        ], className='col-md-6'),  # Bootstrap class for a 6-column width
    ], className='row'),  # Bootstrap class for a row
])

@app.callback(
    Output('month-slider', 'min'),
    Output('month-slider', 'max'),
    Output('month-slider', 'value'),
    Input('year-radio', 'value')
)
def update_slider(selected_year):
    min_month = df[df['Year'] == selected_year]['Month'].min()
    max_month = df[df['Year'] == selected_year]['Month'].max()
    initial_month = min_month
    return min_month, max_month, initial_month

@app.callback(
    Output('choropleth', 'figure'),
    Input('year-radio', 'value'),
    Input('month-slider', 'value')
)
def update_figure(selected_year, selected_month):
    filtered_df = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

    fig = px.choropleth(filtered_df, 
                        locations="Country", 
                        color="Temperature", 
                        hover_name="Country", 
                        color_continuous_scale='Viridis',  
                        range_color=(min_temp, max_temp))

    fig.update_geos(
        visible=True, resolution=50, scope="europe",
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Blue"
    )

    fig.update_layout(
        title={
            'text': f'Temperatuurverdeling in Europa voor maand {selected_month} en jaar {selected_year}',
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
    Output('pie-chart', 'figure'),
    Input('choropleth', 'clickData'),
    Input('year-radio', 'value')
)
def display_pie_chart(clickData, selected_year):
    if clickData is None:
        fig = go.Figure(data=[go.Pie()])
        fig.update_layout(
            title=f'Klik op een land op de kaart om de meest nutteloze visualisatie te zien!!'
        )
    else:
        selected_country = clickData['points'][0]['location']
        fig = go.Figure(data=[go.Pie(labels=[selected_country], values=[1])])
        fig.update_layout(
            title=f'Verdeling van {selected_country} in het jaar {selected_year}'
        )
    return fig

@app.callback(
    Output('histogram', 'figure'),
    Input('year-radio', 'value'),
    Input('choropleth', 'clickData')
)
def display_histogram(selected_year, clickData):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']
    filtered_df = df[(df['Year'] == selected_year) & (df['Country'] == selected_country)]
    fig = px.histogram(filtered_df, x='Month', y='Temperature', color='Year', title=f'Temperatuur histogram voor {selected_country} in het jaar {selected_year}')
    return fig

@app.callback(
    Output('line-chart', 'figure'),
    Input('year-radio', 'value'),
    Input('choropleth', 'clickData')
)
def display_line_chart(selected_year, clickData):
    selected_country = ""  # Initialize to an empty string
    if clickData is not None:
        selected_country = clickData['points'][0]['location']
    filtered_df = df[(df['Year'] == selected_year) & (df['Country'] == selected_country)]
    fig = px.line(filtered_df, x='Month', y='Temperature', color='Year', title=f'Temperatuur in een linechart van {selected_country} in het jaar {selected_year}')
    return fig

print("H")
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=7778)
