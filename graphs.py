from flask import Blueprint, render_template, request, send_file
from bokeh.embed import server_document
import sqlite3
import pandas as pd
from datetime import datetime
from bokeh.palettes import Blues8, Category10
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io.export import export_png
from bokeh.embed import components

import os
import chromedriver_binary

graphs_bp = Blueprint('graphs', __name__)
# Database connection
conn = sqlite3.connect('DrexelRaceWalking.db', check_same_thread=False)

def read_loc_data(race_id, athlete_ids):
    athlete_ids_str = ",".join(map(str, athlete_ids))
    query = f'''
        SELECT "ID", "IDRace", "BibNumber", "LOCAverage", "KneeAngle", "TOD"
        FROM VideoObservation 
        WHERE BibNumber IN ({athlete_ids_str}) AND IDRace={race_id} 
        ORDER BY TOD
    '''
    data = pd.read_sql(query, conn)
    data.columns = ["ID", "IDRace", 'BibNumber', 'LOC', 'KneeAngle', 'Time']
    return data

def read_bib_data():
    data = pd.read_sql('SELECT "IDAthlete", "BibNumber" FROM Bib LIMIT 96', conn)
    data.columns = ['ID', 'BibNumber']
    return data

def read_id_data():
    data = pd.read_sql('SELECT "IDAthlete", "FirstName", "LastName" FROM Athlete', conn)
    data.columns = ['ID', 'FirstName', 'LastName']
    return data

def read_judge_calls_data(race_id, athlete_ids):
    athlete_ids_str = ",".join(map(str, athlete_ids))
    query = f'''
        SELECT * FROM JudgeCall 
        WHERE BibNumber IN ({athlete_ids_str}) AND IDRace={race_id} 
        ORDER BY Color 
        LIMIT 329
    '''
    data = pd.read_sql(query, conn)
    return data

def get_available_athletes(race_id):
    query = f'''
        SELECT DISTINCT BibNumber 
        FROM VideoObservation 
        WHERE IDRace={race_id}
    '''
    # Fetch data from the database
    data = pd.read_sql(query, conn)
    
    # Debug output to check the content of the DataFrame
    print(f"Query Result for Race {race_id}:")

    # Return a list of BibNumbers
    return data['BibNumber'].tolist()

# Function to generate unique colors for each athlete
def get_unique_color(runner_id, max_colors=10):
    return Category10[10][runner_id % max_colors]

def generate_graph(race_id: int, athletes):
    # Fetch data for specified athlete IDs only
    print(athletes)
    loc_data = read_loc_data(race_id, athletes)
    judge_calls_data = read_judge_calls_data(race_id, athletes)
    bib_data = read_bib_data()
    name_data = read_id_data()

    loc_data['Time'] = pd.to_datetime(loc_data['Time'])
    judge_calls_data['TOD'] = pd.to_datetime(judge_calls_data['TOD'])

    # Merge to get runner names
    merged_data = pd.merge(bib_data, name_data, on='ID')

    # Initialize figure for plot
    p = figure(title=f'Loss of Contact vs Judge Calls for Race {race_id}', x_axis_type="datetime", width=1920, height=940)
    
    # Add each athlete's data to the combined plot
    for runner_id in athletes:
        runner_id = int(float(runner_id))
        loc_data_runner = loc_data[loc_data['BibNumber'] == runner_id]
        loc_data_runner = pd.merge(loc_data_runner, merged_data, on='BibNumber')

        if loc_data_runner.empty:
            print(f"No data found for runner ID {runner_id}. Skipping.")
            continue

        athlete_color = get_unique_color(runner_id)
        name = loc_data_runner['FirstName'].iloc[0]
        surname = loc_data_runner['LastName'].iloc[0]

        source = ColumnDataSource(data={
            'x': pd.to_datetime(loc_data_runner['Time']),
            'y': loc_data_runner['LOC'],
            'name': loc_data_runner['FirstName'],
            'surname': loc_data_runner['LastName'],
            'bib_number': [str(runner_id)] * len(loc_data_runner)
        })

        p.line(x='x', y='y', source=source, line_width=3, color=athlete_color, alpha=1, muted_alpha=0.1,
               legend_label=f"{name} {surname}")
        p.scatter(x='x', y='y', source=source, color=athlete_color, size=5)

        hover = HoverTool(tooltips=[
            ("FirstName", "@name"),
            ("LastName", "@surname"),
            ("Bib Number", "@bib_number"),
            ("LOC", "@y"),
            ("Time", "@x{%F %T}")
        ], formatters={'@x': 'datetime'}, mode='mouse')

        p.add_tools(hover)

        # Add judge call markers
        color_mapping = {'Yellow': 'yellow', 'Red': 'red'}
        judge_calls_source = ColumnDataSource(data=dict(x=[], y=[], text=[], color=[], shape=[], infraction=[]))
        print(judge_calls_data)
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
                shape = 'square' if row['Color'] == 'Red' else 'circle'

                judge_calls_source.data['x'].append(x_judge)
                judge_calls_source.data['y'].append(y_judge)
                judge_calls_source.data['text'].append('  Judge #' + str(row['IDJudge']))
                judge_calls_source.data['color'].append(color)
                judge_calls_source.data['shape'].append(shape)
                judge_calls_source.data['infraction'].append(row['Infraction'])
            p.scatter(x='x', y='y', fill_color='color', source=judge_calls_source, size=20, marker='shape')
            p.text(x='x', y='y', text='text', color='black', source=judge_calls_source)
            p.text(x='x', y='y', text='infraction', color='black', source=judge_calls_source, x_offset=-5, y_offset=9)
    p.legend.location = "top_left"
    p.legend.click_policy = "mute"
    p.background_fill_color = "white"
    p.xaxis.axis_label = "Time"
    p.yaxis.axis_label = "LOC"

    graph_dir = 'static\graphs' 
    
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    
    # file path
    graph_path = os.path.join(graph_dir, f"graph_{race_id}.png")
    export_png(p, filename=graph_path)

    return graph_path


@graphs_bp.route('/race/<int:race_id>', methods=['GET'])
def graphs(race_id):
    # If GET request, show the selection form
    athletes = sorted(get_available_athletes(race_id))
    return render_template('graphs.html', race_id=race_id, athlete_ids=athletes, script=None, div=None)


@graphs_bp.route('/generate_graph/<int:race_id>', methods=['GET'])
def generate_graph_route(race_id):
    selected_athletes = request.args.getlist('selected_athletes')
    graph_path = generate_graph(int(race_id), selected_athletes)
    print(f"Graph saved at: {graph_path}")

    return send_file(graph_path, mimetype='image/png')


if __name__ == '__main__':
    print("Here")