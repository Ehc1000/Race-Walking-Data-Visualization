import os

from flask import Blueprint, render_template, request, send_file

import common as cmn

try:
    # https://pypi.org/project/pdfkit/
    import pdfkit
except ImportError as ie:
    print(ie.msg)
    pdfkit = False

tables_bp = Blueprint("tables", __name__)


def generate_table():
    # converts the multidict of arguments to a normal dict
    # note that this will keep only the first value for each key
    # whereas a multidict can have a multiple values for each key
    query_params = request.args.to_dict()
    query_file = query_params.pop("query", "AthleteInfractions.sql")
    db_file = query_params.pop("db", "RWComplete.db")
    table_style = query_params.pop("style", "table")

    # collects all the needed named parameter values for the query, setting to a default if not specified
    # in the http request query params
    needed_params = cmn.get_labeled_sql_parameters(query_file)
    query_params = {k: query_params.get(k, cmn.PARAMETER_DEFAULTS.get(k)) for k in needed_params}
    try:
        df = cmn.df_from_labeled_query(query_file, db_file, params=query_params)
        html_table = df.to_html(classes=table_style, index=False)
    except Exception as e:
        if db_file == "DrexelRaceWalking.db":
            html_table = "<p>The Drexel race walking database does not support this query.</p>"
        else:
            html_table = f"<p>Query failed for the following reason:</p><p>{str(e)}</p>"
    return needed_params, html_table, db_file, query_file, table_style, query_params


@tables_bp.route("/download_pdf")
def download_pdf():
    if not pdfkit:
        return "PDF generation is not available because pdfkit or wkhtmltopdf is not installed."
    # would technically be better if it didn't rerun the query and making the table when the user
    # hits the download button but who cares
    needed_params, html_table, db_file, query_file, table_style, query_params = generate_table()
    pdf_name = f"{db_file}_{query_file}_{table_style}.pdf"
    pdf_output_path = f"{cmn.TMP_FOLDER}{pdf_name}"
    os.makedirs(cmn.TMP_FOLDER, exist_ok=True)
    css_files = [
        "static/bootstrap/css/bootstrap.css",
        "static/tables.css"
    ]

    pdfkit.from_string(html_table, pdf_output_path, css=css_files)
    return send_file(pdf_output_path, as_attachment=True, download_name=pdf_name)


@tables_bp.route("/")
def display_table():
    needed_params, html_table, db_file, query_file, table_style, query_params = generate_table()
    query_options = cmn.get_all_labeled_queries()
    db_options = cmn.get_dbs()
    races = cmn.df_from_labeled_query("AllRaces.sql", "RWComplete.db").to_dict(orient="records")

    query_params = {k: str(v) for k, v in query_params.items() if v is not None}
    for race in races:
        race['IDRace'] = str(race['IDRace'])

    return render_template(
        "tables.html",
        table=html_table,
        table_style=table_style,
        db_file=db_file,
        query_file=query_file,
        db_options=db_options,
        query_options=query_options,
        needed_parameters=needed_params,
        query_params=query_params,
        races=races
    )


def main():
    print("This function runs when the script is executed directly!")


if __name__ == "__main__":
    main()
