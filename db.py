import sqlite3

def setup_database():
    conn = sqlite3.connect('../teamscores.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        team_id INTEGER,
        FOREIGN KEY (team_id) REFERENCES teams (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS beers (
        id INTEGER PRIMARY KEY,
        people_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (people_id) REFERENCES people (id)
    )
    ''')

def get_teams_with_scores():
    conn = sqlite3.connect('teamscores.db')
    c = conn.cursor()
    c.execute('''
        SELECT teams.name, COUNT(beers.id) as beer_count
        FROM teams
        LEFT JOIN people ON teams.id = people.team_id
        LEFT JOIN beers ON people.id = beers.people_id
        GROUP BY teams.id
        ORDER BY beer_count DESC
    ''')
    team_data = c.fetchall()
    conn.close()
    return team_data

def add_beer_for_person(person_name):
    conn = sqlite3.connect('../teamscores.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
        result = cursor.fetchone()

        if result:
            person_id = result[0]
        else:
            cursor.execute("INSERT INTO people (name, team_id) VALUES (?, NULL)", (person_name,))
            person_id = cursor.lastrowid

        cursor.execute("INSERT INTO beers (people_id) VALUES (?)", (person_id,))
        
        conn.commit()
        print(f"Added beer for person '{person_name}'")
        return True

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()
