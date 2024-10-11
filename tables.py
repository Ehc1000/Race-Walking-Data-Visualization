from flask import Blueprint

tables_bp = Blueprint('tables', __name__)

# I guess here we just, display some tables in a format that will look good saved as a pdf?
# Seems simple enough. I'll probably just have a navbar or something simple to pick which table you want to see,
# a button for each to download as pdf, and a button to download all of them as a big pdf altogether.
# The tables will just query the database real time.

@tables_bp.route('/')
def graphs():
    return 'Main page for what will be the tables section!'

# We can also treat this file as a command line script and forget we are using flask.
def runs_only_when_ran_from_command_line():
    print("This function runs when the script is executed directly!")

if __name__ == '__main__':
    runs_only_when_ran_from_command_line()
