import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

# --- 1. CARREGAMENTO DE ASSETS ---
# Certifique-se de que os arquivos .pkl estão na mesma pasta do script
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')

try:
    baselines = joblib.load('medias_comparativas.pkl')
except:
    baselines = {
        'historica': {'IDA':7, 'IEG':7, 'IPS':7, 'IPP':7, 'IPV':7},
        '2024': {'IDA':7.5, 'IEG':7.2, 'IPS':7.1, 'IPP':7.4, 'IPV':7.8}
    }

# --- 2. FUNÇÕES DE APOIO ---

def explicar_resultado(dados, prob_risco_decimal):
    """Gera o texto explicativo focando em Estabilidade para alinhar com o gráfico."""
    estabilidade = (1 - prob_risco_decimal) * 100
    indicadores_baixos = [k for k, v in dados.items() if v < 7.0]
    nomes_bonitos = {
        'IDA': 'Desempenho Acadêmico', 'IEG': 'Engajamento',
        'IPS': 'Socioemocional', 'IPP': 'Psicopedagógico', 'IPV': 'Ponto de Virada'
    }
    
    if prob_risco_decimal >= 0.80: # Alerta apenas para riscos muito altos
        msg = f"O modelo identificou um **Índice de Estabilidade de {estabilidade:.1f}%**. "
        if indicadores_baixos:
            detalhes = ", ".join([nomes_bonitos[idx] for idx in indicadores_baixos])
            msg += f"Este diagnóstico sugere atenção prioritária em: **{detalhes}**. "
        msg += "Recomenda-se intervenção pedagógica próxima."
    elif prob_risco_decimal >= 0.50: # Zona de atenção amarela
        msg = f"O aluno apresenta **{estabilidade:.1f}% de estabilidade**. Embora as notas sejam regulares, há um padrão de oscilação comparado à média de 2024."
    else:
        msg = f"O aluno possui **{estabilidade:.1f}% de estabilidade**. Os indicadores atuais refletem segurança e consistência."
    return msg

def gerar_comentario_ia(dados, alerta_ativo, probabilidade, api_key):
    if not api_key or api_key.strip() == "":
        return None
    try:
        genai.configure(api_key=api_key)
        llm = genai.GenerativeModel('gemini-pro')
        status = "em observação" if probabilidade > 0.5 else "estável"
        prompt = f"""
        Você é um consultor pedagógico da Associação Passos Mágicos.
        Analise os indicadores: IDA:{dados['IDA']}, IEG:{dados['IEG']}, IPS:{dados['IPS']}, IPP:{dados['IPP']}, IPV:{dados['IPV']}.
        Índice de Estabilidade: {(1-probabilidade)*100:.1f}%. Status: {status}.
        Escreva um comentário breve (3 frases) e encorajador para o professor.
        """
        response = llm.generate_content(prompt)
        return response.text
    except:
        return "ℹ️ O Mentor Digital está em repouso. O diagnóstico técnico permanece válido."

# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="Mentor Passos Mágicos", layout="wide", page_icon="🌱")

st.sidebar.header("⚙️ Configurações")
GOOGLE_API_KEY = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.caption("Datathon Fase 5 | FIAP Pós-Tech")

st.title("🌱 Mentor Digital Passos Mágicos")
st.markdown("Plataforma de Diagnóstico Preventivo de Defasagem Escolar")

with st.form("predict_form"):
    st.subheader("Inserir Indicadores do Aluno")
    c1, c2, c3, c4, c5 = st.columns(5)
    ida = c1.number_input("IDA", 0.0, 10.0, 7.0, step=0.1)
    ieg = c2.number_input("IEG", 0.0, 10.0, 7.0, step=0.1)
    ips = c3.number_input("IPS", 0.0, 10.0, 7.0, step=0.1)
    ipp = c4.number_input("IPP", 0.0, 10.0, 7.0, step=0.1)
    ipv = c5.number_input("IPV", 0.0, 10.0, 7.0, step=0.1)
    submit = st.form_submit_button("Analisar Desempenho")

if submit:
    # 1. CÁLCULOS
    input_dict = {'IDA': ida, 'IEG': ieg, 'IPS': ips,
