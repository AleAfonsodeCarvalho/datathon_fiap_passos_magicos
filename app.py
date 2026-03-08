import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# 1. Carregamento dos artefatos
@st.cache_resource
def load_models():
    model = joblib.load('modelo_risco_passos.pkl')
    features = joblib.load('features_list.pkl')
    medias = joblib.load('medias_comparativas.pkl')
    return model, features, medias

model, features, medias = load_models()

st.set_page_config(page_title="Passos Mágicos - Radar de Risco", layout="wide")
st.title("🚀 Mentor Digital: Analisador de Risco")

# 2. Sidebar
st.sidebar.header("Entrada de Indicadores")
input_data = {}
for feature in features:
    label = feature.replace('_', ' ').upper()
    input_data[feature] = st.sidebar.slider(f"{label}", 0.0, 10.0, 5.0)

# 3. Processamento
if st.sidebar.button("Executar Análise"):
    df_input = pd.DataFrame([input_data])
    
    # Probabilidade da Classe 0 (Risco)
    prob_risco = model.predict_proba(df_input)[0][0]
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Resultado da Análise")
        st.metric("Nível de Risco", f"{prob_risco*100:.1f}%")
        
        if prob_risco > 0.6:
            st.error("⚠️ ALTO RISCO: Intervenção prioritária.")
        elif prob_risco > 0.3:
            st.warning("PONTOS DE ATENÇÃO: Monitoramento necessário.")
        else:
            st.success("SITUAÇÃO ESTÁVEL: Bom desenvolvimento.")

    with col2:
        st.subheader("📊 Perfil Multidimensional (Radar)")
        
        # Preparação dos dados para o Radar
        categorias = [f.replace('_', ' ') for f in features]
        valores_aluno = list(input_data.values())
        valores_media = [medias.get(f, 5.0) for f in features]

        # O gráfico radar precisa "fechar" o círculo repetindo o primeiro valor
        categorias.append(categorias[0])
        valores_aluno.append(valores_aluno[0])
        valores_media.append(valores_media[0])

        fig = go.Figure()

        # Camada da Média Geral
        fig.add_trace(go.Scatterpolar(
            r=valores_media,
            theta=categorias,
            fill='toself',
            name='Média Geral',
            line_color='rgba(189, 195, 199, 0.8)'
        ))

        # Camada do Aluno
        fig.add_trace(go.Scatterpolar(
            r=valores_aluno,
            theta=categorias,
            fill='toself',
            name='Aluno Analisado',
            line_color='#2ecc71' if prob_risco < 0.4 else '#e74c3c'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10])
            ),
            showlegend=True,
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("Interface desenvolvida para suporte à decisão pedagógica da Associação Passos Mágicos.")
