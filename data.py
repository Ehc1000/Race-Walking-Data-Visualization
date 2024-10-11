from flask import Blueprint

data_bp = Blueprint('data', __name__)

# The data modification section. Making a note here for those reading this to google the datatables library,
# to do ninety percent of the work for you.
# https://datatables.net/

@data_bp.route('/')
def data():
    return 'Main page for what will be the data modifier section!'
