from flask import Flask, render_template
from data import data_bp
from tables import tables_bp
from graphs import graphs_bp
from webscraper import webscraper_bp

app = Flask(__name__)

# This blueprints feature is not usually necessary,
# but it's what you do with flask if you want to split up your endpoint functions
# into separate files, which I figure we ought to do to limit merge conflicts and such.
# https://flask.palletsprojects.com/en/3.0.x/blueprints/
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(tables_bp, url_prefix='/tables')
app.register_blueprint(graphs_bp, url_prefix='/graphs')
app.register_blueprint(webscraper_bp, url_prefix='/webscraper')

# This is how flask works. You have an annotation specifying the endpoint
# a function corresponds to, and then inside it can forget you're in flask land completely if you want,
# and then whatever you return, whether it be just a string or some raw html or a reference to a html file
# in the templates folder will be the http response to the call.
# https://flask.palletsprojects.com/en/3.0.x/quickstart/#a-minimal-application
# You will specify endpoints identically bar calling the blueprint instead
# of the root app.
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)