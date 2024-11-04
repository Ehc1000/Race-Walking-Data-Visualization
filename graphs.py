from flask import Blueprint, render_template
from bokeh.embed import server_document
import sqlite3
import pandas as pd
import random
from datetime import datetime
from bokeh.palettes import Blues8
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io.export import export_png
from selenium import webdriver
import os
import chromedriver_binary

graphs_bp = Blueprint('graphs', __name__)

# Database connection
conn = sqlite3.connect('DrexelRaceWalking.db', check_same_thread=False)

def read_loc_data(race_id):
    data = pd.read_sql(f'SELECT "ID", "IDRace", "BibNumber", "LOCAverage", "KneeAngle", "TOD" FROM VideoObservation WHERE BibNumber>0 and IDRace={race_id} ORDER BY TOD', conn)
    data.columns = ["ID", "IDRace", 'BibNumber', 'LOC', 'KneeAngle', 'Time']
    return data

def read_bib_data():
    data = pd.read_sql('SELECT "IDAthlete", "BibNumber" from Bib LIMIT 96', conn)
    data.columns = ['ID', 'BibNumber']
    return data

def read_id_data():
    data = pd.read_sql('SELECT "IDAthlete", "FirstName", "LastName" from Athlete', conn)
    data.columns = ['ID', 'FirstName', 'LastName']
    return data

def read_judge_calls_data():
    data = pd.read_sql('SELECT * from JudgeCall WHERE IDRace=1 ORDER BY Color LIMIT 329', conn)
    return data

@graphs_bp.route('/')
def graphs(race_id=1):
    # Read data
    os.makedirs(f'graphs/race_{race_id}', exist_ok=True)
    loc_data = read_loc_data(race_id)
    judge_calls_data = pd.read_sql(f'SELECT * from JudgeCall WHERE IDRace={race_id} ORDER BY Color LIMIT 329', conn)
    bib_data = read_bib_data()
    name_data = read_id_data()

    loc_data['Time'] = pd.to_datetime(loc_data['Time'])
    judge_calls_data['TOD'] = pd.to_datetime(judge_calls_data['TOD'])

    # Merge to get runner names
    merged_data = pd.merge(bib_data, name_data, on='ID')
    
    # Loop through each athlete and create a separate plot
    for runner_id in loc_data['BibNumber'].unique():
        loc_data_runner = loc_data[loc_data['BibNumber'] == runner_id]
        loc_data_runner = pd.merge(loc_data_runner, merged_data, on='BibNumber')
        if loc_data_runner.empty:
            print(f"No data found for runner ID {runner_id}. Skipping.")
            continue
        # print(loc_data_runner)
        p = figure(title=f'Loss of Contact vs Judge Calls for Runner {runner_id}', x_axis_type="datetime", width=1920, height=940)
        
        source = ColumnDataSource(data={
            'x': pd.to_datetime(loc_data_runner['Time']),
            'y': loc_data_runner['LOC'],
            'name': loc_data_runner['FirstName'],
            'surname': loc_data_runner['LastName'],
            'bib_number': [str(runner_id)] * len(loc_data_runner)
        })
        color = Blues8[0]
        name = loc_data_runner['FirstName'].iloc[0]
        surname = loc_data_runner['LastName'].iloc[0]

        p.line(x='x', y='y', source=source, line_width=3, color=color, alpha=1, muted_alpha=0.1,
               legend_label=f"{name} {surname}")
        p.scatter(x='x', y='y', source=source, color=color, size=5)

        hover = HoverTool(tooltips=[
            ("FirstName", "@name"),
            ("LastName", "@surname"),
            ("Bib Number", "@bib_number"),
            ("LOC", "@y"),
            ("Time", "@x{%F %T}")
        ], formatters={'@x': 'datetime'}, mode='mouse')

        p.add_tools(hover)

        # Add judge call markers
        color_mapping = {
            'Yellow': 'yellow',
            'Red': 'red'
        }
        judge_calls_source = ColumnDataSource(data=dict(x=[], y=[], text=[], color=[]))

        for _, row in judge_calls_data[judge_calls_data['BibNumber'] == runner_id].iterrows():
            nearest_before = loc_data_runner[loc_data_runner['Time'] <= row['TOD']].iloc[-1:]
            after_calls = loc_data_runner[loc_data_runner['Time'] > row['TOD']].iloc[:1]

            if not nearest_before.empty and not after_calls.empty:

                nearest_before_time = nearest_before['Time'].iloc[0]
                t1 = 0
                t2 = (after_calls['Time'].iloc[0] - nearest_before_time).total_seconds()
                t3 = (pd.to_datetime(row['TOD']) - nearest_before_time).total_seconds()

                loc1 = float(nearest_before['LOC'].iloc[0])
                loc2 = float(after_calls['LOC'].iloc[0])

                m = (loc2 - loc1) / t2
                loc3 = (m * t3) + loc1

                x_judge = pd.to_datetime(row['TOD'])
                y_judge = loc3
                color = color_mapping.get(row['Color'], 'red')

                judge_calls_source.data['x'].append(x_judge)
                judge_calls_source.data['y'].append(y_judge)
                judge_calls_source.data['text'].append('  Judge #' + str(row['IDJudge']))
                judge_calls_source.data['color'].append(color)


            p.text(x='x', y='y', text='text', color='black', source=judge_calls_source)
            p.scatter(x='x',y='y', fill_color='color', source=judge_calls_source, size=10)
        p.legend.location = "top_left"
        p.legend.click_policy = "mute"
        p.background_fill_color = "white"

        # Export the plot as a PNG
        export_png(p, filename=f"graphs/race_{race_id}/runner_{runner_id}_plot.png")

if __name__ == '__main__':
    graphs(1)
