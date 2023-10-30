import pandas as pd
import pycountry
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
#from database import database as db
app = dash.Dash(__name__)

# # Load your CSV file (replace 'your_dataset.csv' with the actual file path)
# df = pd.read_csv('dashboard\data\electricity.csv')
# # print(df.head())
# alpha2_to_alpha3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}


# # Change all dates to years only, initialize min GWH, max GWH, the selected year and the selected indic, Get a list of available years and indic values
# df['Year'] = pd.to_datetime(df['Date']).dt.year
# min_gwh = df['GWH'].min()
# max_gwh = df['GWH'].max()
# selected_year = df['Year'].min()
# available_years = df['Year'].unique()
# available_indic_values = df['indic'].unique()  # Use the selected indic values
# selected_indic = 'Consumption'  # Initialize to 'Consumption'

# # Define the layout with two columns
# app.layout = html.Div(children=[
#     html.Div(children=[
#         dcc.Graph(id='choropleth'),
#         dcc.RadioItems(
#             id='year-radio',
#             options=[{'label': str(year), 'value': year} for year in available_years],
#             value=selected_year,  # Default to the first year
#         ),
#         dcc.Dropdown(
#             id='indic-dropdown',
#             options=[{'label': indic, 'value': indic} for indic in available_indic_values],
#             value=selected_indic,  # Default to 'Consumption'
#         ),
#     ], style={'width': '48%', 'display': 'inline-block'}),
#     html.Div(children=[
#         dcc.Graph(id='pie-chart'),
#         dcc.Graph(id='histogram'),
#         dcc.Graph(id='line-chart'),
#     ], style={'width': '48%', 'display': 'inline-block'})
# ])

# # Update the choropleth map based on selected year and indic
# @app.callback(
#     Output('choropleth', 'figure'),
#     Input('year-radio', 'value'),
#     Input('indic-dropdown', 'value')
# )
def update_choropleth(df, selected_year, selected_indic):
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    # Filter the dataset based on the selected year and indic
    filtered_df = df[(df['Year'] == selected_year)]
    filtered_df = filtered_df[(filtered_df['indic'] == selected_indic)]
    filtered_df['geo\\TIME_PERIOD'] = filtered_df['geo\\TIME_PERIOD'].map(alpha2_to_alpha3)
    print(filtered_df.head())

def Choropleth(df):
    fig = px.choropleth(df, 
                        locations="Country",
                        color="GWH", 
                        hover_name="Country",
                        color_continuous_scale='Viridis',
                        scope="europe"
                        )

    fig.update_geos(
        visible=True, resolution=50,
        showcountries=True, countrycolor="Black",
        fitbounds="locations",
        center=dict(lat=51.1657, lon=10.4515),
        projection_scale=15         
    )

    fig.update_layout(
        autosize=False,
        geo=dict(
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        margin = dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=4,
                autoexpand=True
            ),
        width=800,
        dragmode=False
        )

    return fig