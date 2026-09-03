def get_initial_exercises():
    base_names = {
        "Peito": [("Supino Reto com Barra", "Empurrar Horizontal", "Barra"), 
                  ("Supino Inclinado com Halteres", "Empurrar Inclinado", "Halteres"), 
                  ("Crucifixo na Polia", "Isolamento", "Cabos"),
                  ("Flexão de Braço", "Empurrar Horizontal", "Peso Corporal")],
        "Costas": [("Puxada Alta na Polia", "Puxar Vertical", "Cabos"),
                   ("Remada Curvada com Barra", "Puxar Horizontal", "Barra"),
                   ("Remada Baixa no Cabo", "Puxar Horizontal", "Cabos"),
                   ("Barra Fixa Pronada", "Puxar Vertical", "Peso Corporal")],
        "Pernas": [("Agachamento Livre com Barra", "Agachamento", "Barra"),
                   ("Leg Press 45º", "Agachamento", "Máquina"),
                   ("Cadeira Extensora", "Extensão de Joelho", "Máquina"),
                   ("Mesa Flexora", "Flexão de Joelho", "Máquina")],
        "Ombros": [("Desenvolvimento com Halteres", "Empurrar Vertical", "Halteres"),
                   ("Elevação Lateral com Halteres", "Isolamento", "Halteres")],
        "Bíceps": [("Rosca Direta com Barra W", "Flexão de Cotovelo", "Barra"),
                   ("Rosca Alternada com Halteres", "Flexão de Cotovelo", "Halteres")],
        "Tríceps": [("Tríceps Corda na Polia", "Extensão de Cotovelo", "Cabos"),
                   ("Tríceps Testa com Barra W", "Extensão de Cotovelo", "Barra")],
        "Core": [("Prancha Abdominal", "Isometria", "Peso Corporal"),
                 ("Abdominal Supra no Colchonete", "Flexão de Tronco", "Peso Corporal")]
    }

    exercises = []
    for muscle, items in base_names.items():
        for name, pattern, eq in items:
            for level in ["Iniciante", "Intermediário", "Avançado"]:
                for goal in ["Hipertrofia", "Emagrecimento e definição", "Condicionamento físico"]:
                    exercises.append({
                        "name": f"{name} ({level[0]}-{goal[:3]})",
                        "muscle_group": muscle,
                        "equipment": eq,
                        "movement_pattern": pattern,
                        "level": level,
                        "goal": goal,
                        "instructions": f"Manter postura firme e execução controlada no exercício de {name.lower()}.",
                        "suggested_sets": 3 if level == "Iniciante" else 4,
                        "rep_range": "8-12" if goal == "Hipertrofia" else "12-15",
                        "rest_time": "90s",
                        "progression_possible": "Sim"
                    })
    return exercises
