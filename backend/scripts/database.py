import sqlite3
import json

def connect_db():
    conn = sqlite3.connect("data/ingredients.db")
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
        conn = connect_db()
        c = conn.cursor()
        
        # Create ingredients table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

def get_tags(ingredient_name):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT tags FROM ingredients WHERE name = ?", (ingredient_name.lower(),))
    row = c.fetchone() # get first row -> if no row exists return none
    conn.close()
    if row and row["tags"]:
        return json.loads(row["tags"]) # json to string
    return None

def add_ingredient(ingredient_name, tags):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO ingredients (name, tags)
        VALUES (?, ?)
    ''', (ingredient_name.lower(), json.dumps(tags))) # string to json
    conn.commit()
    conn.close()

def view_all_ingredients():
    """Display all ingredients and their tags in the database"""
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM ingredients ORDER BY name")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("Database is empty - no ingredients found.")
        return []
    
    print(f"\n{'ID':<5} {'Ingredient':<30} {'Tags'}")
    print("-" * 80)
    
    ingredients_list = []
    for row in rows:
        tags = json.loads(row["tags"]) if row["tags"] else []
        print(f"{row['id']:<5} {row['name']:<30} {', '.join(tags)}")
        ingredients_list.append({
            "id": row["id"],
            "name": row["name"],
            "tags": tags
        })
    
    print(f"\nTotal ingredients: {len(rows)}\n")
    return ingredients_list

def clear_all_ingredients():
    """Delete all ingredients from the database"""
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM ingredients")
    conn.commit()
    rows_deleted = c.rowcount
    conn.close()
    print(f"Cleared {rows_deleted} ingredient(s) from the database.")
    return rows_deleted

def preload_database(json_path="data/preload.json"):
    conn = connect_db()
    c = conn.cursor()

    with open(json_path, "r") as f:
        data = json.load(f)

    for ingredient, tags in data.items():
        c.execute("""
            INSERT OR IGNORE INTO ingredients (name, tags)
            VALUES (?, ?)
        """, (ingredient.lower(), json.dumps(tags)))

    conn.commit()
    conn.close()