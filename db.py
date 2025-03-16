import json
import os

DB_FILE = 'database.json'


def load_db():
    if not os.path.exists(DB_FILE):
        return {'medicines': []}

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {'medicines': []}
            f.seek(0)
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {'medicines': []}


def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_stock(med_name, dose):
    db = load_db()
    for med in db['medicines']:
        if med['name'] == med_name:
            med['stock'] -= dose
            save_db(db)
            return med['stock']
    return None
