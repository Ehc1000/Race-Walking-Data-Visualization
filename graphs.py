from flask import Blueprint, render_template
from bokeh.embed import server_document
import sqlite3
import pandas as pd
from bokeh.palettes import Blues8
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup
from datetime import datetime
import random

graphs_bp = Blueprint('graphs', __name__)

# Database connection
conn = sqlite3.connect('DrexelRaceWalking.db')

def read_loc_data():
    data = pd.read_sql('SELECT "ID", "IDRace", "BibNumber", "LOCAverage", "KneeAngle", "TOD" FROM VideoObservation WHERE BibNumber>0 ORDER BY TOD', conn)
    data.columns = ['BibNumber', 'LOC', 'Time']
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
def graphs():
    # Generate the plot here
    loc_data = read_loc_data()
    judge_calls_data = read_judge_calls_data()
    bib_data = read_bib_data()
    name_data = read_id_data()

    loc_data['Time'] = pd.to_datetime(loc_data['Time'])
    judge_calls_data['TOD'] = pd.to_datetime(judge_calls_data['TOD'])

    p = figure(title='Loss of Contact vs Judge Calls', x_axis_type="datetime", width=1920, height=940)
    some_runners = loc_data['BibNumber'].unique()[:]
    merged_data = pd.merge(bib_data, name_data, on='ID')

    for runner_id in some_runners:
        loc_data_runner = loc_data[loc_data['BibNumber'] == runner_id]
        loc_data_runner = pd.merge(loc_data_runner, merged_data, on='BibNumber')

        source = ColumnDataSource(data={
            'x': pd.to_datetime(loc_data_runner['Time']),
            'y': loc_data_runner['LOC'],
            'name': loc_data_runner['FirstName'],
            'surname': loc_data_runner['LastName'],
            'bib_number': [str(runner_id)] * len(loc_data_runner)
        })
        color = Blues8[random.randint(0, 7)]
        name = loc_data_runner['FirstName'][0]
        surname = loc_data_runner['LastName'][0]
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

    color_mapping = {
        'Yellow': 'yellow',
        'Red': 'red'
    }
    judge_calls_source = ColumnDataSource(data=dict(x=[], y=[], text=[], color=[]))

    for _, row in judge_calls_data.iterrows():
        bib_number = row['BibNumber']
        if bib_number in some_runners:
            loc_data_runner = loc_data[loc_data['BibNumber'] == bib_number]
            nearest_before = loc_data_runner[loc_data_runner['Time'] <= row['TOD']]
            after_calls = loc_data_runner[loc_data_runner['Time'] > row['TOD']]

            if not after_calls.empty:
                nearest_after = after_calls.iloc[0]
                t2 = (after_calls['Time'].iloc[0] - nearest_before['Time']).total_seconds()
                t3 = (pd.to_datetime(row['TOD']) - nearest_before['Time']).total_seconds()
                loc1 = float(nearest_before['LOC'])
                loc2 = float(after_calls['LOC'].iloc[0])
                m = (loc2 - loc1) / (t2 - 0)  # Use t1=0 for nearest_before
                loc3 = m * (t3 - 0) + loc1

                x_judge = pd.to_datetime(row['TOD'])
                y_judge = loc3
                color = color_mapping.get(row['Color'], 'red')

                judge_calls_source.data['x'].append(x_judge)
                judge_calls_source.data['y'].append(y_judge)
                judge_calls_source.data['text'].append(row['Infraction'] + ' Judge #' + str(row['IDJudge']))
                judge_calls_source.data['color'].append(color)

    judge_calls_glyph = p.text(x='x', y='y', text='text', color='color', source=judge_calls_source)

    checkbox_group = CheckboxGroup(labels=["Show Judge Calls"], active=[0])
    def update_glyph_visibility(attr, old, new):
        judge_calls_glyph.visible = 0 in checkbox_group.active

    checkbox_group.on_change('active', update_glyph_visibility)

    p.legend.location = "top_left"
    p.legend.click_policy = "mute"

    # Return the Bokeh plot as HTML
    script = server_document('http://localhost:5006/myapp')  # Adjust URL for your Bokeh server
    return render_template('graphs.html', script=script)

def runs_only_when_ran_from_command_line():
    print("This function runs when the script is executed directly!")

if __name__ == '__main__':
    runs_only_when_ran_from_command_line()
