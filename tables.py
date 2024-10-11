from flask import Blueprint, render_template, request
from common import df_from_query

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
    # The below get query params i.e. the key value pairs after a ? in the url.
    query_file = request.args.get('query', 'AthleteInfractions.sql')
    db_file = request.args.get('db', 'RWComplete.db')
    table_style = request.args.get('style', 'default-style')

    df = df_from_query(query_file, db_file)
    html_table = df.to_html(classes=table_style, index=False)
    html_content = render_template('tables.html', table=html_table)
    # pdfkit line:
    # pdfkit.from_string(html_content, '/output/test.pdf')
    # weasyprint line:
    # pdf = HTML(string=html_table).write_pdf(stylesheets=['static/tables.css'])

    return html_content


# We can also treat this file as a command line script and forget we are using flask.
def main():
    print("This function runs when the script is executed directly!")


if __name__ == '__main__':
    main()
