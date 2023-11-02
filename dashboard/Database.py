import pandas as pd
import regex as re
from sqlalchemy import create_engine, Table, MetaData, select, text
from Electricty import MonthlyElectricity, TypesOfEnergy
from Temperature import TemperatureDownloader
from Population import DownloadPopulationData


class Database:
    """
    Database class, manages db initialization, fetching and loading
    Parameters:
        engine (str): The database engine (i.e., PostgreSQL connection string).
        source (str): Data source, 'csv' or 'api'.
    Attributes:
        engine (sqlalchemy.engine): Database engine.
    Methods:
        _drop_data(*tables): Drop specified tables from the database.
        _load_data(exists='replace', **kwargs): Load data into the database.
        _fetch_data(table): Fetch data from a specified table.
    """

    def __init__(self):
        """
        Initialize the Database instance.
        Args:
            engine (str): The database engine (i.e., PostgreSQL connection string).
        """
        self.engine = create_engine("postgresql://student:infomdss@db_dashboard:5432/dashboard")
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)

    def _update_database(self):
        print("dropping old data...")
        self._drop_all_tables()
        print("Downloading new population data...")
        self._load_data(population=DownloadPopulationData())
        print("Downloading new monthly electricity data...")
        self._load_data(electricity_consumption=MonthlyElectricity())
        print("Downloading new segregated electricity data...") #shit am I racist????
        self._load_data(electricity_types=TypesOfEnergy())
        #The temperature data appends the database, hence why it passes the database as a self object
        TemperatureDownloader(db=self)

    def _update_database_csv(self):
        print("dropping old data...")
        self._drop_all_tables()
        print("Getting population data...")
        self._load_data(population=pd.read_csv("csv/population.csv"))
        print("Getting monthly electricity data...")
        self._load_data(electricity_consumption=pd.read_csv("csv/electricity_consumption.csv"))
        print("Getting segregated electricity data...")
        self._load_data(electricity_types=pd.read_csv("csv/electricity_types.csv"))
        print("Getting temperature data...") 
        self._load_data(temperature=pd.read_csv("csv/temperature.csv"))

    def _drop_all_tables(self):
        """
        Drops all tables in the database
        """
        self.metadata.reflect(bind=self.engine)
        for table in reversed(self.metadata.sorted_tables):
            table.drop(self.engine)
        self.metadata = MetaData()

    def _to_csv(self):
        for table in self.metadata.tables.keys():
            df = self._fetch_data(f"SELECT * FROM {table}")
            df.to_csv(f"{table}.csv", index=False)

    def _load_data(self, exists="replace", **kwargs):
        """
        Load data into the database.
        Args:
            exists (str): What to do if a table already exists, 'replace' to replace it, 'append' to append data or 'fail' to raise a ValueError
            **kwargs: keyword arguments, "temperature=df" will make a table called [temperature] with [df] as the table
        """
        for key, value in kwargs.items():
            value.to_sql(str(key), self.engine, if_exists=exists, index=True)
        self.metadata = MetaData()

    def _fetch_data(self, query):
        """
        Fetch data from a specified table.
        Args:
            query (str): The SQL query to execute on the database
        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
            or
            List: If only a single column is selected, it'll return an (unordered) list
            or
            pd.DataFrame: If the query fails, it'll print an error and return an empty dataframe
        """
        try:
            with self.engine.connect() as con:
                res = pd.read_sql(query, con)
                if len(res.columns) == 1:
                    return res.iloc[:,0]
            return res
        except Exception as e:
            print(f"Can't execute \n{query}\n due to error \n {e}")
            return pd.DataFrame()