import sqlite3
import hashlib
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    # Interviews table
    c.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            candidate_name TEXT,
            cv_summary TEXT,
            question TEXT,
            answer TEXT,
            communication_score REAL,
            technical_score REAL,
            confidence_score REAL,
            overall_score REAL,
            emotion TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(full_name, email, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Hash password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        c.execute('''
            INSERT INTO users (full_name, email, password, created_at)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, hashed, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Email already exists!"

def login_user(email, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    c.execute('''
        SELECT id, full_name, email 
        FROM users 
        WHERE email = ? AND password = ?
    ''', (email, hashed))
    
    user = c.fetchone()
    conn.close()
    
    if user:
        return True, {"id": user[0], "full_name": user[1], "email": user[2]}
    return False, "Invalid email or password!"
def save_interview(candidate_name, cv_summary, question,
                   answer, communication_score, technical_score,
                   confidence_score, overall_score, emotion):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO interviews (
            candidate_name, cv_summary, question, answer,
            communication_score, technical_score,
            confidence_score, overall_score, emotion, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        candidate_name, cv_summary, question, answer,
        communication_score, technical_score,
        confidence_score, overall_score, emotion,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_all_interviews():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM interviews ORDER BY timestamp DESC')
    results = c.fetchall()
    conn.close()
    return results

def get_average_scores():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT
            AVG(communication_score),
            AVG(technical_score),
            AVG(confidence_score),
            AVG(overall_score)
        FROM interviews
    ''')
    result = c.fetchone()
    conn.close()
    return result