import streamlit as st
import datetime
from database import init_db, get_connection, get_analytics_summary
from models import save_user_profile, get_user_profile, add_body_metric, get_body_metrics
from training_engine import generate_workout, save_generated_workout
from safety import check_safety_guidelines

st.set_page_config(page_title="AI FIT ELITE", page_icon="⚡", layout="wide")

init_db()

profile = get_user_profile()

st.sidebar.title("⚡ AI FIT ELITE")

# Se não houver perfil salvo, força a navegação direto para a aba de cadastro/perfil
if not profile or not profile.get("terms_accepted"):
    st.sidebar.warning("⚠️ Conclua o Perfil e Anamnese.")
    menu = "Meu Perfil"
else:
    menu = st.sidebar.radio("Navegação", [
        "Dashboard", "Meu Perfil", "Treino de Hoje", "Ficha de Treino Atual", "Histórico", "Evolução", "Configurações"
    ])

# Integração do relato de dor diretamente salvando nas restrições do perfil
safety_input = st.sidebar.text_input("Relatar dor ou condição física:", placeholder="Ex: Dor no joelho...")
if safety_input and profile:
    is_unsafe, warning_msg = check_safety_guidelines(safety_input)
    if is_unsafe:
        st.sidebar.error(warning_msg)
    # Atualiza automaticamente as restrições no banco com o relato de dor
    current_restrictions = profile.get("restrictions", "") or ""
    new_restriction = f"{current_restrictions} | Alerta recente: {safety_input}" if current_restrictions else f"Alerta recente: {safety_input}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET restrictions = ? WHERE id = 1", (new_restriction,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 1. DASHBOARD
# ---------------------------------------------------------
if menu == "Dashboard":
    st.title("📊 Painel de Controle Principal")
    if profile:
        summary = get_analytics_summary(1)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Treinos Realizados", summary["total_workouts"])
        c2.metric("Volume Total (kg)", f"{summary['total_volume']:,.1f}")
        c3.metric("Peso Atual", f"{profile.get('weight', 0)} kg")
        c4.metric("Objetivo", profile.get("goal", "Hipertrofia"))
        
        st.divider()
        st.subheader("📋 Resumo do Perfil e Anamnese")
        st.write(f"**Nome:** {profile.get('name')} | **Experiência:** {profile.get('experience')} | **Frequência:** {profile.get('frequency')}x/sem")
        if profile.get('restrictions'):
            st.warning(f"⚠️ **Restrições / Limitações:** {profile.get('restrictions')}")

# ---------------------------------------------------------
# 2. MEU PERFIL
# ---------------------------------------------------------
elif menu == "Meu Perfil":
    st.title("👤 Avaliação Inicial, Anamnese e Termos")
    
    curr = profile or {}
    
    with st.form("profile_form"):
        name = st.text_input("Nome Completo *", value=curr.get("name", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Idade *", value=int(curr.get("age", 25)))
        with c2:
            sex = st.selectbox("Sexo *", ["Masculino", "Feminino", "Outro"], index=0)
        with c3:
            weight = st.number_input("Peso (kg) *", value=float(curr.get("weight", 70.0)))
            
        c4, c5 = st.columns(2)
        with c4:
            height = st.number_input("Altura (m) *", value=float(curr.get("height", 1.75)))
        with c5:
            goal = st.selectbox("Objetivo Principal *", [
                "Hipertrofia", "Emagrecimento e definição", "Condicionamento físico", "Treinamento de força", "Desenvolvimento físico geral"
            ])
            
        experience = st.selectbox("Nível de Experiência *", ["Iniciante", "Intermediário", "Avançado"])
        
        c6, c7 = st.columns(2)
        with c6:
            frequency = st.slider("Dias por semana *", 1, 7, value=int(curr.get("frequency", 4)))
        with c7:
            duration = st.slider("Minutos por sessão *", 30, 120, value=int(curr.get("duration", 60)))
            
        equipment = st.selectbox("Equipamentos *", ["Academia completa", "Home Gym", "Peso Corporal"])
        
        st.divider()
        st.subheader("🛌 Anamnese")
        c8, c9, c10 = st.columns(3)
        with c8:
            sleep = st.selectbox("Sono *", ["Excelente", "Boa", "Regular", "Ruim"])
        with c9:
            disposition = st.selectbox("Disposição *", ["Alto", "Moderado", "Baixo"])
        with c10:
            recovery = st.selectbox("Recuperação *", ["Rápida", "Normal", "Lenta"])
            
        restrictions = st.text_area("Restrições ou lesões", value=curr.get("restrictions", ""))
        
        st.divider()
        terms_accepted = st.checkbox("Li e aceito os termos de responsabilidade e uso do sistema. *", value=bool(curr.get("terms_accepted", 0)))
        
        submitted = st.form_submit_button("Salvar Perfil e Liberar Sistema")
        
        if submitted:
            if not name.strip():
                st.error("Preencha o seu Nome Completo.")
            elif not terms_accepted:
                st.error("Você deve aceitar os Termos de Responsabilidade.")
            else:
                save_user_profile({
                    "name": name, "age": age, "sex": sex, "weight": weight, "height": height,
                    "goal": goal, "experience": experience, "frequency": frequency,
                    "duration": duration, "equipment": equipment, "sleep_quality": sleep,
                    "disposition": disposition, "recovery_quality": recovery, "restrictions": restrictions,
                    "terms_accepted": 1
                })
                st.success("Perfil salvo! Sistema liberado com sucesso.")
                st.rerun()

# ---------------------------------------------------------
# 3. TREINO DE HOJE
# ---------------------------------------------------------
elif menu == "Treino de Hoje":
    st.title("🏋️ Execução do Treino Adaptativo")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM workouts WHERE user_id = 1 AND completed = 0 ORDER BY id DESC LIMIT 1")
    workout_row = cursor.fetchone()
    
    if not workout_row:
        st.info("Nenhum treino ativo no momento.")
        if st.button("Gerar Próximo Treino do Ciclo"):
            plan = generate_workout(profile)
            save_generated_workout(1, plan)
            st.success("Novo treino gerado!")
            st.rerun()
    else:
        st.subheader(f"Sessão: {workout_row['workout_name']}")
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
        if st.button("Finalizar Treino e Avançar Ciclo"):
            cursor.execute("UPDATE workouts SET completed = 1 WHERE id = ?", (workout_row["id"],))
            conn.commit()
            st.success("Treino finalizado!")
            st.rerun()
    conn.close()

# ---------------------------------------------------------
# 4. FICHA DE TREINO ATUAL
# ---------------------------------------------------------
elif menu == "Ficha de Treino Atual":
    st.title("📋 Ficha de Treino Ativa")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts WHERE user_id = 1 AND completed = 0 ORDER BY id DESC LIMIT 1")
    active_workout = cursor.fetchone()
    
    if not active_workout:
        st.info("Nenhum treino ativo. Vá em **Treino de Hoje** para gerar.")
    else:
        cursor.execute("""
            SELECT e.name, e.muscle_group, we.target_sets, we.target_reps, we.rest_time, e.instructions
            FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id
            WHERE we.workout_id = ?
        """, (active_workout["id"],))
        for idx, ex in enumerate(cursor.fetchall(), 1):
            st.markdown(f"**{idx}. {ex['name']}** ({ex['muscle_group']}) — {ex['target_sets']}x{ex['target_reps']} (Descanso: {ex['rest_time']})")
    conn.close()

# ---------------------------------------------------------
# 5. HISTÓRICO
# ---------------------------------------------------------
elif menu == "Histórico":
    st.title("📜 Histórico")
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, date, workout_name, completed FROM workouts WHERE user_id = 1 ORDER BY date DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# 6. EVOLUÇÃO
# ---------------------------------------------------------
elif menu == "Evolução":
    st.title("📈 Evolução de Peso")
    with st.form("met_form"):
        nw = st.number_input("Novo Peso (kg)", value=float(profile.get("weight", 70.0) if profile else 70.0))
        if st.form_submit_button("Salvar Peso"):
            add_body_metric(1, datetime.date.today().isoformat(), nw)
            st.success("Salvo!")
            st.rerun()
    df_m = get_body_metrics(1)
    if not df_m.empty:
        st.line_chart(df_m, x="date", y="weight")

# ---------------------------------------------------------
# 7. CONFIGURAÇÕES
# ---------------------------------------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    st.write("AI FIT ELITE operando perfeitamente.")
