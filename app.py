# Formulário lateral para relatar dor e enviar direto para restrições
st.sidebar.divider()
st.sidebar.subheader("🚨 Relatar Dor")
with st.sidebar.form("dor_form", clear_on_submit=True):
    dor_input = st.text_input("Condição física ou dor:", placeholder="Ex: Dor no joelho...")
    enviar_dor = st.form_submit_button("Enviar para Restrições")
    
    if enviar_dor and dor_input:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT restrictions FROM users WHERE id = 1")
        res_atual = cursor.fetchone()
        
        atual_rest = res_atual["restrictions"] if res_atual and res_atual["restrictions"] else ""
        nova_rest = f"{atual_rest} | Relato: {dor_input}" if atual_rest else f"Relato: {dor_input}"
        
        cursor.execute("UPDATE users SET restrictions = ? WHERE id = 1", (nova_rest,))
        conn.commit()
        conn.close()
        st.sidebar.success("Adicionado às restrições com sucesso!")
        st.rerun()
