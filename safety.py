def check_safety_guidelines(user_input_text):
    warning_keywords = ["dor", "lesão", "machucado", "cirurgia", "médico", "diagnóstico", "hérnia"]
    text_lower = user_input_text.lower()
    
    for kw in warning_keywords:
        if kw in text_lower:
            return True, (
                "⚠️ **Aviso de Segurança:** Identificamos menção a desconforto físico. "
                "O AI FIT ELITE é um sistema de suporte e não faz diagnósticos médicos. "
                "Procure um profissional qualificado."
            )
    return False, ""
