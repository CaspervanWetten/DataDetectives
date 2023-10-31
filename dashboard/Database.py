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

    def _fetch_data(self, sel_table, *sel_columns, **sel_where):
        """
        Fetch data from a specified table.
        Args:
            sel_table (str): name of the table
            sel_columns: a list of returned columns, passing none will return all columns
            sel_where: keyword arguments where column name == conditional, passing no condition will return all columns. Can also pass distinct="true" to get all unique values;
            The query "SELECT Country, GWH FROM electricity WHERE year == 2010" would be  _fetch_data(electricity, Country, GWH, year="=2010")
        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
            or
            List: If only a single column is selected, it'll return an (unordered) list
            or
            pd.DataFrame: If the query fails, it'll print an error and return an empty dataframe
        """
        table = Table(sel_table, self.metadata, autoload_with=self.engine)

        if sel_columns:
            columns = [table.c[col] for col in sel_columns]
        else:
            columns = [table.c[col] for col in table.columns.keys()]
        statement = select(*columns).select_from(table)

        if sel_where.pop('distinct', ''):
            statement = statement.distinct()

        if sel_where:
            for column_name, conditional in sel_where.items():
                if "distinct" in conditional:
                    continue
                column = table.c[column_name]
                operator_value = re.split(r'([<>=]+)', conditional)
                operator = operator_value[1].strip()
                value = operator_value[2].strip()

                if not value.isdigit():
                    statement = statement.where(text(f"'{column_name}' {conditional}"))
                    continue
                else:
                    value = value.strip()
                if operator == '=':
                    statement = statement.where(column == value)
                elif operator == '>':
                    statement = statement.where(column > value)
                elif operator == '<':
                    statement = statement.where(column < value)
                elif operator == '>=':
                    statement = statement.where(column >= value)
                elif operator == '<=':
                    statement = statement.where(column <= value)
                elif operator.lower() == 'like':
                    statement = statement.where(column.like(value))
                
        try:
            with self.engine.connect() as con:
                result = con.execute(statement)
                result = result.fetchall()
            if len(columns) == 1:
                return [row[0] for row in result]
            df = pd.DataFrame(result, columns=[col.name for col in columns])
            return df
        except Exception as e:
            print(f"Quit query: \n {statement} \n with the following SQL error: \n {e}")
            return pd.DataFrame()
