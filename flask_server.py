from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import os
from db import get_teams_with_scores, get_teams, get_people, get_recent_beers, update_people

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
    return redirect(url_for('teams'))

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/team-table')
def team_table():
    team_data = get_teams_with_scores()
    return render_template('teams_table.html', team_data=team_data)

@app.route('/recent-entries')
def recent_entries():
    recent_people = get_recent_beers()
    return render_template('recent_entries.html', entries=recent_people)

@app.route('/people')
def persons():
    return render_template('people.html')

@app.route('/people-table')
def user_table():
    people = get_people()
    teams = get_teams()
    return render_template('people_table.html', people=people, all_teams=teams)

def run_flask_server():
    app.run(debug=True, use_reloader=False)

@app.route('/change-team', methods=['POST'])
def change_team():
    person_id = request.form.get('person_id')
    new_team_id = request.form.get('team_id')
    
    update_people(person_id, new_team_id)
    return "Team updated successfully", 200

if __name__ == '__main__':
    run_flask_server()

