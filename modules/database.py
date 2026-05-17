import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            cv_summary TEXT,
            question TEXT,
            answer TEXT,
            communication_score REAL,
            technical_score REAL,
            confidence_score REAL,
            overall_score REAL,
            emotion TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

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