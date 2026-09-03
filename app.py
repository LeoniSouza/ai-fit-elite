elif menu == "Meu Perfil":
    st.title("👤 Avaliação Inicial, Anamnese e Termos")
    curr = profile or {}
    
    with st.form("profile_form"):
        name = st.text_input("Nome Completo *", value=curr.get("name", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Idade *", value=int(curr.get("age", 25)))
        with c2:
            sex = st.selectbox("Sexo *", ["Masculino", "Feminino", "Outro"])
        with c3:
            weight = st.number_input("Peso (kg) *", value=float(curr.get("weight", 70.0)))
            
        c4, c5 = st.columns(2)
        with c4:
            height = st.number_input("Altura (m) *", value=float(curr.get("height", 1.75)))
        with c5:
            goal = st.selectbox("Objetivo Principal *", ["Hipertrofia", "Emagrecimento e definição", "Condicionamento físico", "Treinamento de força", "Desenvolvimento físico geral"])
            
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
                st.session_state.sistema_liberado = True
                st.success("Salvo com sucesso!")
                st.rerun()
