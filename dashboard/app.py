import pandas as pd
import plotly.express as px
from flask import Flask, render_template_string, render_template
from sqlalchemy import create_engine, text, inspect, Table, MetaData
from sqlalchemy.orm import sessionmaker
from Electricty import MonthlyElectricity
from Temperature import TemperatureDownloader
from Population import DownloadPopulationData


# Load the csv file into the db
def _load_data_to_db():
    # Create a SQLAlchemy engine to connect to the PostgreSQL database
    engine = create_engine("postgresql://student:infomdss@db_dashboard:5432/dashboard")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    meta = MetaData()
    table = Table('temperature', meta)
    session.query(table).delete()
    session.commit()

    # Establish a connection to the database using the engine and delete all existing tables
    # The 'with' statement ensures that the connection is properly closed when done
    with engine.connect() as conn:
        # Execute an SQL command to drop the 'population' table if it exists
        # The text() function allows you to execute raw SQL statements
        conn.execute(text("DROP TABLE IF EXISTS population CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS temperature CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS electricity CASCADE;"))
    
    # Write the data from the pipelines to the sql database
    if False:
        TemperatureDownloader(engine)
        MonthlyElectricity().to_sql("electricity", engine, if_exists="replace", index=True)
        DownloadPopulationData().to_sql("population", engine, if_exists="replace", index=True)
    else:
        pd.read_csv("data/population.csv").to_sql("population", engine, if_exists="replace", index=True)
        pd.read_csv("data/temperature.csv").to_sql("temperature", engine, if_exists="replace", index=True)
        pd.read_csv("data/electricity.csv").to_sql("electricity", engine, if_exists="replace", index=True)

# Fetch the hardcoded population table from the database
def _fetch_data_from_db():
    engine = create_engine("postgresql://student:infomdss@db_dashboard:5432/dashboard")
    population_table = pd.read_sql_table('population', engine, index_col='index')

    return population_table

# Generate the interactive plot for in your HTML file
def generate_population_graph():
    # Get the table from the database, returns a dataframe of the table
    population_df = _fetch_data_from_db()
    data_netherlands = population_df["country"]="NLD"
    print(population_df.head())

    fig = px.bar(population_df, x='Date', y='Population', barmode='group')  # Set the barmode to 'group' for side-by-side bars
    # Convert the Plotly figure to HTML
    plot_html = fig.to_html(full_html=False)

    return plot_html


# Load the data into the database
# You will do this asynchronously as a cronjob in the background of your application
# Or you fetch the data from different sources when the page is visited or how you like to fetch your data
# Notice that the method _load_data_to_db() now just reads a preloaded .csv file
# You will have to fetch external files, or call API's to fill your database
_load_data_to_db()

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def index():
    # As soon as the page is loaded, the data is retrieved from the db and the graph is created
    # And is put in the HTML div
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)