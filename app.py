import streamlit as st
import joblib
import pandas as pd
import google.generativeai as genai

# Carregar modelo e colunas
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')

# --- CONFIGURAÇÃO DA API KEY ---
if "GEMINI_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
else:
    GOOGLE_API_KEY = st.sidebar.text_input("Insira sua Gemini API Key (Opcional)", type="password")

# --- FUNÇÃO 1: EXPLICAÇÃO TÉCNICA (Lógica de Negócio) ---
def explicar_risco_tecnico(dados, prob):
    indicadores_baixos = [k for k, v in dados.items() if v < 7.0]
    
    # Tradução dos termos para o usuário
    nomes = {
        'IDA': 'Desempenho Acadêmico', 'IEG': 'Engajamento',
        'IPS': 'Socioemocional', 'IPP': 'Psicopedagógico', 'IPV': 'Ponto de Virada'
    }
    
    if prob > 0.5:
        msg = f"O modelo identificou um **risco de {prob*100:.1f}%** baseado no cruzamento histórico de dados. "
        if indicadores_baixos:
            detalhes = ", ".join([nomes[idx] for idx in indicadores_baixos])
            msg += f"Este alerta foi acionado principalmente pela fragilidade em: **{detalhes}**. "
        msg += "Recomenda-se uma intervenção preventiva para evitar o distanciamento do aluno."
    else:
        msg = "Os indicadores mostram que, apesar de possíveis oscilações, o aluno mantém uma trajetória de segurança estatística."
    
    return msg

# --- FUNÇÃO 2: COMENTÁRIO HUMANIZADO (IA) ---
def gerar_comentario_ia(dados, risco, probabilidade):
    if not GOOGLE_API_KEY:
        return None # Silencioso se não houver chave

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        llm = genai.GenerativeModel('gemini-pro')
        status = "em risco" if risco == 1 else "estável"
        prompt = f"Analise como consultor da Passos Mágicos: IDA:{dados['IDA']}, IEG:{dados['IEG']}, IPS:{dados['IPS']}, IPP:{dados['IPP']}, IPV:{dados['IPV']}. Risco: {probabilidade*100:.1f}%. Gere um acolhimento breve."
        response = llm.generate_content(prompt)
        return response.text
    except:
        return "ℹ️ Mentor Digital indisponível no momento."

# --- Interface Streamlit ---
st.set_page_config(page_title="Passos Mágicos - Diagnóstico", layout="centered")
st.title("🌱 Mentor Digital Passos Mágicos")

# Guia de Indicadores
with st.expander("📖 Guia Rápido de Indicadores"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**📚 IDA:** Desempenho Escolar")
        st.write("**🧠 IPP:** Processo de Aprendizado")
        st.write("**🔥 IEG:** Motivação e Frequência")
    with col_b:
        st.write("**❤️ IPS:** Relações e Emoções")
        st.write("**✨ IPV:** Protagonismo (Brilho nos Olhos)")

# Formulário
with st.form("predict_form"):
    st.subheader("Indicadores do Aluno")
    col1, col2 = st.columns(2)
    with col1:
        ida = st.number_input("IDA (Acadêmico)", 0.0, 10.0, 7.0)
        ieg = st.number_input("IEG (Engajamento)", 0.0, 10.0, 7.0)
        ips = st.number_input("IPS (Socioemocional)", 0.0, 10.0, 7.0)
    with col2:
        ipp = st.number_input("IPP (Psicopedagógico)", 0.0, 10.0, 7.0)
        ipv = st.number_input("IPV (Ponto de Virada)", 0.0, 10.0, 7.0)
    submit = st.form_submit_button("Realizar Diagnóstico")

if submit:
    input_dict = {'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}
    input_df = pd.DataFrame([input_dict], columns=features)
    prediction = model.predict(input_df)[0]
    prob = model.predict_proba(input_df)[0][1]

    st.divider()

    # 1. DIAGNÓSTICO TÉCNICO
    if prediction == 1:
        st.error(f"⚠️ **Diagnóstico Técnico: Atenção Necessária**")
        # EXPLICAÇÃO DOS DADOS (Cereja do bolo)
        st.warning(explicar_risco_tecnico(input_dict, prob))
    else:
        st.success(f"✅ **Diagnóstico Técnico: Desenvolvimento Estável**")
        st.info("O aluno apresenta segurança nos indicadores atuais.")

    # 2. COMENTÁRIO IA (Opcional)
    res_ia = gerar_comentario_ia(input_dict, prediction, prob)
    if res_ia:
        with st.expander("✨ Ver Análise Humanizada do Mentor", expanded=True):
            st.write(res_ia)
    elif not GOOGLE_API_KEY:
        st.info("💡 Para uma análise pedagógica detalhada via IA, configure a API Key na barra lateral.")

st.sidebar.markdown("---")
st.sidebar.caption("Projeto Datathon - Fase 5 | FIAP Pós-Tech")
