from flask import Blueprint

data_bp = Blueprint('data', __name__)

# The data modification section. Making a note here for those reading this to google the datatables library,
# to do ninety percent of the work for you.
# https://datatables.net/

@data_bp.route('/')
def data():
    return 'Main page for what will be the data modifier section!'

# We can also treat this file as a command line script and forget we are using flask.
def runs_only_when_ran_from_command_line():
    print("This function runs when the script is executed directly!")

if __name__ == '__main__':
    runs_only_when_ran_from_command_line()
