from flask import Blueprint

tables_bp = Blueprint('tables', __name__)

# I guess here we just, display some tables in a format that will look good saved as a pdf?
# Seems simple enough. I'll probably just have a navbar or something simple to pick which table you want to see,
# a button for each to download as pdf, and a button to download all of them as a big pdf altogether.
# The tables will just query the database real time.

@tables_bp.route('/')
def graphs():
    return 'Main page for what will be the tables section!'
