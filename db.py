"""
Database connection helper for the Azure SQL (SQL Server) Lego database.

Usage:
    from db import get_connection, query

    conn = get_connection()          # raw pymssql connection
    df   = query("SELECT TOP 5 * FROM sets")  # returns a pandas DataFrame
"""

import os
import pymssql
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_connection() -> pymssql.Connection:
    return pymssql.connect(
        server   = os.environ["DB_HOST"],
        port     = int(os.environ.get("DB_PORT", 1433)),
        database = os.environ["DB_NAME"],
        user     = os.environ["DB_USER"],
        password = os.environ["DB_PASSWORD"],
        tds_version = "7.4",
    )

def query(sql: str, params=None) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=params)
