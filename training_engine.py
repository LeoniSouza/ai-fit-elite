import datetime
from database import get_connection

def generate_workout(profile, history=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    goal = profile.get("goal", "Hipertrofia")
    level = profile.get("experience", "Intermediário")
    
    cursor.execute("""
        SELECT id, name, muscle_group, suggested_sets, rep_range, rest_time 
        FROM exercises 
        WHERE goal = ? AND level = ? 
        LIMIT 6
    """, (goal, level))
    
    exercises = cursor.fetchall()
    conn.close()
    
    workout_plan = {
        "workout_name": f"Treino Adaptativo - {goal} ({profile.get('frequency')}x/sem)",
        "exercises": [dict(ex) for ex in exercises],
        "rur_target": "1-2 RIR",
        "notes": "Foque na qualidade de execução."
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
