import os
import sqlite3 as sql
import pandas as pd

DB_FOLDER = "web_scrape/dbs/"


def init_db(db_file, schema_file=None):
    """
    Initialize the database. Optionally, provide a SQL schema file to set up tables.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    
    with sql.connect(db_path) as conn:
        if schema_file:
            with open(schema_file, 'r') as f:
                conn.executescript(f.read())
    print(f"Database {db_file} initialized.")


def insert_athlete(db_file, name, profile_image_url):
    """
    Insert an athlete into the athletes table.
    Returns the athlete_id of the inserted row.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO athletes (name, profile_image_url) VALUES (?, ?)",
            (name, profile_image_url)
        )
        conn.commit()
        return cursor.lastrowid


def insert_event(db_file, athlete_id, event_title, race_title, race_name, date, country):
    """
    Insert event data into the events table.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (athlete_id, event_title, race_title, race_name, date, country)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (athlete_id, event_title, race_title, race_name, date, country)
        )
        conn.commit()


def insert_ranking(db_file, athlete_id, event_title, ranking_position, ranking_score, weeks_at_position):
    """
    Insert ranking data into the rankings table.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO rankings (athlete_id, event_title, ranking_position, ranking_score, weeks_at_position)
            VALUES (?, ?, ?, ?, ?)
            """,
            (athlete_id, event_title, ranking_position, ranking_score, weeks_at_position)
        )
        conn.commit()


def insert_personal_best(db_file, athlete_id, event_title, performance_time, performance_score):
    """
    Insert personal best data into the personal_bests table.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO personal_bests (athlete_id, event_title, performance_time, performance_score)
            VALUES (?, ?, ?, ?)
            """,
            (athlete_id, event_title, performance_time, performance_score)
        )
        conn.commit()


def insert_progression(db_file, athlete_id, event_title, year, time, race_name, date):
    """
    Insert progression data into the progressions table.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO progressions (athlete_id, event_title, year, time, race_name, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (athlete_id, event_title, year, time, race_name, date)
        )
        conn.commit()


def insert_honor(db_file, athlete_id, event_title, placement, race_title, date):
    """
    Insert honor data into the honors table.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO honors (athlete_id, event_title, placement, race_title, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (athlete_id, event_title, placement, race_title, date)
        )
        conn.commit()


def display_table(db_file, table_name):
    """
    Display all data from the specified table.
    """
    db_path = os.path.join(DB_FOLDER, db_file)
    with sql.connect(db_path) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    print(df)
    return df
