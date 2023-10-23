import pandas as pd
import dash
import pycountry
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
app = dash.Dash(__name__)

# Load your CSV file (replace 'your_dataset.csv' with the actual file path)
df = pd.read_csv('data/electricity.csv')
# print(df.head())
alpha2_to_alpha3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}


# Change all dates to years only, initialize min GWH, max GWH, the selected year and the selected indic, Get a list of available years and indic values
df['Year'] = pd.to_datetime(df['Date']).dt.year
min_gwh = df['GWH'].min()
max_gwh = df['GWH'].max()
selected_year = df['Year'].min()
available_years = df['Year'].unique()
available_indic_values = df['indic'].unique()  # Use the selected indic values
selected_indic = 'Consumption'  # Initialize to 'Consumption'

# Define the layout with two columns
app.layout = html.Div(children=[
    html.Div(children=[
        dcc.Graph(id='choropleth'),
        dcc.RadioItems(
            id='year-radio',
            options=[{'label': str(year), 'value': year} for year in available_years],
            value=selected_year,  # Default to the first year
        ),
        dcc.Dropdown(
            id='indic-dropdown',
            options=[{'label': indic, 'value': indic} for indic in available_indic_values],
            value=selected_indic,  # Default to 'Consumption'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div(children=[
        dcc.Graph(id='pie-chart'),
        dcc.Graph(id='histogram'),
        dcc.Graph(id='line-chart'),
    ], style={'width': '48%', 'display': 'inline-block'})
])

# Update the choropleth map based on selected year and indic
@app.callback(
    Output('choropleth', 'figure'),
    Input('year-radio', 'value'),
    Input('indic-dropdown', 'value')
)
def update_choropleth(df, selected_year, selected_indic):
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    # Filter the dataset based on the selected year and indic
    filtered_df = df[(df['Year'] == selected_year)]
    filtered_df = filtered_df[(filtered_df['indic'] == selected_indic)]
    filtered_df['geo\\TIME_PERIOD'] = filtered_df['geo\\TIME_PERIOD'].map(alpha2_to_alpha3)
    print(filtered_df.head())

    # Create a choropleth map based on the filtered data
    fig = px.choropleth(filtered_df, 
                        locations="geo\TIME_PERIOD", 
                        color="GWH",  # Use the selected indic column
                        hover_name="geo\TIME_PERIOD", 
                        # hover_data=[selected_indic, "GWH"],  # Display GWH in hover data
                        color_continuous_scale='Viridis',  
                        range_color=(min_gwh, max_gwh))

    # Customize the map layout and title
    fig.update_geos(
        visible=True, resolution=50, scope="europe",
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Blue"
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        height=1000, margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig.to_html(full_html=False)

# Update the pie chart based on selected year
@app.callback(
    Output('pie-chart', 'figure'),
    Input('year-radio', 'value')
)
def update_pie_chart(df, selected_year):
    # Filter the dataset based on the selected year
    filtered_df = df[(df['Year'] == selected_year)]

    # Create a pie chart based on the filtered data
    fig = px.pie(filtered_df, names='geo\TIME_PERIOD', values=selected_indic,  # Use the selected indic column
                 title=f'GWH Distribution for {selected_year}')

    return fig

# Update the histogram based on selected year
@app.callback(
    Output('histogram', 'figure'),
    Input('year-radio', 'value')
)
def update_histogram(df, selected_year):
    # Filter the dataset based on the selected year
    filtered_df = df[(df['Year'] == selected_year)]

    # Create a histogram based on the filtered data
    fig = px.histogram(filtered_df, x=selected_indic,  # Use the selected indic column
                      title=f'GWH Histogram for {selected_year}')

    return fig

# Update the line chart based on selected year
@app.callback(
    Output('line-chart', 'figure'),
    Input('year-radio', 'value')
)
def update_line_chart(df, selected_year):
    # Filter the dataset based on the selected year
    filtered_df = df[(df['Year'] == selected_year)]

    # Create a line chart based on the filtered data
    fig = px.line(filtered_df, x='geo\TIME_PERIOD', y=selected_indic,  # Use the selected indic column
                 title=f'GWH Line Chart for {selected_year}')
    
    fig.to

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=7779)
