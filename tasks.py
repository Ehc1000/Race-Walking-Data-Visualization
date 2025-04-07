from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import os
import sqlite3

tasks_bp = Blueprint("tasks", __name__)

TASKS_FILE = "tasks/tasks.json"

with open(TASKS_FILE) as f:
    TASKS = json.load(f)

@tasks_bp.route("/", methods=["GET", "POST"])
def show_tasks():
    return render_template("tasks.html", tasks=TASKS)

DB_FOLDER = "db/"
DB_FILE = "RWComplete.db"
SQL_FOLDER = os.path.dirname("/tasks/")

@tasks_bp.route("/run/<file>", methods=["POST"])
def run_task(file):
    sql_path = os.path.join(SQL_FOLDER, file)
    db_path = os.path.join(DB_FOLDER, DB_FILE)

    try:
        with open(sql_path, 'r') as task_file:
            sql_script = task_file.read()
        with sqlite3.connect(db_path) as conn:
            conn.executescript(sql_script)
    except Exception as e:
        print("Error running task: {}".format(e))

    return redirect(url_for("tasks.show_tasks"))

def main():
    print("This function runs when the script is executed directly!")

if __name__ == "__main__":
    main()
