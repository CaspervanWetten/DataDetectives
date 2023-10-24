import pandas as pd
from sqlalchemy import create_engine
from os import listdir

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

    def _drop_data(self, *tables):
        """
        Drop specified tables from the database.
        Args:
            *tables: Variable number of table names to drop.
        """
        with self.engine.connect() as connection:
            for table in tables:
                query = f"DROP TABLE IF EXISTS {table} CASCADE"
                try:
                    connection.execute(query)
                except Exception as e:
                    print(f"An error occurred while dropping table {table}:\n{e}")

    def _load_data(self, exists="replace", **kwargs):
        """
        Load data into the database.
        Args:
            exists (str): If table already exists, 'replace' to replace it, 'append' to append data or 'fail' to raise a ValueError
            **kwargs: keyword arguments, "temperature=df" will make a table called [temperature] with [df] as values
        """
        for key, value in kwargs.items():
            value.to_sql(str(key), self.engine, if_exists=exists, index=True)

    def _fetch_data(self, query):
        """
        Fetch data from a specified table.
        Args:
            query (str): The query to fetch the data,
        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
            or
            str: A "failed to execute" string which shows the error
        """
        try:
            df = pd.read_sql_query(query, self.engine)
        except Exception as e:
            return f"failed to execute {query} with \n {e} \n as error"
        return df

        
