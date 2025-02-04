from flask import Blueprint, render_template, request
import sqlite3 as sql

data_bp = Blueprint("data", __name__)


@data_bp.route("/")
def data():
    db_file = request.args.get('db', 'db/RWComplete.db')
    with sql.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall() if ('Old' not in table[0]) and ('Backup' not in table[0])]
        tables.sort()
    return render_template("db_view.html", tables=tables)


@data_bp.route("/load_table/<table>")
def load_table(table):
    db_file = request.args.get("db", "RWComplete.db")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    offset = (page - 1) * per_page
    with sql.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT ? OFFSET ?;", (per_page, offset))
        rows = cursor.fetchall()
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]

    return render_template(
        "table_partial.html", table=table, content={"columns": columns, "rows": rows}, page=page
    )


@data_bp.route("/update/<table>/<column>/<pk>", methods=["PATCH"])
def update_cell(table, column, pk):
    new_value = request.form.get("value")
    print(f"Form data: {request.form}")
    db_file = request.args.get("db", "RWComplete.db")

    try:
        with sql.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {table} SET {column} = ? WHERE rowid = ?", (new_value, pk)
            )
            conn.commit()
            return create_input_cell_html(request.path, new_value)
    except Exception as e:
        return str(e), 400


def create_input_cell_html(request_path: str, new_value: str) -> str:
    return f"""
                <td>
                    <div class="editable"
                        hx-target="closest td"
                        hx-patch="{request_path}"
                        contenteditable="true"
                        hx-trigger="blur"
                        hx-swap="outerHTML"
                        oninput="this.parentElement.querySelector('input').value = this.innerText">
                        {new_value}
                    </div>
                    <input type="hidden" name="value" value="{new_value}" />
                </td>
            """
