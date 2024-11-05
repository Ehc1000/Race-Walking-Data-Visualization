from flask import Blueprint, render_template, request

import common as cmn

# from weasyprint import HTML

# https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#python-library
# Did some googling, and it seemed weasyprint was a good html to pdf library, but
# it requires some more installing than just pip, so not bothering with for now.
# import pdfkit
# https://pypi.org/project/pdfkit/
# Tried pdfkit after writing this, but it also requires some extra installation stuff.
# So not going to check in any code that uses either yet. Will mess around and do more research.

tables_bp = Blueprint('tables', __name__)


@tables_bp.route('/')
def display_table():
    # converts the multidict of arguments to a normal dict
    # note that this will keep only the first value for each key
    # whereas a multidict can have a multiple values for each key
    query_params = request.args.to_dict()

    query_file = query_params.pop('query', 'AthleteInfractions.sql')
    db_file = query_params.pop('db', 'RWComplete.db')
    table_style = query_params.pop('style', 'default-style')

    # collects all the needed named parameter values for the query, setting to a default if not specified
    # in the http request query params
    query_params = {k: query_params.get(k, cmn.PARAMETER_DEFAULTS.get(k)) for k in cmn.get_sql_parameters(query_file)}

    df = cmn.df_from_labeled_query(query_file, db_file, params=query_params)

    html_table = df.to_html(classes=table_style, index=False)
    html_content = render_template('tables.html', table=html_table)
    # pdfkit line:
    # pdfkit.from_string(html_content, '/output/test.pdf')
    # weasyprint line:
    # pdf = HTML(string=html_table).write_pdf(stylesheets=['static/tables.css'])
    # this will not work unless you have the stuff locally installed
    # so imma just comment it out

    return html_content


# We can also treat this file as a command line script and forget we are using flask.
def main():
    print("This function runs when the script is executed directly!")


if __name__ == '__main__':
    main()
