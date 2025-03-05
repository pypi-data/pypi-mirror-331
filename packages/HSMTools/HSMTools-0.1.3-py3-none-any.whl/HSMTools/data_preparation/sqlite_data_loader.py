import sqlite3
from typing import Dict

import polars as pl

class SQLiteDataLoader:
    """
    Responsible for loading tables from a SQLite database file (.dat file) as Polars DataFrames.
    """

    def load_tables_from_file(self, filepath: str) -> Dict[str, pl.DataFrame]:
        """
        Loads all tables from the SQLite database at the given filepath.

        Parameters:
            filepath (str): Path to the SQLite (.dat) file.

        Returns:
            Dict[str, pl.DataFrame]: A dictionary mapping table names to their respective Polars DataFrames.
        """
        try:
            connection = sqlite3.connect(filepath)
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row[0] for row in cursor.fetchall()]

            tables = {}
            for table_name in table_names:
                query = f"SELECT * FROM {table_name}"
                df = pl.read_database(query, connection)
                tables[table_name] = df

            return tables
        except sqlite3.Error as e:
            print(f"SQLite error while processing {filepath}: {e}")
            return {}
        finally:
            if 'connection' in locals():
                connection.close()