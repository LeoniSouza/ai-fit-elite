def analyze_progression(exercise_history):
    """
    Motor determinístico de decisão analítica pós-treino.
    Avalia se houve atingimento do topo da faixa de repetições, RIR adequado ou queda de desempenho.
    """
    if not exercise_history or len(exercise_history) < 2:
        return "MAINTAIN_LOAD", "Fase inicial de consolidação. Mantenha a carga com foco na execução técnica."
    
    last_session = exercise_history[-1]
    avg_rir = sum([s.get("rir", 2) for s in last_session]) / len(last_session) if last_session else 2
    max_reps_hit = all([s.get("reps", 0) >= 12 for s in last_session]) # Topo de faixa padrão
    
    # Verificação de queda de desempenho recente
    prev_session = exercise_history[-2] if len(exercise_history) >= 2 else last_session
    avg_reps_last = sum([s.get("reps", 0) for s in last_session]) / len(last_session) if last_session else 0
    avg_reps_prev = sum([s.get("reps", 0) for s in prev_session]) / len(prev_session) if prev_session else 0

    if avg_reps_last < avg_reps_prev * 0.9:
        return "MONITOR_FATIGUE", "Queda de desempenho detectada em relação à sessão anterior. Avaliar recuperação e sono, sem alterar o programa precipitadamente."

    if max_reps_hit and avg_rir >= 2:
        return "INCREASE_LOAD", "Objetivo atingido com excelência! Carga pronta para progressão moderada (2% a 5% de acréscimo)."
    elif avg_rir > 3:
        return "INCREASE_REPS", "Reserva de esforço alta (RIR > 3). O estímulo ficou abaixo do planejado; adicione repetições mantendo a carga."
    elif avg_rir < 1:
        return "MAINTAIN_LOAD", "Proximidade extrema da falha com esgotamento. Mantenha a carga atual para consolidar a adaptação."
    
    return "MAINTAIN_LOAD", "Progresso estável dentro dos parâmetros ótimos. Regra principal: não alterar o que está funcionando."
