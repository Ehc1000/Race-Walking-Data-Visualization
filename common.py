import os
import re
import sqlite3 as sql

import pandas as pd

# https://docs.python.org/3/library/sqlite3.html

QUERY_FOLDER = 'sql'
LABELED_QUERY_FOLDER = 'sql-named-parameters'
DB_FOLDER = ''


# NORMAL QUERY OPERATIONS

def df_from_query(query_file, db_file, params=()):
    with open(f'{QUERY_FOLDER}/{query_file}', 'r') as sql_file:
        sql_query = sql_file.read()
    with sql.connect(f'{DB_FOLDER}/{db_file}') as conn:
        df = pd.read_sql_query(sql_query, conn, params=params)
    return df


def get_all_queries():
    return [f for f in os.listdir(QUERY_FOLDER) if f.endswith('.sql')]


def get_parameter_count(query_file):
    with open(f'{QUERY_FOLDER}/{query_file}', 'r') as sql_file:
        sql_query = sql_file.read()
    return sql_query.count('?')


# LABELED QUERY OPERATIONS

def df_from_labeled_query(query_file, db_file, params=None):
    # pycharm gets mad when you use a mutable object as a default argument
    # why? because apparently python only evaluates the expression once,
    # and if it's ever modified, all future calls to that function will use
    # that modified object. so okay, we will do pycharm's bidding and get rid
    # of that yellow underline, and do it like this:
    if params is None:
        params = {}
    with open(f'{LABELED_QUERY_FOLDER}/{query_file}', 'r') as sql_file:
        sql_query = sql_file.read()
    with sql.connect(f'{DB_FOLDER}/{db_file}') as conn:
        df = pd.read_sql_query(sql_query, conn, params=params)
    return df


def get_all_labeled_queries():
    return [f for f in os.listdir(LABELED_QUERY_FOLDER) if f.endswith('.sql')]


def get_sql_parameters(query_file):
    with open(f'{LABELED_QUERY_FOLDER}/{query_file}', 'r') as sql_file:
        sql_query = sql_file.read()
    # since let's be honest, none of us have regex memorized, let's be specific here:
    # this regex searches for all strings starting with colons, followed by a word that is
    # specifically at least one alphanumeric or underscore character, of course going until
    # it runs of out of such characters, likely up to some whitespace.
    # the capture group denoted by the parentheses ensure only the words themselves are returned
    # disregarding the colon.
    parameters = re.findall(r':(\w+)', sql_query)
    return list(set(parameters))
