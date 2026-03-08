import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# 1. Carregamento dos artefatos processados
@st.cache_resource
def load_models():
    # Carregando os arquivos enviados pelo usuário
    model = joblib.load('modelo_risco_passos.pkl')
    features = joblib.load('features_list.pkl')
    medias = joblib.load('medias_comparativas.pkl')
    return model, features, medias

model, features, medias = load_models()

# Configuração da Interface
st.set_page_config(page_title="Passos Mágicos - Predição de Risco", layout="wide")
st.title("🚀 Mentor Digital: Analisador de Risco de Defasagem")
st.markdown("""
Esta ferramenta auxilia na identificação precoce de alunos em risco, utilizando os indicadores 
acadêmicos, psicossociais e de engajamento da **Associação Passos Mágicos**.
""")

st.divider()

# 2. Entrada de Dados no Corpo Principal
st.subheader("📝 Inserir Indicadores do Aluno")
input_data = {}

# Organizando os inputs em colunas para não ocupar muito espaço vertical
cols_input = st.columns(len(features))

for i, feature in enumerate(features):
    with cols_input[i]:
        label = feature.replace('_', ' ').upper()
        # Voltando ao number_input como solicitado
        input_data[feature] = st.number_input(f"{label}", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

st.markdown("---")

# 3. Processamento da Predição
if st.button("Executar Análise de Risco", use_container_width=True):
    # Transforma o dicionário em DataFrame (1 linha) para o modelo
    df_input = pd.DataFrame([input_data])
    
    # Cálculo da probabilidade de RISCO (Classe 0)
    prob_risco = model.predict_proba(df_input)[0][0]
    
    # 4. Exibição dos Resultados (Métricas + Gráfico Radar)
    col_metrics, col_chart = st.columns([1, 2])

    with col_metrics:
        st.subheader("Resultado")
        st.metric("Probabilidade de Risco", f"{prob_risco*100:.1f}%")
        
        if prob_risco > 0.6:
            st.error("⚠️ ALTO RISCO: Intervenção imediata recomendada.")
        elif prob_risco > 0.3:
            st.warning("PONTOS DE ATENÇÃO: Monitorar evolução no próximo ciclo.")
        else:
            st.success("SITUAÇÃO ESTÁVEL: Aluno em bom desenvolvimento.")
            
        st.info(f"O modelo analisou as variáveis: {', '.join(features)}.")

    with col_chart:
        st.subheader("📊 Perfil Multidimensional (Radar)")
        
        # Preparação dos dados para o Gráfico Spider
        categorias = [f.replace('_', ' ') for f in features]
        valores_aluno = list(input_data.values())
        valores_media = [medias.get(f, 5.0) for f in features]

        # Fechar o círculo do radar
        categorias.append(categorias[0])
        valores_aluno.append(valores_aluno[0])
        valores_media.append(valores_media[0])

        fig = go.Figure()

        # Camada da Média Geral (Referência)
        fig.add_trace(go.Scatterpolar(
            r=valores_media,
            theta=categorias,
            fill='toself',
            name='Média Geral',
            line_color='rgba(189, 195, 199, 0.8)'
        ))

        # Camada do Aluno Analisado
        # A cor muda conforme o risco
        cor_radar = '#2ecc71' if prob_risco < 0.4 else ('#f1c40f' if prob_risco < 0.6 else '#e74c3c')
        
        fig.add_trace(go.Scatterpolar(
            r=valores_aluno,
            theta=categorias,
            fill='toself',
            name='Aluno',
            line_color=cor_radar
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10])
            ),
            showlegend=True,
            height=450,
            margin=dict(l=50, r=50, t=20, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

# 5. Rodapé informativo
st.divider()
st.caption("Protótipo desenvolvido para o Datathon Fase 5 - Pós Tech. [cite: 3, 4, 6]")
