import sqlite3

DB_PATH = "recruiter.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_recruiter_db():
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recruiters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                role TEXT DEFAULT 'recruiter'
            )
        ''')

def authenticate_user(username, password):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM recruiters WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()

def register_user(username, password, email, role):
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO recruiters (username, password, email, role) VALUES (?, ?, ?, ?)",
                           (username, password, email, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
