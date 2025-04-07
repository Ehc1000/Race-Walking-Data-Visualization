from flask import Flask, render_template
from data import data_bp
from reports import reports_bp
from tasks import tasks_bp
from graphs import graphs_bp
from webscraper import webscraper_bp

app = Flask(__name__)

blueprints = [
    (graphs_bp, "Data Graphs", "/graphs"),
    (reports_bp, "Report Generator", "/reports"),
    (webscraper_bp, "Web Scraper", "/webscraper"),
    (tasks_bp, "Task Runner", "/tasks"),
    (data_bp, "Data Modifier", "/data")
]

nav_items = []
for bp, label, prefix in blueprints:
    app.register_blueprint(bp, url_prefix=prefix)
    nav_items.append({'label': label, 'url': prefix})

app.jinja_env.globals['nav_items'] = nav_items

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)