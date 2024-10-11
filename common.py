import sqlite3 as sql
import pandas as pd

# https://docs.python.org/3/library/sqlite3.html

def df_from_query(query_file, db_file):
    with open(f'sql/{query_file}', 'r') as sql_file:
        sql_query = sql_file.read()
    conn = sql.connect(db_file)
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df
