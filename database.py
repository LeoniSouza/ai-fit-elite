import sqlite3
import pandas as pd

def get_connection():
    conn = sqlite3.connect("ai_fit_elite.db", timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Garante que a tabela users tenha o id 1 como chave primária estrita
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            sex TEXT,
            weight REAL,
            height REAL,
            goal TEXT,
            experience TEXT,
            frequency INTEGER,
            duration INTEGER,
            equipment TEXT,
            sleep_quality TEXT,
            disposition TEXT,
            recovery_quality TEXT,
            restrictions TEXT,
            terms_accepted INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS body_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            weight REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            muscle_group TEXT,
            description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            workout_name TEXT,
            date TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            exercise_id INTEGER,
            target_sets INTEGER,
            target_reps TEXT,
            rest_time INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sets_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_exercise_id INTEGER,
            set_number INTEGER,
            weight REAL,
            reps INTEGER,
            rir REAL,
            rpe REAL
        )
    """)
    
    conn.commit()
    conn.close()

def get_analytics_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM workouts WHERE user_id = ? AND completed = 1", (user_id,))
    row = cursor.fetchone()
    total_workouts = row["total"] if row else 0
    
    cursor.execute("""
        SELECT SUM(sl.weight * sl.reps) as volume 
        FROM sets_log sl 
        JOIN workout_exercises we ON sl.workout_exercise_id = we.id 
        JOIN workouts w ON we.workout_id = w.id 
        WHERE w.user_id = ?
    """, (user_id,))
    vol_row = cursor.fetchone()
    total_volume = vol_row["volume"] if vol_row and vol_row["volume"] else 0.0
    
    conn.close()
    return {
        "total_workouts": total_workouts,
        "total_volume": total_volume
    }
