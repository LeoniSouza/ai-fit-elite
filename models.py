import pandas as pd
from database import get_connection

def save_user_profile(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    cursor.execute("""
        INSERT INTO users (name, age, sex, weight, height, goal, experience, frequency, duration, equipment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["age"], data["sex"], data["weight"], data["height"],
        data["goal"], data["experience"], data["frequency"], data["duration"], data["equipment"]
    ))
    conn.commit()
    conn.close()

def get_user_profile():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_body_metric(user_id, date, weight):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO body_metrics (user_id, date, weight) VALUES (?, ?, ?)", (user_id, date, weight))
    cursor.execute("UPDATE users SET weight = ? WHERE id = ?", (weight, user_id))
    conn.commit()
    conn.close()

def get_body_metrics(user_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM body_metrics WHERE user_id = ? ORDER BY date ASC", conn, params=(user_id,))
    conn.close()
    return df
