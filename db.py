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
    c.execute('''SELECT 
    teams.name, 
    COUNT(beers.id) as beer_count,
    CASE 
        WHEN COUNT(DISTINCT people.id) = 0 THEN 0
        ELSE ROUND(CAST(COUNT(beers.id) AS FLOAT) / COUNT(DISTINCT people.id), 1)
    END as average
FROM teams
LEFT JOIN people ON teams.id = people.team_id
LEFT JOIN beers ON people.id = beers.people_id
GROUP BY teams.id
ORDER BY beer_count DESC
''')
    team_data = c.fetchall()
    conn.close()
    return team_data


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_teams():
    conn = sqlite3.connect('teamscores.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute('SELECT id, name FROM teams')
    data = c.fetchall()
    conn.close()
    return data

def get_people():
    conn = sqlite3.connect('teamscores.db')
    c = conn.cursor()
    conn.row_factory = dict_factory
    c.execute('''
        SELECT people.id, people.name, COUNT(beers.id) as score, people.team_id
        FROM people
        LEFT JOIN beers ON people.id = beers.people_id
        GROUP BY people.id
        ORDER BY score DESC
    ''')
    data = c.fetchall()
    conn.close()
    return data

def  get_people_by_id(id): 
    conn = sqlite3.connect('teamscores.db')
    c = conn.cursor()
    conn.row_factory = dict_factory
    c.execute(f'SELECT * FROM people WHERE id = {id}')
    data = c.fetchone()
    conn.close()
    return data


def update_people(id, team_id): 
    conn = sqlite3.connect('teamscores.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE people 
            SET team_id = ?             
            WHERE id = ?
        ''', (team_id, id))
        conn.commit()
        updated_rows = c.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        updated_rows = 0
    finally:
        conn.close()
    return updated_rows > 0


def get_recent_beers():
    conn = sqlite3.connect('teamscores.db')
    c = conn.cursor()
    conn.row_factory = dict_factory
    c.execute('''
        SELECT people.name, 
               COALESCE(teams.name, 'no team') as team_name
        FROM beers
        JOIN people ON beers.people_id = people.id
        LEFT JOIN teams ON people.team_id = teams.id
        ORDER BY beers.timestamp DESC
        LIMIT 5
    ''')
    data = c.fetchall()
    conn.close()
    return data


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
