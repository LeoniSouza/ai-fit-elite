import pandas as pd
from database import get_connection

def save_user_profile(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica se já existe algum perfil cadastrado
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        # Atualiza o perfil existente garantindo o ID correto
        cursor.execute("""
            UPDATE users SET 
                name = ?, age = ?, sex = ?, weight = ?, height = ?, 
                goal = ?, experience = ?, frequency = ?, duration = ?, 
                equipment = ?, sleep_quality = ?, disposition = ?, 
                recovery_quality = ?, restrictions = ?, terms_accepted = ?
            WHERE id = ?
        """, (
            data["name"], data["age"], data["sex"], data["weight"], data["height"],
            data["goal"], data["experience"], data["frequency"], data["duration"], data["equipment"],
            data["sleep_quality"], data["disposition"], data["recovery_quality"], data["restrictions"], 
            data["terms_accepted"], user["id"]
        ))
    else:
        # Insere o primeiro perfil se a tabela estiver vazia
        cursor.execute("""
            INSERT INTO users (name, age, sex, weight, height, goal, experience, frequency, duration, equipment, sleep_quality, disposition, recovery_quality, restrictions, terms_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"], data["age"], data["sex"], data["weight"], data["height"],
            data["goal"], data["experience"], data["frequency"], data["duration"], data["equipment"],
            data["sleep_quality"], data["disposition"], data["recovery_quality"], data["restrictions"], data["terms_accepted"]
        ))
        
    conn.commit()
    conn.close()
            data["name"], data["age"], data["sex"], data["weight"], data["height"],
            data["goal"], data["experience"], data["frequency"], data["duration"], data["equipment"],
            data["sleep_quality"], data["disposition"], data["recovery_quality"], data["restrictions"], data["terms_accepted"]
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
