import streamlit as st
import datetime
from database import init_db, get_connection, get_analytics_summary
from models import save_user_profile, get_user_profile, add_body_metric, get_body_metrics
from training_engine import generate_workout, save_generated_workout
from progression_engine import analyze_progression
from safety import check_safety_guidelines

st.set_page_config(page_title="AI FIT ELITE", page_icon="⚡", layout="wide")

init_db()

st.sidebar.title("⚡ AI FIT ELITE")
profile = get_user_profile()

menu = st.sidebar.radio("Navegação", [
    "Dashboard", "Meu Perfil", "Treino de Hoje", "Histórico", "Evolução", "Biblioteca de Exercícios", "Configurações"
])

safety_input = st.sidebar.text_input("Relatar dor ou condição física:", placeholder="Ex: Senti dor persistente no joelho...")
if safety_input:
    is_unsafe, warning_msg = check_safety_guidelines(safety_input)
    if is_unsafe:
        st.sidebar.error(warning_msg)

if menu == "Dashboard":
    st.title("📊 Painel de Controle Principal")
    if not profile:
        st.warning("⚠️ Configure seu perfil completo na aba **Meu Perfil** para iniciar a prescrição.")
    else:
        summary = get_analytics_summary(1)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Treinos Realizados", summary["total_workouts"])
        col2.metric("Volume Total (kg)", f"{summary['total_volume']:,.1f}")
        col3.metric("Peso Atual", f"{profile.get('weight', 0)} kg")
        col4.metric("Objetivo", profile.get("goal", "Hipertrofia"))
        
        st.divider()
        st.subheader("💡 Status do Motor de Decisão")
        st.success(f"Aluno classificado como **{profile.get('experience', 'Intermediário')}** com foco em **{profile.get('goal')}**. O sistema está operando com ciclo determinístico ativo.")

elif menu == "Meu Perfil":
    st.title("👤 Avaliação Inicial e Perfil do Aluno")
    curr = get_user_profile() or {}
    
    with st.form("profile_form"):
        name = st.text_input("Nome Completo", value=curr.get("name", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Idade", value=curr.get("age", 25))
        with c2:
            sex = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"], index=0)
        with c3:
            weight = st.number_input("Peso (kg)", value=curr.get("weight", 70.0))
            
        c4, c5 = st.columns(2)
        with c4:
            height = st.number_input("Altura (m)", value=curr.get("height", 1.75))
        with c5:
            goal = st.selectbox("Objetivo Principal", [
                "Hipertrofia", 
                "Emagrecimento e definição", 
                "Condicionamento físico",
                "Treinamento de força",
                "Desenvolvimento físico geral"
            ])
            
        experience = st.selectbox("Nível de Experiência com Musculação", ["Iniciante", "Intermediário", "Avançado"])
        
        c6, c7 = st.columns(2)
        with c6:
            frequency = st.slider("Dias disponíveis por semana", 1, 7, value=curr.get("frequency", 4))
        with c7:
            duration = st.slider("Tempo disponível por sessão (min)", 30, 120, value=curr.get("duration", 60))
            
        equipment = st.selectbox("Equipamentos / Local de Treinamento", ["Academia completa", "Home Gym", "Peso Corporal"])
        
        st.divider()
        st.subheader("🛌 Anamnese de Recuperação e Estilo de Vida")
        c8, c9, c10 = st.columns(3)
        with c8:
            sleep = st.selectbox("Qualidade percebida do sono", ["Excelente", "Boa", "Regular", "Ruim"])
        with c9:
            disposition = st.selectbox("Nível habitual de disposição", ["Alto", "Moderado", "Baixo"])
        with c10:
            recovery = st.selectbox("Qualidade percebida da recuperação", ["Rápida", "Normal", "Lenta"])
            
        restrictions = st.text_area("Restrições, lesões ou limitações informadas", value=curr.get("restrictions", ""))
        
        if st.form_submit_button("Salvar Perfil e Atualizar Motor"):
            save_user_profile({
                "name": name, "age": age, "sex": sex, "weight": weight, "height": height,
                "goal": goal, "experience": experience, "frequency": frequency,
                "duration": duration, "equipment": equipment, "sleep_quality": sleep,
                "disposition": disposition, "recovery_quality": recovery, "restrictions": restrictions
            })
            st.success("Perfil de treinamento atualizado com sucesso no banco de dados!")
            st.rerun()

elif menu == "Treino de Hoje":
    st.title("🏋️ Execução do Treino e Registro de Desempenho")
    if not profile:
        st.warning("Cadastre seu perfil na aba **Meu Perfil** primeiro.")
    else:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM workouts WHERE user_id = 1 AND completed = 0 ORDER BY id DESC LIMIT 1")
        workout_row = cursor.fetchone()
        
        if not workout_row:
            st.info("Nenhum treino ativo no momento. O motor determinístico está pronto para estruturar sua próxima sessão.")
            if st.button("Gerar Próximo Treino Adaptativo"):
                plan = generate_workout(profile)
                save_generated_workout(1, plan)
                st.success("Ficha de treino gerada com sucesso com base no seu objetivo e histórico!")
                st.rerun()
        else:
            st.subheader(f"Sessão: {workout_row['workout_name']} | Data: {workout_row['date']})")
            
            cursor.execute("""
                SELECT we.id as we_id, e.name, we.target_sets, we.target_reps, we.rest_time 
                FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id
                WHERE we.workout_id = ?
            """, (workout_row["id"],))
            exercises = cursor.fetchall()
            
            for ex in exercises:
                with st.expander(f"🔹 {ex['name']} | Séries: {ex['target_sets']} | Alvo Reps: {ex['target_reps']} | Descanso: {ex['rest_time']}"):
                    for s in range(1, ex["target_sets"] + 1):
                        c1, c2, c3, c4 = st.columns(4)
                        w = c1.number_input(f"Carga (kg) S{s}", value=0.0, key=f"w_{ex['we_id']}_{s}")
                        r = c2.number_input(f"Repetições S{s}", value=10, key=f"r_{ex['we_id']}_{s}")
                        rir = c3.number_input(f"RIR S{s}", value=2.0, key=f"rir_{ex['we_id']}_{s}")
                        done = c4.checkbox(f"Concluir S{s}", key=f"chk_{ex['we_id']}_{s}")
                        if done:
                            cursor.execute("INSERT OR REPLACE INTO sets_log (workout_exercise_id, set_number, weight, reps, rir, rpe) VALUES (?, ?, ?, ?, ?, ?)", (ex["we_id"], s, w, r, rir, 10 - rir))
                            conn.commit()
            
            st.divider()
            feedback_notes = st.text_input("Observações da sessão (ex: cansaço acumulado, foco alto):")
            
            if st.button("Finalizar Treino e Executar Motor de Análise"):
                cursor.execute("UPDATE workouts SET completed = 1, feedback_notes = ? WHERE id = ?", (feedback_notes, workout_row["id"]))
                conn.commit()
                st.success("Treino finalizado! O motor determinístico registrou os dados e ajustará o próximo ciclo.")
                st.balloons()
                st.rerun()
        conn.close()

elif menu == "Histórico":
    st.title("📜 Histórico de Sessões Concluídas")
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, date, workout_name, feedback_notes, completed FROM workouts WHERE user_id = 1 ORDER BY date DESC", conn)
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum histórico registrado até o momento.")

elif menu == "Evolução":
    st.title("📈 Acompanhamento de Evolução e Cargas")
    with st.form("met_form"):
        nw = st.number_input("Atualizar Peso Corporal (kg)", value=profile.get("weight", 70.0) if profile else 70.0)
        if st.form_submit_button("Salvar Medição"):
            add_body_metric(1, datetime.date.today().isoformat(), nw)
            st.success("Métrica salva com sucesso!")
            st.rerun()
    df_m = get_body_metrics(1)
    if not df_m.empty:
        st.line_chart(df_m, x="date", y="weight")
    else:
        st.info("Adicione medições de peso corporal para visualizar a curva de evolução.")

elif menu == "Biblioteca de Exercícios":
    st.title("📚 Biblioteca de Exercícios Estruturados")
    conn = get_connection()
    df_ex = pd.read_sql_query("SELECT name, muscle_group, equipment, level, goal, rep_range FROM exercises", conn)
    conn.close()
    st.dataframe(df_ex, use_container_width=True)

elif menu == "Configurações":
    st.title("⚙️ Configurações do Sistema")
    st.write("Arquitetura Modular Determinística: **Ativa**")
    st.write("Camada de IA Futura: **Preparada para Injeção de Contexto Estruturado**")
