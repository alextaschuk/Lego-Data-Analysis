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
    # Extract just the 'cosc301' part from the host
    short_server = os.environ["DB_HOST"].split('.')[0]

    # Format user as username@servername
    db_user = f"{os.environ['DB_USER']}@{short_server}"

    return pymssql.connect(
        server      = os.environ["DB_HOST"],
        port        = int(os.environ.get("DB_PORT", 1433)),
        database    = os.environ["DB_NAME"],
        user        = db_user,
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
        print(f"Loading {table_name} from cache...")
        return pd.read_pickle(cache_path)

    print(f"Querying {table_name} from databased...")
    df = query(query_str)
    df.to_pickle(cache_path)
    return df
