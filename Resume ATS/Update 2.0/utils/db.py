import sqlite3

DB_PATH = "resumes.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT,
                experience TEXT,
                education TEXT,
                score REAL,
                status TEXT DEFAULT 'Pending',
                notes TEXT
            )
        ''')

def insert_resume(file_name, data):
    with connect_db() as conn:
        conn.execute('''
            INSERT INTO resumes (file_name, name, email, phone, skills, experience, education, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_name, data['name'], data['email'], data['phone'], data['skills'], data['experience'], data['education'], data['score']))
        conn.commit()

def get_resume_count():
    with connect_db() as conn:
        return conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]

def get_avg_match_score():
    with connect_db() as conn:
        row = conn.execute("SELECT AVG(score) FROM resumes").fetchone()
        return row[0] if row else None
