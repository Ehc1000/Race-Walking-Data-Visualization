from flask import Blueprint, redirect, render_template, render_template_string, request
from bokeh.embed import server_document
import sqlite3
import pandas as pd
from bokeh.palettes import Blues8, Category10, Viridis256
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Legend, LegendItem, DatetimeTickFormatter
from bokeh.embed import components

graphs_bp = Blueprint('graphs', __name__)
# Database connection
conn = sqlite3.connect('db/DrexelRaceWalking.db', check_same_thread=False)


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
    data = pd.read_sql('SELECT "IDAthlete", "BibNumber" FROM Bib', conn)
    data.columns = ['ID', 'BibNumber']
    return data


def read_id_data():
    data = pd.read_sql('SELECT "IDAthlete", "FirstName", "LastName" FROM Athlete', conn)
    data.columns = ['ID', 'FirstName', 'LastName']
    return data


def read_judge_calls_data(race_id, athlete_ids):
    athlete_ids_str = ",".join(map(str, athlete_ids))
    # query = f'''
    #     SELECT * FROM JudgeCall 
    #     WHERE BibNumber IN ({athlete_ids_str}) AND IDRace={race_id} 
    #     ORDER BY Color 
    #     LIMIT 329
    # '''
    query = f'''
        SELECT JudgeCall.*, Judge.FirstName, Judge.LastName
        FROM JudgeCall
        JOIN Judge ON JudgeCall.IDJudge = Judge.IDJudge
        WHERE BibNumber IN ({athlete_ids_str}) AND IDRace={race_id} 
        ORDER BY Color
    '''
    data = pd.read_sql(query, conn)
    return data

def get_available_athletes(race_id):
    query = f'''
        SELECT DISTINCT Bib.BibNumber, Athlete.FirstName, Athlete.LastName
        FROM VideoObservation
        JOIN Bib ON VideoObservation.BibNumber = Bib.BibNumber
        JOIN Athlete ON Bib.IDAthlete = Athlete.IDAthlete
        WHERE VideoObservation.IDRace={race_id}
    '''
    # Fetch data from the database
    data = pd.read_sql(query, conn)

    # Debug output to check the content of the DataFrame
    # print(f"Query Result for Race {race_id}: {data}")

    # Return a list of BibNumbers
    # return data['BibNumber'].tolist()
    return data.to_dict(orient="records") 

predefined_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                     "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
athlete_to_color = {}

# Function to generate unique colors for each athlete
def get_unique_color(runner_id):
    if runner_id not in athlete_to_color:
        athlete_to_color[runner_id] = predefined_colors[len(athlete_to_color) % len(predefined_colors)]
    return athlete_to_color[runner_id]
    
def clean_time_string(time_str):
    # Replace invalid characters (e.g., double quotes) with valid ones
    return time_str.replace('"', ':')

def convert_time(time_str, race_date):
    try:
        # Clean the time string first
        cleaned_time_str = clean_time_string(time_str)
        # Combine the race date with the cleaned time string
        datetime_str = f"{race_date} {cleaned_time_str}"
        # Attempt to convert the combined string to a datetime object
        return pd.to_datetime(datetime_str)
    except ValueError:
        # If conversion fails, append 'AM' and try again
        datetime_str = f"{race_date} {cleaned_time_str} AM"
        return pd.to_datetime(datetime_str)


def combine_infractions(infractions):
    # Convert the list of infractions to a set to remove duplicates
    unique_infractions = set(infractions)
    
    # If both '~' and '<' are present, return '~/<'
    if '~' in unique_infractions and '<' in unique_infractions:
        return 'B'
    # Otherwise, return the first infraction in the set
    elif unique_infractions:
        return list(unique_infractions)[0]
    # If no infractions, return an empty string
    return ''



def generate_graph(race_id: int, athletes):
    # Limit to 10 athletes
    athletes = athletes[:10]
    # Hardcoded palette of 10 distinct colors
    predefined_colors = [
        "#1f77b4",  # Blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#7f7f7f",  # Gray
        "#bcbd22",  # Yellow-green
        "#17becf"  # Cyan
    ]
    # Fetch data for specified athlete IDs only
    #print(athletes)
    loc_data = read_loc_data(race_id, athletes)
    judge_calls_data = read_judge_calls_data(race_id, athletes)
    bib_data = read_bib_data()
    name_data = read_id_data()
    
    loc_data['Time'] = pd.to_datetime(loc_data['Time'])
    race_date = loc_data['Time'].iloc[0].date()

    judge_calls_data['TOD'] = judge_calls_data['TOD'].apply(convert_time, args=(race_date,))


    # Merge to get runner names
    merged_data = pd.merge(bib_data, name_data, on='ID')

    min_time = loc_data['Time'].min()
    max_time = loc_data['Time'].max()
    time_range = max_time - min_time
    buffer_seconds_y = time_range.total_seconds() * 0.1  # 10% buffer to extend x-axis from the left
    buffer_seconds_x = time_range.total_seconds() * 0.40  # 40% buffer to extend x-axis from the right to account for the athelte leegnd covering the data
    buffer_y = pd.Timedelta(seconds=buffer_seconds_y)
    buffer_x = pd.Timedelta(seconds=buffer_seconds_x)
    extended_min_time = min_time - buffer_y
    extended_max_time = max_time + buffer_x

    # Initialize figure for plot
    p = figure(
        title=f'Loss of Contact vs Judge Calls for Race {race_id}', 
        x_axis_type="datetime", 
        width=1920, 
        height=1140,
        sizing_mode="scale_width",
        x_range=(extended_min_time, extended_max_time)
    )

    # Set the x-axis tick formatter to display military time (HH:MM)
    p.xaxis.formatter = DatetimeTickFormatter(hours="%H:%M", minutes="%H:%M")

    index = 0
    # Define a judge dictionary to store names
    judge_legend_dict = {}
    # Add each athlete's data to the combined plot
    athletes_with_no_data = []
    for runner_id in athletes:
        runner_id = int(float(runner_id))
        loc_data_runner = loc_data[loc_data['BibNumber'] == runner_id]
        loc_data_runner = pd.merge(loc_data_runner, merged_data, on='BibNumber')

        # Extend athlete LOC data to last infraction time
        athlete_calls = judge_calls_data[judge_calls_data['BibNumber'] == runner_id]
        if not athlete_calls.empty:
            last_infraction_time = athlete_calls['TOD'].max()
            if last_infraction_time > loc_data_runner['Time'].max():
                # Find two nearest LOC points before and after the last infraction
                before = loc_data_runner[loc_data_runner['Time'] <= last_infraction_time].iloc[-1:]
                after = loc_data_runner[loc_data_runner['Time'] > last_infraction_time].iloc[:1]

                if not before.empty and not after.empty:
                    t1 = before['Time'].iloc[0]
                    t2 = after['Time'].iloc[0]
                    loc1 = before['LOC'].iloc[0]
                    loc2 = after['LOC'].iloc[0]
                    seconds_diff = (t2 - t1).total_seconds()
                    if seconds_diff != 0:
                        slope = (loc2 - loc1) / seconds_diff
                        t3 = (last_infraction_time - t1).total_seconds()
                        extrapolated_loc = loc1 + (slope * t3)
                        extended_row = before.copy()
                        extended_row['Time'] = last_infraction_time
                        extended_row['LOC'] = extrapolated_loc
                        loc_data_runner = pd.concat([loc_data_runner, extended_row], ignore_index=True)
        if loc_data_runner.empty:
            athletes_with_no_data.append(f"{runner_id}")
            print(f"No data found for runner ID {runner_id}. Skipping.")
            continue
        athlete_color = get_unique_color(runner_id)
        # Assign the color based on the athlete's index
        athlete_color = predefined_colors[index]
        index += 1
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
               legend_label=f"{name} {surname} ({runner_id})")
        p.scatter(x='x', y='y', source=source, color=athlete_color, size=5)

        hover = HoverTool(tooltips=[
            ("FirstName", "@name"),
            ("LastName", "@surname"),
            ("Bib Number", "@bib_number"),
            ("LOC", "@y"),
            ("Time", "@x{%H:%M:%S}")
        ], formatters={'@x': 'datetime'}, mode='mouse')

        p.add_tools(hover)

        # Add judge call markers
        color_mapping = {'Yellow': 'yellow', 'Red': 'red'}
        judge_calls_source = ColumnDataSource(data=dict(x=[], y=[], text=[], color=[], shape=[], infraction=[]))
        added_judges = set()
        # Iterate over the original judge_calls_data to populate the legend
        for _, row in judge_calls_data.iterrows():
            judge_id = row['IDJudge']
            if judge_id not in added_judges:
                judge_legend_dict[judge_id] = f'Judge #{judge_id}: {row["FirstName"]} {row["LastName"]}'
                added_judges.add(judge_id)

        # Group by BibNumber and TOD, and aggregate the judge calls
        grouped_judge_calls = judge_calls_data.groupby(['BibNumber', 'TOD']).agg({
            'IDJudge': lambda x: ', '.join(map(str, x)),
            'Color': 'first',  # Assuming all entries in the group have the same color
            'Infraction': lambda x: combine_infractions(x),
            'FirstName': lambda x: ', '.join(x),
            'LastName': lambda x: ', '.join(x)
        }).reset_index()
        # print(grouped_judge_calls)
        for _, row in grouped_judge_calls[grouped_judge_calls['BibNumber'] == runner_id].iterrows():
            nearest_before = loc_data_runner[loc_data_runner['Time'] <= row['TOD']].iloc[-1:]
            after_calls = loc_data_runner[loc_data_runner['Time'] > row['TOD']].iloc[:1]

            if not nearest_before.empty and not after_calls.empty:
                nearest_before_time = nearest_before['Time'].iloc[0]
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
                judge_calls_source.data['text'].append('    #' + str(row['IDJudge']))
                judge_calls_source.data['color'].append(color)
                judge_calls_source.data['shape'].append(shape)
                judge_calls_source.data['infraction'].append(row['Infraction'])

        # Plot the scatter points and text
        p.scatter(x='x', y='y', fill_color='color', source=judge_calls_source, size=20, marker='shape')
        p.text(x='x', y='y', text='text', color='black', source=judge_calls_source, y_offset=10)
        p.text(x='x', y='y', text='infraction', color='black', source=judge_calls_source, x_offset=-5, y_offset=9)

        # Create legend items
        judge_legend_items = [LegendItem(label=label) for _, label in judge_legend_dict.items()]

            
    p.legend.location = "top_right"
    p.legend.click_policy = "mute"
    p.background_fill_color = "white"
    p.xaxis.axis_label = "Time"
    p.yaxis.axis_label = "LOC"

    #Add Judge Legend
    sorted_judge_items = sorted(judge_legend_dict.items())
    judge_legend_items = [LegendItem(label=label) for _, label in sorted_judge_items]
    judge_legend = Legend(items=judge_legend_items)
    judge_legend.location = "bottom_right"
    p.add_layout(judge_legend)
    script, div = components(p)
    return script, div, athletes_with_no_data

@graphs_bp.route('/race/<int:race_id>', methods=['GET'])
def graphs(race_id):
    # Fetch available races
    query = 'SELECT DISTINCT IDRace FROM Race'
    race_data = pd.read_sql(query, conn)
    print(race_data)
    race_ids = race_data['IDRace'].tolist()  # List of available race IDs
    print(race_ids)
    # Fetch athletes for the selected race
    athletes = sorted(get_available_athletes(race_id), key=lambda x: x["BibNumber"])

    # Render the template with race_ids, race_id, and athlete_ids
    return render_template('graphs.html', race_ids=race_ids, race_id=race_id, athlete_ids=athletes)

@graphs_bp.route('', methods=['GET'])
@graphs_bp.route('/', methods=['GET'])
def graphs_default():
    return redirect('/graphs/race/1')

@graphs_bp.route('/generate_graph/<int:race_id>', methods=['POST'])
def generate_graph_route(race_id):
    selected_athletes = request.form.getlist('selected_athletes')
    script, div, athletes_with_no_data = generate_graph(int(race_id), selected_athletes)
    
    # warning message generation
    warning_message = ""
    if athletes_with_no_data:
        warning_message = "No data found for the following athletes: " + ", ".join(athletes_with_no_data)
    
    # Return the warning box, graph, and script
    return f'''
        <div id="warning-box" class="warning-box" style="display: {'inline-block' if warning_message else 'none'};">
            <p id="warning-message">{warning_message}</p>
        </div>
        {div}
        {script}
        <script>
            // Display the warning box if there's a warning message
            const warningBox = document.getElementById('warning-box');
            const warningMessage = document.getElementById('warning-message');
            if (warningMessage.textContent) {{
                warningBox.style.display = 'inline-block';
            }} else {{
                warningBox.style.display = 'none';
            }}
        </script>
    '''

@graphs_bp.route('/', methods=['GET', 'POST'])
def select_race():
    # Fetch available races
    query = 'SELECT DISTINCT IDRace FROM Race'
    race_data = pd.read_sql(query, conn)
    race_ids = race_data['IDRace'].tolist()  # List of available race IDs

    # If form is submitted, redirect to the selected race ID
    if request.method == 'POST':
        race_id = request.form.get('race_id')
        return redirect(f'/graphs/race/{race_id}')

    # Render the template with the list of race IDs
    return render_template('graphs.html', race_ids=race_ids, race_id=None)

@graphs_bp.route('/get-available-athletes/', methods=['GET', 'POST'])
def get_athletes():
    race = request.args.get('race')  
    athletes = get_available_athletes(race)
    return render_template_string('''
        {% for athlete in available_athletes %}
            <option value="{{ athlete }}">{{ athlete }}</option>
        {% endfor %}
    ''', available_athletes=athletes)

@graphs_bp.route('/graph-add/', methods=['POST'])
def add_athletes():
    # Get data from the request
    print(request.form)
    available_items = request.form.get('available-items')
    print(available_items)
    selected_items = request.form.get('selected-items')
    print(selected_items)

    # Process selected items
    selected_to_add = request.form.getlist('available_items')
    for item in selected_to_add:
        if item in available_items:
            available_items.remove(item)
            selected_items.append(item)

    return render_template_string('''
        <!-- Updated Available Athletes -->
        {% for athlete in available_items %}
            <option value="{{ athlete }}">{{ athlete }}</option>
        {% endfor %}
        <!-- Updated Selected Athletes -->
        {% for athlete in selected_items %}
            <option value="{{ athlete }}">{{ athlete }}</option>
        {% endfor %}
    ''', available_items=available_items, selected_items=selected_items)

@graphs_bp.route('/graph-remove/', methods=['POST'])
def remove_athletes():
    # Get data from the request
    available_items = request.form.getlist('available-items')
    selected_items = request.form.getlist('selected-items')

    # Process deselected items
    selected_to_remove = request.form.getlist('selected_items')
    for item in selected_to_remove:
        if item in selected_items:
            selected_items.remove(item)
            available_items.append(item)

    return render_template_string('''
        <!-- Updated Available Athletes -->
        {% for athlete in available_items %}
            <option value="{{ athlete }}">{{ athlete }}</option>
        {% endfor %}
        <!-- Updated Selected Athletes -->
        {% for athlete in selected_items %}
            <option value="{{ athlete }}">{{ athlete }}</option>
        {% endfor %}
    ''', available_items=available_items, selected_items=selected_items)
