import streamlit as st
import pandas as pd
import joblib

# Configuração da página
st.title("Previsão de Risco de Defasagem - Passos Mágicos")

# Carregar o modelo
model = joblib.load('modelo_treinado.pkl')

# Inputs baseados nos indicadores do Datathon
st.header("Indicadores do Aluno")
ida = st.slider("IDA (Desempenho Acadêmico)", 0.0, 10.0, 5.0)
ieg = st.slider("IEG (Engajamento)", 0.0, 10.0, 5.0)
ips = st.slider("IPS (Psicossocial)", 0.0, 10.0, 5.0)

if st.button("Analisar Risco"):
    # Organizar dados para o modelo
    dados = pd.DataFrame([[ida, ieg, ips]], columns=['IDA', 'IEG', 'IPS'])
    
    # Predição de probabilidade
    probabilidade = model.predict_proba(dados)[0][1] 
    
    st.subheader(f"Probabilidade de Risco: {probabilidade*100:.2f}%")
    
    if probabilidade > 0.7:
        st.error("Alerta: Alto risco de defasagem!")
    else:
        st.success("Aluno em situação estável.")
