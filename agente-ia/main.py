entrada = st.chat_input(f"Pergunte sobre {config['badge'].lower()}...")

if entrada:
    st.chat_message("user").write(entrada)
    msgs.append({"role": "user", "content": entrada})
    hist_gem.append({"role": "user", "content": entrada})

    contexto = ""
    if precisa_buscar(entrada):
        with st.spinner("Buscando informações atualizadas..."):
            resultado = buscar_internet(entrada)
            if resultado:
                data = datetime.now().strftime("%d/%m/%Y")
                contexto = f"[INTERNET - {data}]\n{resultado}\n[FIM]\n\n"

    system = config["prompt"] + f"\nHoje: {datetime.now().strftime('%d/%m/%Y')}"
    msg_completa = f"{contexto}Pergunta: {entrada}"

    resposta = None

    if GEMINI_API_KEY:
        try:
            with st.spinner("Paulo AI está pensando..."):
                resposta = responder_gemini(system, hist_gem[:-1], msg_completa)
        except:
            pass

    if resposta is None and GROQ_API_KEY:
        try:
            with st.spinner("Paulo AI está pensando (Groq)..."):
                resposta = responder_groq(system, hist_gem[:-1], msg_completa)
        except Exception as e:
            resposta = f"Erro: {e}"

    if resposta is None:
        resposta = "Configure uma API Gemini ou Groq."

    st.chat_message("assistant").write(resposta)

    msgs.append({"role": "assistant", "content": resposta})
    hist_gem.append({"role": "assistant", "content": resposta})

    # salva no Google Sheets
    registrar_lead(nicho, entrada, resposta)
