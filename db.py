import sqlite3

def setup_database():
    conn = sqlite3.connect('teamscores.db')
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

    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())

if __name__ == "__main__":
    setup_database()

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
    conn = sqlite3.connect('teamscores.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
        result = cursor.fetchone()

        if result:
            person_id = result[0]
        else:
            print("Person will be created")
            cursor.execute("INSERT INTO people (name, team_id) VALUES (?, NULL)", (person_name,))
            person_id = cursor.lastrowid

        cursor.execute("INSERT INTO beers (people_id) VALUES (?)", (person_id,))
        
        conn.commit()
        print(f"Added beer for person '{person_name}''{person_id}'")
        return True

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def add_person_to_team(person_name, team_name):
    conn = sqlite3.connect('teamscores.db')
    cursor = conn.cursor()

    try:
        # Get or create the person
        cursor.execute("SELECT id, team_id FROM people WHERE name = ?", (person_name,))
        person = cursor.fetchone()
        if person:
            person_id, existing_team_id = person
            print(f"Found existing person '{person_name}' with ID {person_id}")
        else:
            cursor.execute("INSERT INTO people (name, team_id) VALUES (?, NULL)", (person_name,))
            person_id = cursor.lastrowid
            existing_team_id = None
            print(f"Created person '{person_name}' with ID {person_id}")
        
        if team_name == "":
            return;
        # Get or create the team
        cursor.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
        team = cursor.fetchone()
        if team:
            team_id = team[0]
            print(f"Found existing team '{team_name}' with ID {team_id}")
        else:
            cursor.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
            team_id = cursor.lastrowid
            print(f"Created team '{team_name}' with ID {team_id}")

        # Update the person’s team_id if not already set or different
        if existing_team_id != team_id:
            cursor.execute("UPDATE people SET team_id = ? WHERE id = ?", (team_id, person_id))
            print(f"Assigned person '{person_name}' to team '{team_name}'")

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()
