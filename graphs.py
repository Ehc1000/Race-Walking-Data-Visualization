from flask import Blueprint

graphs_bp = Blueprint('graphs', __name__)

# The graphs section. Howe want to do this up in the air.

@graphs_bp.route('/')
def graphs():
    return 'Main page for what will be the graphs section!'
