import streamlit as st
import joblib
import pandas as pd

# Carregar o modelo e a lista de colunas
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')

# Configuração da página
st.set_page_config(page_title="Preditor de Risco - Passos Mágicos", layout="centered")

st.image("https://passosmagicos.org.br/wp-content/uploads/2020/10/logo-passos-magicos.png", width=200)
st.title("📊 Sistema de Alerta de Risco de Defasagem")
st.markdown("""
Esta ferramenta utiliza Inteligência Artificial para identificar alunos com probabilidade de entrar em risco de defasagem escolar.
Insira as notas dos indicadores abaixo para obter o diagnóstico.
""")

# Criando formulário de entrada
with st.form("predict_form"):
    st.subheader("Indicadores do Aluno")

    col1, col2 = st.columns(2)

    with col1:
        ida = st.number_input("IDA (Desempenho Acadêmico)", 0.0, 10.0, 7.0)
        ieg = st.number_input("IEG (Engajamento)", 0.0, 10.0, 7.0)
        ips = st.number_input("IPS (Socioemocional)", 0.0, 10.0, 7.0)

    with col2:
        ipp = st.number_input("IPP (Psicopedagógico)", 0.0, 10.0, 7.0)
        ipv = st.number_input("IPV (Ponto de Virada)", 0.0, 10.0, 7.0)

    submit = st.form_submit_button("Realizar Diagnóstico")

if submit:
    # Organizar os dados na ordem correta que o modelo espera
    input_data = pd.DataFrame([[ida, ieg, ips, ipp, ipv]], columns=features)

    # Realizar a predição
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1] # Probabilidade de ser Risco (1)

    st.divider()

    if prediction == 1:
        st.error(f"⚠️ **ALERTA: Aluno em Risco de Defasagem.**")
        st.write(f"Probabilidade calculada: **{probability*100:.1f}%**")
        st.info("Recomendação: Encaminhar para acompanhamento psicopedagógico intensivo.")
    else:
        st.success(f"✅ **Aluno Estável.**")
        st.write(f"Probabilidade de risco: **{probability*100:.1f}%**")
        st.info("O aluno apresenta bons indicadores de desenvolvimento.")

st.sidebar.info("Projeto Datathon - Fase 5 | FIAP Pós-Tech")
