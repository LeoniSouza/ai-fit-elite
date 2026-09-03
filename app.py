st.sidebar.divider()
st.sidebar.subheader("🚨 Relatar Dor")
dor_input = st.sidebar.text_input("Condição física ou dor:", placeholder="Ex: Dor no joelho...", key="input_dor_lateral")

if st.sidebar.button("Enviar para Restrições"):
    if dor_input:
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
    else:
        st.sidebar.warning("Digite algo no campo de dor antes de enviar.")
