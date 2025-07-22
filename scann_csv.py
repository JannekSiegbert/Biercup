import csv;
import db

def scan_csv(filename):
    try:
        with open(filename, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                row = {key.strip(): value.strip() for key, value in row.items()}

                print(row)

                person_vorname = row.get('Vorname')
                person_nachname = row.get('Nachname')
                person_name =  f"{person_vorname} {person_nachname}".strip()
                team_name = row.get('Team')

                if person_name and team_name:
                    db.add_person_to_team(person_name.strip(), team_name.strip())
                elif person_name: 
                    db.add_person_to_team(person_name.strip(), "")
                else:
                    print(f"Skipping invalid row: {row}")
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except Exception as e:
        print(f"Error reading CSV: {e}")


if __name__ == "__main__":
    scan_csv("Mappe1.csv")

