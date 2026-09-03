import datetime
from database import get_connection

def determine_weekly_split(frequency, goal):
    """Define a divisão semanal de acordo com a frequência disponível do aluno."""
    if frequency <= 2:
        return ["Full Body A", "Full Body B"]
    elif frequency == 3:
        return ["Full Body A", "Full Body B", "Full Body C"]
    elif frequency == 4:
        return ["Upper A (Superior)", "Lower A (Inferior)", "Upper B (Superior)", "Lower B (Inferior)"]
    elif frequency == 5:
        return ["Upper A", "Lower A", "Upper B", "Lower B", "Sessão Complementar / Core"]
    else:
        return ["Push (Empurrar)", "Pull (Puxar)", "Legs (Pernas)", "Upper (Superior)", "Lower (Inferior)", "Full Body Técnico"]

def generate_workout(profile, history=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    goal = profile.get("goal", "Hipertrofia")
    level = profile.get("experience", "Intermediário")
    frequency = profile.get("frequency", 4)
    
    # Seleção inteligente baseada em grupamentos
    cursor.execute("""
        SELECT id, name, muscle_group, suggested_sets, rep_range, rest_time 
        FROM exercises 
        WHERE goal = ? AND level = ? 
        LIMIT 6
    """, (goal, level))
    
    exercises = cursor.fetchall()
    conn.close()
    
    splits = determine_weekly_split(frequency, goal)
    # Seleciona o treino do ciclo com base no histórico de treinos concluídos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM workouts WHERE user_id = 1 AND completed = 1")
    completed_count = cursor.fetchone()[0]
    conn.close()
    
    current_split_name = splits[completed_count % len(splits)]
    
    workout_plan = {
        "workout_name": f"{current_split_name} - Foco: {goal}",
        "exercises": [dict(ex) for ex in exercises],
        "rur_target": "1-2 RIR",
        "notes": f"Nível de Experiência: {level}. Priorize controle excêntrico e execução técnica."
    }
    return workout_plan

def save_generated_workout(user_id, workout_plan):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()
    
    cursor.execute("""
        INSERT INTO workouts (user_id, date, workout_name, completed)
        VALUES (?, ?, ?, 0)
    """, (user_id, today, workout_plan["workout_name"]))
    workout_id = cursor.lastrowid
    
    for ex in workout_plan["exercises"]:
        cursor.execute("SELECT id FROM exercises WHERE name = ?", (ex["name"],))
        res = cursor.fetchone()
        ex_id = res["id"] if res else 1
        
        cursor.execute("""
            INSERT INTO workout_exercises (workout_id, exercise_id, target_sets, target_reps, target_rir, rest_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (workout_id, ex_id, ex["suggested_sets"], ex["rep_range"], "2 RIR", ex["rest_time"]))
        
    conn.commit()
    conn.close()
    return workout_id
