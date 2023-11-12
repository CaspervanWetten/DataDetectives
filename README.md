# DataDetectives Dashboard

## Introduction

Welcome to the DataDetectives Dashboard, a powerful tool offering visualizations of energy statistics across Europe. This comprehensive dashboard not only presents energy usage data but also integrates and compares it with population and temperature metrics. By doing so, it provides a holistic view, enabling users to explore the correlation between energy consumption and various factors.

## Known Bugs

There is a known issue where data for Iceland and Norway may intermittently disappear on the choropleth map. If you encounter this, a simple page reload (not the entire service) should resolve the problem.

## Installation and Usage

Setting up and running the DataDetectives Dashboard is a straightforward process:

1. Clone the repository to your local machine.
2. Navigate to the root directory of the cloned project using the `cd` command.
3. Execute the command `docker-compose build` in the project's root directory.
4. Once the build process is complete, launch the application with `docker-compose up`.

The dashboard should now be accessible. By default, it should be available at 127.0.0.1:8080, but this may vary depending on your system. We recommend checking the terminal output to confirm the exact address.

## Code Explanation

The DataDetectives Dashboard utilizes a PostgreSQL database to query information. The interaction with this database is facilitated through a Database object. The database is populated by data pipelines, each dedicated to a specific type of data (Population data, Temperature data, Monthly Energy data, and Yearly Energy data). These pipelines download, clean, and prepare the corresponding data.

- `app.py` represents the Dash application, serving as the dashboard interface.
- `Database.py` contains the code for the Database object, enabling seamless interaction with the PostgreSQL database.
- `Electricity.py` is the pipeline for electricity data.
- `Population.py` manages the population data pipeline.
- `Temperature.py` handles the temperature data pipeline.
- `PerCapita.py` calculates per capita energy usage.
- `Predictions.py` utilizes an optimized random forest regressor to predict GWH usage.

## Data Sources

Our dashboard is powered by data from reputable sources to ensure accuracy and reliability.
The temperature data is sourced from the KNMI Climate Explorer, a tool provided by the Royal Netherlands Meteorological Institute. Our population data is obtained from the World Bank API, which provides access to comprehensive global development data. Lastly, the energy data is derived from EUROSTAT, the statistical office of the European Union, which provides high-quality statistics at the European level.
By integrating these diverse datasets, we aim to provide a holistic view of energy usage across the European Union.

### Final Note

The Jupyternotebook is no longer used in the deployment of this application. It's continued inclusion is for legacy reasons.

### Credits

Ismaïl el Alami
Dagmar van den Berg
Laura Bröring
Roy Schenk
Thomas Valkenburg
Casper van Wetten

### License

This code has been licensed under the [GNU General Public License V3.0.](https://choosealicense.com/licenses/gpl-3.0/)
