import streamlit as st
import pandas as pd
import datetime
from database import init_db, get_connection, get_analytics_summary
from models import save_user_profile, get_user_profile, add_body_metric, get_body_metrics
from training_engine import generate_workout, save_generated_workout
from safety import check_safety_guidelines

st.set_page_config(page_title="AI FIT ELITE", page_icon="⚡", layout="wide")

init_db()

# Garante que o perfil seja lido e o estado seja forçado corretamente
profile = get_user_profile()

if "sistema_liberado" not in st.session_state:
    st.session_state.sistema_liberado = bool(profile and profile.get("terms_accepted"))
elif profile and profile.get("terms_accepted"):
    st.session_state.sistema_liberado = True

st.sidebar.title("⚡ AI FIT ELITE")

if not st.session_state.sistema_liberado:
    st.sidebar.warning("⚠️ Conclua o Perfil e Anamnese para liberar o sistema.")
    menu = "Meu Perfil"
else:
    menu = st.sidebar.radio("Navegação", [
        "Dashboard", "Meu Perfil", "Treino de Hoje", "Ficha de Treino Atual", "Histórico", "Evolução", "Configurações"
    ])

st.sidebar.divider()
st.sidebar.subheader("🚨 Relatar Dor")
dor_input = st.sidebar.text_input("Condição física ou dor:", placeholder="Ex: Dor no joelho...", key="input_dor_lateral")

if st.sidebar.button("Enviar para Restrições"):
    if dor_input:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, restrictions FROM users WHERE id = 1")
        user_res = cursor.fetchone()
        
        if user_res:
            uid = user_res["id"]
            atual_rest = user_res["restrictions"] if user_res["restrictions"] else ""
            nova_rest = f"{atual_rest} | Relato: {dor_input}" if atual_rest else f"Relato: {dor_input}"
            cursor.execute("UPDATE users SET restrictions = ? WHERE id = ?", (nova_rest, uid))
            conn.commit()
        conn.close()
        st.sidebar.success("Adicionado às restrições!")
        st.rerun()
    else:
        st.sidebar.warning("Digite algo antes de enviar.")

if menu == "Dashboard":
    st.title("📊 Painel de Controle Principal")
    if not profile or not profile.get("terms_accepted"):
        st.warning("⚠️ Vá até a aba **Meu Perfil**, preencha os dados e aceite os termos para liberar o sistema.")
    else:
        summary = get_analytics_summary(profile.get("id", 1))
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Treinos Realizados", summary["total_workouts"])
        col2.metric("Volume Total (kg)", f"{summary['total_volume']:,.1f}")
        col3.metric("Peso Atual", f"{profile.get('weight', 0)} kg")
        col4.metric("Objetivo", profile.get("goal", "Hipertrofia"))
        
        st.divider()
        st.subheader("📋 Resumo do Aluno & Anamnese")
        st.write(f"**Nome:** {profile.get('name')} | **Experiência:** {profile.get('experience')} | **Frequência:** {profile.get('frequency')}x/sem")
        if profile.get('restrictions'):
            st.error(f"⚠️ **Restrições/Dores:** {profile.get('restrictions')}")

elif menu == "Meu Perfil":
    st.title("👤 Avaliação Inicial, Anamnese e Termos")
    
    st.info("ℹ️ **Diretrizes de Anamnese:** Preencha com atenção todas as informações abaixo sobre seu histórico, sono, disposição e eventuais restrições físicas. Esses dados são fundamentais para que o motor adaptativo calcule cargas e restrições com segurança e precisão para o seu perfil.")
    
    curr = profile or {}
    
    with st.form("profile_form"):
        name = st.text_input("Nome Completo *", value=curr.get("name", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Idade *", value=int(curr.get("age", 25)))
        with c2:
            sex = st.selectbox("Sexo *", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(curr.get("sex")) if curr.get("sex") in ["Masculino", "Feminino", "Outro"] else 0)
        with c3:
            weight = st.number_input("Peso (kg) *", value=float(curr.get("weight", 70.0)))
            
        c4, c5 = st.columns(2)
        with c4:
            height = st.number_input("Altura (m) *", value=float(curr.get("height", 1.75)))
        with c5:
            goal_options = ["Hipertrofia", "Emagrecimento e definição", "Condicionamento físico", "Treinamento de força", "Desenvolvimento físico geral"]
            goal = st.selectbox("Objetivo Principal *", goal_options, index=goal_options.index(curr.get("goal")) if curr.get("goal") in goal_options else 0)
            
        exp_options = ["Iniciante", "Intermediário", "Avançado"]
        experience = st.selectbox("Nível de Experiência *", exp_options, index=exp_options.index(curr.get("experience")) if curr.get("experience") in exp_options else 0)
        
        c6, c7 = st.columns(2)
        with c6:
            frequency = st.slider("Dias por semana *", 1, 7, value=int(curr.get("frequency", 4)))
        with c7:
            duration = st.slider("Minutos por sessão *", 30, 120, value=int(curr.get("duration", 60)))
            
        eq_options = ["Academia completa", "Home Gym", "Peso Corporal"]
        equipment = st.selectbox("Equipamentos *", eq_options, index=eq_options.index(curr.get("equipment")) if curr.get("equipment") in eq_options else 0)
        
        st.divider()
        st.subheader("🛌 Anamnese")
        c8, c9, c10 = st.columns(3)
        with c8:
            sleep_options = ["Excelente", "Boa", "Regular", "Ruim"]
            sleep = st.selectbox("Sono *", sleep_options, index=sleep_options.index(curr.get("sleep_quality")) if curr.get("sleep_quality") in sleep_options else 0)
        with c9:
            disp_options = ["Alto", "Moderado", "Baixo"]
            disposition = st.selectbox("Disposição *", disp_options, index=disp_options.index(curr.get("disposition")) if curr.get("disposition") in disp_options else 0)
        with c10:
            rec_options = ["Rápida", "Normal", "Lenta"]
            recovery = st.selectbox("Recuperação *", rec_options, index=rec_options.index(curr.get("recovery_quality")) if curr.get("recovery_quality") in rec_options else 0)
            
        restrictions = st.text_area("Restrições ou lesões", value=curr.get("restrictions", ""))
        
        st.divider()
        terms_accepted = st.checkbox("Li e aceito os termos de responsabilidade e uso do sistema. *", value=bool(curr.get("terms_accepted", 0)))
        
        submitted = st.form_submit_button("Salvar Perfil e Liberar Sistema")
        
        if submitted:
            if not name.strip():
                st.error("Preencha o nome.")
            elif not terms_accepted:
                st.error("Aceite os termos de responsabilidade.")
            else:
                save_user_profile({
                    "name": name, "age": age, "sex": sex, "weight": weight, "height": height,
                    "goal": goal, "experience": experience, "frequency": frequency,
                    "duration": duration, "equipment": equipment, "sleep_quality": sleep,
                    "disposition": disposition, "recovery_quality": recovery, "restrictions": restrictions,
                    "terms_accepted": 1
                })
                # Altera o estado na sessão e força o redirecionamento automático para o Dashboard
                st.session_state.sistema_liberado = True
                st.success("Salvo com sucesso! Liberando o sistema...")
                st.rerun()

elif menu == "Treino de Hoje":
    st.title("🏋️ Execução do Treino Adaptativo")
    uid = profile.get("id", 1) if profile else 1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts WHERE user_id = ? AND completed = 0 ORDER BY id DESC LIMIT 1", (uid,))
    workout_row = cursor.fetchone()
    
    if not workout_row:
        st.info("Nenhum treino ativo no momento.")
        if st.button("Gerar Próximo Treino"):
            plan = generate_workout(profile)
            save_generated_workout(uid, plan)
            st.success("Gerado!")
            st.rerun()
    else:
        st.subheader(f"Sessão: {workout_row['workout_name']}")
        cursor.execute("""
            SELECT we.id as we_id, e.name, we.target_sets, we.target_reps, we.rest_time 
            FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id
            WHERE we.workout_id = ?
        """, (workout_row["id"],))
        for ex in cursor.fetchall():
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
            cursor.execute("UPDATE workouts SET completed = 1 WHERE id = ?", (workout_row["id"],))
            conn.commit()
            st.success("Finalizado!")
            st.rerun()
    conn.close()

elif menu == "Ficha de Treino Atual":
    st.title("📋 Ficha de Treino Ativa")
    uid = profile.get("id", 1) if profile else 1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts WHERE user_id = ? AND completed = 0 ORDER BY id DESC LIMIT 1", (uid,))
    active = cursor.fetchone()
    if not active:
        st.info("Nenhum treino ativo.")
    else:
        cursor.execute("""
            SELECT e.name, e.muscle_group, we.target_sets, we.target_reps 
            FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id WHERE we.workout_id = ?
        """, (active["id"],))
        for idx, ex in enumerate(cursor.fetchall(), 1):
            st.markdown(f"**{idx}. {ex['name']}** ({ex['muscle_group']}) — {ex['target_sets']}x{ex['target_reps']}")
    conn.close()

elif menu == "Histórico":
    st.title("📜 Histórico")
    uid = profile.get("id", 1) if profile else 1
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, date, workout_name, completed FROM workouts WHERE user_id = ? ORDER BY date DESC", conn, params=(uid,))
    conn.close()
    st.dataframe(df, use_container_width=True)

elif menu == "Evolução":
    st.title("📈 Evolução de Peso")
    uid = profile.get("id", 1) if profile else 1
    with st.form("met_form"):
        nw = st.number_input("Novo Peso (kg)", value=float(profile.get("weight", 70.0) if profile else 70.0))
        if st.form_submit_button("Salvar"):
            add_body_metric(uid, datetime.date.today().isoformat(), nw)
            st.success("Salvo!")
            st.rerun()
    df_m = get_body_metrics(uid)
    if not df_m.empty:
        st.line_chart(df_m, x="date", y="weight")

elif menu == "Configurações":
    st.title("⚙️ Configurações")
    st.write("Sistema operacional estável.")
