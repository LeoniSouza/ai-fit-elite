import streamlit as st
import datetime
from database import init_db, get_connection, get_analytics_summary
from models import save_user_profile, get_user_profile, add_body_metric, get_body_metrics
from training_engine import generate_workout, save_generated_workout
from safety import check_safety_guidelines

st.set_page_config(page_title="AI FIT ELITE", page_icon="⚡", layout="wide")

init_db()

st.sidebar.title("⚡ AI FIT ELITE")
profile = get_user_profile()

menu = st.sidebar.radio("Navegação", [
    "Dashboard", "Meu Perfil", "Treino de Hoje", "Histórico", "Evolução", "Biblioteca de Exercícios", "Configurações"
])

safety_input = st.sidebar.text_input("Relatar dor ou condição física:", placeholder="Ex: Dor no joelho...")
if safety_input:
    is_unsafe, warning_msg = check_safety_guidelines(safety_input)
    if is_unsafe:
        st.sidebar.error(warning_msg)

if menu == "Dashboard":
    st.title("📊 Painel de Controle Principal")
    if not profile:
        st.warning("⚠️ Configure seu perfil na aba **Meu Perfil**.")
    else:
        summary = get_analytics_summary(1)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Treinos Realizados", summary["total_workouts"])
        col2.metric("Volume Total (kg)", f"{summary['total_volume']:,.1f}")
        col3.metric("Peso Atual", f"{profile.get('weight', 0)} kg")
        col4.metric("Objetivo", profile.get("goal", "Hipertrofia"))

elif menu == "Meu Perfil":
    st.title("👤 Configuração de Perfil")
    curr = get_user_profile() or {}
    with st.form("profile_form"):
        name = st.text_input("Nome", value=curr.get("name", ""))
        age = st.number_input("Idade", value=curr.get("age", 25))
        weight = st.number_input("Peso (kg)", value=curr.get("weight", 70.0))
        height = st.number_input("Altura (m)", value=curr.get("height", 1.75))
        goal = st.selectbox("Objetivo", ["Hipertrofia", "Emagrecimento e definição", "Condicionamento físico"])
        experience = st.selectbox("Experiência", ["Iniciante", "Intermediário", "Avançado"])
        frequency = st.slider("Frequência Semanal", 1, 7, value=4)
        duration = st.slider("Duração (min)", 30, 120, value=60)
        equipment = st.selectbox("Equipamentos", ["Academia completa"])
        
        if st.form_submit_button("Salvar Perfil"):
            save_user_profile({"name": name, "age": age, "sex": "Masculino", "weight": weight, "height": height, "goal": goal, "experience": experience, "frequency": frequency, "duration": duration, "equipment": equipment})
            st.success("Perfil salvo!")
            st.rerun()

elif menu == "Treino de Hoje":
    st.title("🏋️ Treino do Dia")
    if not profile:
        st.warning("Cadastre seu perfil primeiro na aba **Meu Perfil**.")
    else:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Busca apenas um treino ATIVO (completed = 0) para o usuário
        cursor.execute("SELECT * FROM workouts WHERE user_id = 1 AND completed = 0 ORDER BY id DESC LIMIT 1")
        workout_row = cursor.fetchone()
        
        # Se não houver nenhum treino ativo, exibe o botão para gerar um NOVO treino
        if not workout_row:
            st.info("Nenhum treino ativo no momento. Clique abaixo para gerar o seu próximo treino adaptativo!")
            if st.button("Gerar Novo Treino"):
                plan = generate_workout(profile)
                save_generated_workout(1, plan)
                st.success("Novo treino gerado com sucesso!")
                st.rerun()
        else:
            st.subheader(f"Sessão: {workout_row['workout_name']} (Data: {workout_row['date']})")
            
            cursor.execute("""
                SELECT we.id as we_id, e.name, we.target_sets, we.target_reps, we.rest_time 
                FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id
                WHERE we.workout_id = ?
            """, (workout_row["id"],))
            exercises = cursor.fetchall()
            
            for ex in exercises:
                with st.expander(f"🔹 {ex['name']} | Séries: {ex['target_sets']} | Reps: {ex['target_reps']}"):
                    for s in range(1, ex["target_sets"] + 1):
                        c1, c2, c3, c4 = st.columns(4)
                        w = c1.number_input(f"Carga S{s}", value=0.0, key=f"w_{ex['we_id']}_{s}")
                        r = c2.number_input(f"Reps S{s}", value=10, key=f"r_{ex['we_id']}_{s}")
                        rir = c3.number_input(f"RIR S{s}", value=2.0, key=f"rir_{ex['we_id']}_{s}")
                        done = c4.checkbox(f"OK S{s}", key=f"chk_{ex['we_id']}_{s}")
                        if done:
                            cursor.execute("INSERT OR REPLACE INTO sets_log (workout_exercise_id, set_number, weight, reps, rir, rpe) VALUES (?, ?, ?, ?, ?, ?)", (ex["we_id"], s, w, r, rir, 10 - rir))
                            conn.commit()
            
            st.divider()
            if st.button("Finalizar Treino"):
                # Marca o treino atual como concluído (completed = 1)
                cursor.execute("UPDATE workouts SET completed = 1 WHERE id = ?", (workout_row["id"],))
                conn.commit()
                st.success("Treino finalizado, arquivado no histórico e pronto para gerar o próximo!")
                st.balloons()
                st.rerun()
        conn.close()

elif menu == "Histórico":
    st.title("📜 Histórico de Treinos Concluídos")
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, date, workout_name, completed FROM workouts WHERE user_id = 1 ORDER BY date DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

elif menu == "Evolução":
    st.title("📈 Evolução de Peso Corporal")
    with st.form("met_form"):
        nw = st.number_input("Novo Peso (kg)", value=profile.get("weight", 70.0) if profile else 70.0)
        if st.form_submit_button("Salvar Peso"):
            add_body_metric(1, datetime.date.today().isoformat(), nw)
            st.success("Peso salvo com sucesso!")
            st.rerun()
    df_m = get_body_metrics(1)
    if not df_m.empty:
        st.line_chart(df_m, x="date", y="weight")

elif menu == "Biblioteca de Exercícios":
    st.title("📚 Biblioteca de Exercícios")
    conn = get_connection()
    df_ex = pd.read_sql_query("SELECT name, muscle_group, equipment, level, goal FROM exercises", conn)
    conn.close()
    st.dataframe(df_ex, use_container_width=True)

elif menu == "Configurações":
    st.title("⚙️ Configurações do Sistema")
    st.write("Sistema operando com banco de dados SQLite local na nuvem.")
