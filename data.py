from flask import Blueprint, render_template, request
import sqlite3 as sql

data_bp = Blueprint('data', __name__)

# The data modification section. Making a note here for those reading this to google the datatables library,
# to do ninety percent of the work for you.
# https://datatables.net/

@data_bp.route('/')
def data():
    db_file = request.args.get('db', 'RWComplete.db')
    with sql.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        data = {}

        for table_name in tables:
            table = table_name[0]
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()

            cursor.execute(f"PRAGMA table_info({table});")
            columns = [col[1] for col in cursor.fetchall()]

            data[table] = {'columns': columns, 'rows': rows}
        
    return render_template('db_view.html', data=data)

# We can also treat this file as a command line script and forget we are using flask.
def runs_only_when_ran_from_command_line():
    print("This function runs when the script is executed directly!")

if __name__ == '__main__':
    runs_only_when_ran_from_command_line()
