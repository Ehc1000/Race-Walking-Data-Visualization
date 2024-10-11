from flask import Blueprint

graphs_bp = Blueprint('graphs', __name__)

# The graphs section. Howe want to do this up in the air.

@graphs_bp.route('/')
def graphs():
    return 'Main page for what will be the graphs section!'

# We can also treat this file as a command line script and forget we are using flask.
def runs_only_when_ran_from_command_line():
    print("This function runs when the script is executed directly!")

if __name__ == '__main__':
    runs_only_when_ran_from_command_line()