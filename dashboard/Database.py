import pandas as pd
import regex as re
from sqlalchemy import create_engine, Table, MetaData, select, text

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

    def _fetch_data(self, sel_table, distinct=False, *sel_columns, **sel_where):
        """
        Fetch data from a specified table.
        Args:
            sel_table (str): name of the table
            distinct=False (bool): selects only the unique items, de
            sel_columns: a list of returned columns, passing none will return all columns
            sel_where: keyword arguments where column name == conditional, passing no condition will return all columns
            so SELECT Country, GWH FROM electricity WHERE year == 2010 would be  _fetch_data(electricity, Country, GWH, year="=2010")
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

        if distinct:
            statement = statement.distinct()

        if sel_where:
            for column_name, conditional in sel_where.items():
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
            print(f"SQL error \n {e}")
            return pd.DataFrame()