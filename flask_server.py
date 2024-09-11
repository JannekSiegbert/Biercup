from flask import Flask, render_template
import sqlite3
import os
from db import get_teams_with_scores

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=current_dir,
            static_folder=current_dir,
            static_url_path='')

def get_db_connection():
    conn = sqlite3.connect('teamscores.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update-table')
def update_table():
    team_data = get_teams_with_scores()
    return render_template('table.html', team_data=team_data)

def run_flask_server():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    run_flask_server()

