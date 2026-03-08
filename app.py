import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go # Para os gráficos de Rosca e Radar
import google.generativeai as genai

# --- CARREGAMENTO DE ASSETS ---
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')
# Carrega as médias para o gráfico de Radar (gerado no Passo 1)
try:
    baselines = joblib.load('medias_comparativas.pkl')
except:
    # Médias fictícias caso o arquivo não exista (apenas para o app não quebrar)
    baselines = {'historica': {'IDA':7, 'IEG':7, 'IPS':7, 'IPP':7, 'IPV':7}, 
                 '2024': {'IDA':7.5, 'IEG':7.2, 'IPS':7.1, 'IPP':7.4, 'IPV':7.8}}

# --- CONFIGURAÇÃO DA API KEY ---
st.sidebar.header("Configurações de IA")
GOOGLE_API_KEY = st.sidebar.text_input("Gemini API Key", type="password")

# --- INTERFACE ---
st.set_page_config(page_title="Mentor Passos Mágicos", layout="wide")
st.title("🌱 Mentor Digital Passos Mágicos")

with st.form("predict_form"):
    st.subheader("Indicadores do Aluno")
    c1, c2, c3, c4, c5 = st.columns(5)
    ida = c1.number_input("IDA", 0.0, 10.0, 7.0)
    ieg = c2.number_input("IEG", 0.0, 10.0, 7.0)
    ips = c3.number_input("IPS", 0.0, 10.0, 7.0)
    ipp = c4.number_input("IPP", 0.0, 10.0, 7.0)
    ipv = c5.number_input("IPV", 0.0, 10.0, 7.0)
    submit = st.form_submit_button("Analisar Desempenho")

if submit:
    # 1. PREDIÇÃO
    input_dict = {'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}
    input_df = pd.DataFrame([input_dict])[features]
    prob_risco = 1-model.predict_proba(input_df)[0][1]
    seguranca = (1 - prob_risco) * 100

    st.divider()
    
    # --- COLUNAS DE RESULTADOS VISUAIS ---
    col_texto, col_rosca, col_radar = st.columns([1, 1, 1.5])

    with col_texto:
        if prob_risco>= 0.40 or prob_risco<= 0.55:
            st.error("⚠️ **Atenção Necessária**")
            st.write(f"O modelo detectou um risco de {prob_risco*100:.1f}%.")
        else:
            st.success("✅ **Desenvolvimento Estável**")
            st.write("O aluno segue em trajetória segura.")

    # 2. GRÁFICO DE ROSCA (% de Segurança/Estabilidade)
    with col_rosca:
        fig_rosca = go.Figure(go.Pie(
            values=[seguranca, 100-seguranca],
            labels=['Estabilidade', 'Risco'],
            hole=.7,
            marker_colors=['#2ecc71', '#e74c3c'],
            textinfo='none'
        ))
        fig_rosca.update_layout(
            showlegend=False, height=250, margin=dict(t=0, b=0, l=0, r=0),
            annotations=[dict(text=f'{seguranca:.0f}%', x=0.5, y=0.5, font_size=30, showarrow=False)]
        )
        st.plotly_chart(fig_rosca, use_container_width=True)
        st.caption("Índice de Estabilidade Pedagógica")

    # 3. GRÁFICO DE RADAR (Comparativo)
    with col_radar:
        categories = ['IDA', 'IEG', 'IPS', 'IPP', 'IPV']
        fig_radar = go.Figure()

        # Notas do Aluno
        fig_radar.add_trace(go.Scatterpolar(
            r=[ida, ieg, ips, ipp, ipv], theta=categories, fill='toself', name='Este Aluno', line_color='blue'
        ))
        # Média Histórica
        fig_radar.add_trace(go.Scatterpolar(
            r=[baselines['historica'][c] for c in categories], theta=categories, name='Média Histórica', line_color='gray', line_dash='dot'
        ))
        # Média 2024
        fig_radar.add_trace(go.Scatterpolar(
            r=[baselines['2024'][c] for c in categories], theta=categories, name='Média 2024', line_color='green'
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True, height=350, margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 4. COMENTÁRIO IA (Opcional)
    if GOOGLE_API_KEY:
        with st.expander("✨ Ver Análise Humanizada do Mentor", expanded=True):
            # (Aqui entra sua função gerar_comentario_ia já existente)
            st.write("Análise da IA baseada no seu código anterior...")

st.sidebar.markdown("---")
st.sidebar.caption("Datathon Fase 5 | FIAP Pós-Tech")
