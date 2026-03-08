import streamlit as st
import joblib
import pandas as pd
import google.generativeai as genai

# Carregar modelo e colunas
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')

# Configuração da IA (Gemini)
# DICA: No deploy, use st.secrets para esconder sua chave!
GOOGLE_API_KEY = st.sidebar.text_input("Insira sua Gemini API Key", type="password")

def gerar_comentario_ia(dados, risco, probabilidade):
    if not GOOGLE_API_KEY:
        return "Insira a chave da API no menu lateral para gerar um comentário humanizado."
    
    genai.configure(api_key=GOOGLE_API_KEY)
    llm = genai.GenerativeModel('gemini-pro')
    
    status = "em risco" if risco == 1 else "estável"
    
    # O "Prompt" é o segredo para a IA ser humana
    prompt = f"""
    Você é um consultor pedagógico da Associação Passos Mágicos. 
    Analise os seguintes indicadores de um aluno:
    - Desempenho Acadêmico (IDA): {dados['IDA']}
    - Engajamento (IEG): {dados['IEG']}
    - Socioemocional (IPS): {dados['IPS']}
    - Psicopedagógico (IPP): {dados['IPP']}
    - Ponto de Virada (IPV): {dados['IPV']}
    
    O modelo de IA classificou este aluno como {status} (Probabilidade de risco: {probabilidade*100:.1f}%).
    
    Escreva um breve comentário (máximo 4 frases) acolhedor e humanizado para a equipe pedagógica. 
    Incentive o foco no desenvolvimento do aluno e não apenas na nota.
    Use um tom empático e motivador.
    """
    
    response = llm.generate_content(prompt)
    return response.text

# --- Interface Streamlit ---
st.set_page_config(page_title="Passos Mágicos - IA", layout="centered")
st.title("🌱 Mentor Digital Passos Mágicos")

# (Aqui entra o formulário que já criamos anteriormente...)
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
    submit = st.form_submit_button("Analisar Desempenho")

if submit:
    input_data = pd.DataFrame([[ida, ieg, ips, ipp, ipv]], columns=features)
    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]
    
    st.divider()
    
    # Exibe o resultado do Modelo
    if prediction == 1:
        st.error(f"⚠️ **Diagnóstico: Atenção Necessária**")
    else:
        st.success(f"✅ **Diagnóstico: Desenvolvimento Estável**")
        
    # --- NOVIDADE: Bot de IA Generativa ---
    with st.expander("✨ Ver Comentário do Mentor Digital", expanded=True):
        with st.spinner("O Mentor está analisando os dados..."):
            comentario = gerar_comentario_ia({'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}, prediction, prob)
            st.write(comentario)

st.sidebar.markdown("---")
st.sidebar.caption("Esta IA utiliza dados históricos e o modelo Random Forest para apoio pedagógico.")
