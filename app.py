import streamlit as st
import joblib
import pandas as pd
import google.generativeai as genai

# Carregar modelo e colunas
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')

# --- CONFIGURAÇÃO DA API KEY (SECRETS OU SIDEBAR) ---
# Tenta buscar no Secrets do Streamlit Cloud primeiro
if "GEMINI_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
else:
    # Caso não esteja no Secrets, permite entrada manual na barra lateral
    GOOGLE_API_KEY = st.sidebar.text_input("Insira sua Gemini API Key (Opcional)", type="password", help="A chave é necessária apenas para gerar o comentário humanizado.")

def gerar_comentario_ia(dados, risco, probabilidade):
    # Se não houver chave, retorna uma mensagem informativa sem erro
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "":
        return "💡 O diagnóstico técnico foi concluído! Para receber um comentário humanizado da nossa IA, insira uma API Key válida no menu lateral."

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        llm = genai.GenerativeModel('gemini-pro')

        status = "em risco" if risco == 1 else "estável"

        prompt = f"""
        Você é um consultor pedagógico da Associação Passos Mágicos.
        Analise os seguintes indicadores de um aluno:
        - IDA: {dados['IDA']}, IEG: {dados['IEG']}, IPS: {dados['IPS']}, IPP: {dados['IPP']}, IPV: {dados['IPV']}

        O modelo classificou este aluno como {status} (Probabilidade de risco: {probabilidade*100:.1f}%).

        Escreva um breve comentário (máximo 4 frases) acolhedor e humanizado para a equipe pedagógica.
        Incentive o foco no desenvolvimento do aluno e não apenas na nota. Tonalidade empática.
        """

        response = llm.generate_content(prompt)
        return response.text
    
    except Exception:
        return "ℹ️ Não foi possível conectar ao Mentor Digital. Verifique sua chave ou tente novamente mais tarde. O diagnóstico técnico acima permanece válido."

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

# Formulário de Entrada
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
    # 1. PROCESSAMENTO DO MODELO (Sempre executa)
    input_data = pd.DataFrame([[ida, ieg, ips, ipp, ipv]], columns=features)
    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    st.divider()

    # Exibe o resultado visual do diagnóstico técnico
    if prediction == 1:
        st.error(f"⚠️ **Diagnóstico Técnico: Atenção Necessária**")
        st.info(f"Probabilidade de risco calculada pelo modelo: {prob*100:.1f}%")
    else:
        st.success(f"✅ **Diagnóstico Técnico: Desenvolvimento Estável**")
        st.info(f"O aluno apresenta segurança nos indicadores atuais.")

    # 2. CHAMADA DA IA (Opcional/Condicional)
    with st.expander("✨ Comentário do Mentor Digital", expanded=True):
        if GOOGLE_API_KEY:
            with st.spinner("O Mentor está analisando os dados..."):
                res_ia = gerar_comentario_ia({'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}, prediction, prob)
                st.write(res_ia)
        else:
            st.write("💡 Para receber uma análise humanizada detalhada, configure a chave de API no menu lateral.")

st.sidebar.markdown("---")
st.sidebar.caption("Projeto Datathon - Fase 5 | FIAP Pós-Tech")
