def analyze_progression(exercise_history):
    if not exercise_history or len(exercise_history) < 2:
        return "MAINTAIN_LOAD", "Dados insuficientes. Mantenha a carga."
    
    last_session = exercise_history[-1]
    avg_rir = sum([s.get("rir", 2) for s in last_session]) / len(last_session) if last_session else 2
    max_reps_hit = all([s.get("reps", 0) >= 12 for s in last_session])
    
    if max_reps_hit and avg_rir >= 2:
        return "INCREASE_LOAD", "Atingiu o topo da faixa de repetições. Aumente a carga levemente (2-5%)."
    elif avg_rir > 3:
        return "INCREASE_REPS", "Reserva alta. Adicione repetições mantendo a carga."
    
    return "MAINTAIN_LOAD", "Desempenho estável. Mantenha a carga."
