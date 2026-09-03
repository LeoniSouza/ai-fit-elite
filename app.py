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

# Validação estrita: Se o perfil não existe ou os termos não foram aceitos, bloqueia o menu e obriga o preenchimento
if not profile or not profile.get("terms_accepted"):
    st.sidebar.warning("⚠️ Preenchimento obrigatório do Perfil e Anamnese para liberar o sistema.")
    menu = "Meu Perfil"
else:
    menu = st.sidebar.radio("Navegação", [
        "Dashboard", "Meu Perfil", "Treino de Hoje", "Ficha de Treino Atual", "Histórico", "Evolução", "Configurações"
    ])

safety_input = st.sidebar.text_input("Relatar dor ou condição física:", placeholder="Ex: Senti dor no joelho...")
if safety_input:
    is_unsafe, warning_msg = check_safety_guidelines(safety_input)
    if is_unsafe:
        st.sidebar.error(warning_msg)

# ---------------------------------------------------------
# DASHBOARD (Mostra todas as informações e métricas)
# ---------------------------------------------------------
if menu == "Dashboard":
    st.title("📊 Painel de Controle Principal")
    
    summary = get_analytics_summary(1)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Treinos Realizados", summary["total_workouts"])
    col2.metric("Volume Total (kg)", f"{summary['total_volume']:,.1f}")
    col3.metric("Peso Atual", f"{profile.get('weight', 0)} kg")
    col4.metric("Objetivo", profile.get("goal", "Hipertrofia"))
    
    st.divider()
    st.subheader("📋 Resumo do Perfil e Anamnese Cadastrada")
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Nome:** {profile.get('name')}")
    c1.markdown(f"**Idade:** {profile.get('age')} anos")
    c1.markdown(f"**Sexo:** {profile.get('sex')}")
    
    c2.markdown(f"**Altura:** {profile.get('height')} m")
    c2.markdown(f"**Experiência:** {profile.get('experience')}")
    c2.markdown(f"**Frequência:** {profile.get('frequency')}x por semana")
    
    c3.markdown(f"**Sono:** {profile.get('sleep_quality')}")
    c3.markdown(f"**Disposição:** {profile.get('disposition')}")
    c3.markdown(f"**Recuperação:** {profile.get('recovery_quality')}")
    
    if profile.get('restrictions'):
        st.warning(f"⚠️ **Restrições / Limitações Informadas:** {profile.get('restrictions')}")

# ---------------------------------------------------------
# MEU PERFIL (Obrigatório e com Anamnese e Termos)
# ---------------------------------------------------------
elif menu == "Meu Perfil":
    st.title("👤 Avaliação Inicial, Anamnese e Termos")
    
    if not profile or not profile.get("terms_accepted"):
        st.error("🚨 **Atenção:** Você deve preencher todos os dados e aceitar os termos de responsabilidade para acessar o sistema.")
    
    curr = profile or {}
    
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
        
        st.divider()
        st.subheader("⚖️ Termos de Responsabilidade")
        st.markdown("""
        Declaro que estou apto fisicamente para a prática de exercícios físicos e que as informações prestadas são verdadeiras. 
        O **AI FIT ELITE** é um sistema de suporte tecnológico e não substitui a avaliação ou acompanhamento médico e de profissionais de educação física habilitados.
        """)
        terms_accepted = st.checkbox("Li e aceito os termos de responsabilidade e uso do sistema.", value=bool(curr.get("terms_accepted", 0)))
        
        submitted = st.form_submit_button("Salvar Perfil e Liberar Sistema")
        if submitted:
            if not name.strip():
                st.error("Por favor, preencha o seu nome.")
            elif not terms_accepted:
                st.error("Você deve aceitar os termos de responsabilidade para continuar.")
            else:
                save_user_profile({
                    "name": name, "age": age, "sex": sex, "weight": weight, "height": height,
                    "goal": goal, "experience": experience, "frequency": frequency,
                    "duration": duration, "equipment": equipment, "sleep_quality": sleep,
                    "disposition": disposition, "recovery_quality": recovery, "restrictions": restrictions,
                    "terms_accepted": 1 if terms_accepted else 0
                })
                st.success("Perfil salvo e validado com sucesso! Sistema liberado.")
                st.rerun()

# ---------------------------------------------------------
# TREINO DE HOJE
# ---------------------------------------------------------
elif menu == "Treino de Hoje":
    st.title("🏋️ Execução do Treino Adaptativo")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM workouts WHERE user_id = 1 AND completed = 0 ORDER BY id DESC LIMIT 1")
    workout_row = cursor.fetchone()
    
    if not workout_row:
        st.info("Nenhum treino ativo no momento. Gere sua próxima sessão com base no seu objetivo.")
        if st.button("Gerar Próximo Treino do Ciclo"):
            plan = generate_workout(profile)
            save_generated_workout(1, plan)
            st.success("Novo treino gerado e alinhado na sequência semanal!")
            st.rerun()
    else:
        st.subheader(f"Sessão: {workout_row['workout_name']} | Data: {workout_row['date']}")
        
        cursor.execute("""
            SELECT we.id as we_id, e.name, we.target_sets, we.target_reps, we.rest_time 
            FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id
            WHERE we.workout_id = ?
        """, (workout_row["id"],))
        exercises = cursor.fetchall()
        
        for ex in exercises:
            with st.expander(f"🔹 {ex['name']} | Séries: {ex['target_sets']} | Reps: {ex['target_reps']} | Descanso: {ex['rest_time']}"):
                for s in range(1, ex["target_sets"] + 1):
                    c1, c2, c3, c4 = st.columns(4)
                    w = c1.number_input(f"Carga (kg) S{s}", value=0.0, key=f"w_{ex['we_id']}_{s}")
                    r = c2.number_input(f"Reps S{s}", value=10, key=f"r_{ex['we_id']}_{s}")
                    rir = c3.number_input(f"RIR S{s}", value=2.0, key=f"rir_{ex['we_id']}_{s}")
                    done = c4.checkbox(f"Concluir S{s}", key=f"chk_{ex['we_id']}_{s}")
                    if done:
                        cursor.execute("INSERT OR REPLACE INTO sets_log (workout_exercise_id, set_number, weight, reps, rir, rpe) VALUES (?, ?, ?, ?, ?, ?)", (ex["we_id"], s, w, r, rir, 10 - rir))
                        conn.commit()
        
        st.divider()
        if st.button("Finalizar Treino e Avançar Ciclo"):
            cursor.execute("UPDATE workouts SET completed = 1 WHERE id = ?", (workout_row["id"],))
            conn.commit()
            st.success("Treino finalizado com sucesso! O ciclo avançou para a próxima seção.")
            st.balloons()
            st.rerun()
    conn.close()

# ---------------------------------------------------------
# FICHA DE TREINO ATUAL (Substituiu a Biblioteca)
# ---------------------------------------------------------
elif menu == "Ficha de Treino Atual":
    st.title("📋 Ficha de Treino Ativa do Aluno")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM workouts WHERE user_id = 1 AND completed = 0 ORDER BY id DESC LIMIT 1")
    active_workout = cursor.fetchone()
    
    if not active_workout:
        st.info("Nenhum treino ativo gerado no momento. Vá em **Treino de Hoje** para gerar sua ficha.")
    else:
        st.subheader(f"Sessão Vigente: {active_workout['workout_name']}")
        cursor.execute("""
            SELECT e.name, e.muscle_group, e.equipment, we.target_sets, we.target_reps, we.rest_time, e.instructions
            FROM workout_exercises we 
            JOIN exercises e ON we.exercise_id = e.id
            WHERE we.workout_id = ?
        """, (active_workout["id"],))
        ficha_exercises = cursor.fetchall()
        
        for idx, ex in enumerate(ficha_exercises, 1):
            with st.expander(f"{idx}. {ex['name']} ({ex['muscle_group']})"):
                st.markdown(f"**Equipamento:** {ex['equipment']}")
                st.markdown(f"**Prescrição:** {ex['target_sets']} séries de {ex['target_reps']} repetições")
                st.markdown(f"**Descanso:** {ex['rest_time']}")
                st.markdown(f"**Instrução de Execução:** {ex['instructions']}")
    conn.close()

elif menu == "Histórico":
    st.title("📜 Histórico de Sessões")
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, date, workout_name, completed FROM workouts WHERE user_id = 1 ORDER BY date DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

elif menu == "Evolução":
    st.title("📈 Acompanhamento de Peso Corporal")
    with st.form("met_form"):
        nw = st.number_input("Novo Peso (kg)", value=profile.get("weight", 70.0))
        if st.form_submit_button("Salvar Medição"):
            add_body_metric(1, datetime.date.today().isoformat(), nw)
            st.success("Salvo com sucesso!")
            st.rerun()
    df_m = get_body_metrics(1)
    if not df_m.empty:
        st.line_chart(df_m, x="date", y="weight")
    else:
        st.info("Nenhuma medição registrada.")

elif menu == "Configurações":
    st.title("⚙️ Configurações do Sistema")
    st.write("Sistema rodando com motor determinístico adaptativo e anamnese obrigatória.")
