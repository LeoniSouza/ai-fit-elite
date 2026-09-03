import sqlite3
import pandas as pd

DB_NAME = "ai_fit.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Desativa temporariamente as chaves estrangeiras para permitir a recriação das tabelas
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS body_metrics;")
    cursor.execute("DROP TABLE IF EXISTS exercises;")
    cursor.execute("DROP TABLE IF EXISTS workouts;")
    cursor.execute("DROP TABLE IF EXISTS workout_exercises;")
    cursor.execute("DROP TABLE IF EXISTS sets_log;")
    
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Recria todas as tabelas na ordem correta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
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
            terms_accepted INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS body_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            muscle_group TEXT,
            equipment TEXT,
            movement_pattern TEXT,
            level TEXT,
            goal TEXT,
            instructions TEXT,
            suggested_sets INTEGER,
            rep_range TEXT,
            rest_time TEXT,
            progression_possible TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            workout_name TEXT,
            completed INTEGER DEFAULT 0,
            feedback_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            exercise_id INTEGER,
            target_sets INTEGER,
            target_reps TEXT,
            target_rir TEXT,
            rest_time TEXT,
            FOREIGN KEY (workout_id) REFERENCES workouts (id),
            FOREIGN KEY (exercise_id) REFERENCES exercises (id)
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
            rpe REAL,
            FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises (id)
        )
    """)

    conn.commit()

    # Popular exercícios padrão se vazio
    cursor.execute("SELECT COUNT(*) FROM exercises")
    if cursor.fetchone()[0] == 0:
        default_exs = [
            ("Supino Reto com Barra", "Peito", "Barra", "Empurrar Horizontal", "Intermediário", "Hipertrofia", "Manter escápulas deprimidas.", 3, "8-12", "90s", "Sim"),
            ("Remada Curvada com Barra", "Costas", "Barra", "Puxar Horizontal", "Intermediário", "Hipertrofia", "Coluna neutra e cotovelos próximos ao corpo.", 3, "8-12", "90s", "Sim"),
            ("Agachamento Livre com Barra", "Pernas", "Barra", "Agachamento", "Intermediário", "Hipertrofia", "Profundidade adequada e joelhos alinhados.", 3, "6-10", "120s", "Sim"),
            ("Desenvolvimento com Halteres", "Ombros", "Halteres", "Empurrar Vertical", "Intermediário", "Hipertrofia", "Evitar hiperlordose lombar.", 3, "8-12", "90s", "Sim"),
            ("Rosca Direta com Barra", "Bíceps", "Barra", "Flexão de Cotovelo", "Intermediário", "Hipertrofia", "Evitar balanço do tronco.", 3, "10-15", "60s", "Sim"),
            ("Tríceps na Polia com Corda", "Tríceps", "Cabos", "Extensão de Cotovelo", "Intermediário", "Hipertrofia", "Cotovelos fixos ao lado do corpo.", 3, "10-15", "60s", "Sim")
        ]
        for ex in default_exs:
            cursor.execute("""
                INSERT INTO exercises (name, muscle_group, equipment, movement_pattern, level, goal, instructions, suggested_sets, rep_range, rest_time, progression_possible)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ex)
        conn.commit()

    conn.close()

def get_analytics_summary(user_id):
    conn = get_connection()
    workouts_df = pd.read_sql_query("SELECT * FROM workouts WHERE user_id = ?", conn, params=(user_id,))
    sets_df = pd.read_sql_query("""
        SELECT sl.*, we.workout_id 
        FROM sets_log sl
        JOIN workout_exercises we ON sl.workout_exercise_id = we.id
    """, conn)
    conn.close()
    
    total_workouts = len(workouts_df[workouts_df["completed"] == 1]) if not workouts_df.empty else 0
    total_volume = (sets_df["weight"] * sets_df["reps"]).sum() if not sets_df.empty else 0
    
    return {
        "total_workouts": total_workouts,
        "total_volume": total_volume,
        "workouts_df": workouts_df,
        "sets_df": sets_df
    }
