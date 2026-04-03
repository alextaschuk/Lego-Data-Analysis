"""
Database connection helper for the Azure SQL (SQL Server) Lego database.

Usage:
    from db import get_connection, query

    conn = get_connection()          # raw pymssql connection
    df   = query("SELECT TOP 5 * FROM sets")  # returns a pandas DataFrame
"""

import pymssql
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# Create a directory to store the cached files
CACHE_DIR = "db_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_connection() -> pymssql.Connection:
    '''Connect to the SQL database'''
    return pymssql.connect(
        server      = os.environ["DB_HOST"],
        port        = os.environ["DB_PORT"],
        database    = os.environ["DB_NAME"],
        user        = os.environ["DB_USER"],
        password    = os.environ["DB_PASSWORD"],
        tds_version = "7.4",
    )

def query(sql: str, params=None) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=params)

def get_cached_query(query_str: str, table_name: str) -> pd.DataFrame:
    """
    Attempts to load a DataFrame from disk. If not found, runs the query
    and saves the result to disk.
    """
    cache_path = os.path.join(CACHE_DIR, f"{table_name}.pkl")

    if os.path.exists(cache_path):
        print(f"Loading table '{table_name}' from the cache...")
        return pd.read_pickle(cache_path)

    print(f"Querying table '{table_name}' the from Azure database...")
    df = query(query_str)
    df.to_pickle(cache_path)
    return df
