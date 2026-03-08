import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# 1. Carregamento dos artefatos processados
@st.cache_resource
def load_models():
    model = joblib.load('modelo_risco_passos.pkl')
    features = joblib.load('features_list.pkl')
    medias = joblib.load('medias_comparativas.pkl')
    return model, features, medias

model, features, medias = load_models()

# Configuração da Interface
st.set_page_config(page_title="Passos Mágicos - Predição de Risco", layout="wide")
st.title("🚀 Mentor Digital: Analisador de Risco de Defasagem")
st.markdown("Utilize os indicadores abaixo para identificar alunos que precisam de atenção prioritária.")

# 2. Sidebar para entrada de dados
st.sidebar.header("Entrada de Indicadores")
input_data = {}

# Criar inputs dinamicamente com base nas features do seu modelo
for feature in features:
    # Ajusta o label para algo mais amigável se necessário
    label = feature.replace('_', ' ').upper()
    input_data[feature] = st.sidebar.number_input(f"{label}", min_value=0.0, max_value=10.0, value=5.0)

# 3. Processamento da Predição
if st.sidebar.button("Executar Análise de Risco"):
    # Transforma o dicionário em DataFrame (1 linha)
    df_input = pd.DataFrame([input_data])
    
    # Predição
    probabilidade = model.predict_proba(df_input)[0][1]
    classe = model.predict(df_input)[0]

    # 4. Exibição dos Resultados
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Probabilidade de Risco", f"{probabilidade*100:.1f}%")
        if probabilidade > 0.6:
            st.error("⚠️ ALTO RISCO: Intervenção imediata recomendada.")
        elif probabilidade > 0.3:
            st.warning("PONTOS DE ATENÇÃO: Monitorar evolução no próximo ciclo.")
        else:
            st.success("SITUAÇÃO ESTÁVEL: Aluno em bom desenvolvimento.")

    with col2:
        # Comparação visual com as médias (usando o arquivo medias_comparativas.pkl)
        st.subheader("Comparativo com a Média Geral")
        
        # Criando um gráfico simples para mostrar onde o aluno está em relação à média
        df_comp = pd.DataFrame({
            'Indicador': list(input_data.keys()),
            'Aluno': list(input_data.values()),
            'Média Geral': [medias.get(f, 5.0) for f in features] # Fallback para 5.0 se não achar
        }).melt(id_vars='Indicador', var_name='Tipo', value_name='Nota')

        fig = px.bar(df_comp, x='Indicador', y='Nota', color='Tipo', barmode='group',
                     color_discrete_map={'Aluno': '#2ecc71', 'Média Geral': '#bdc3c7'})
        st.plotly_chart(fig, use_container_width=True)

# 5. Rodapé informativo
st.divider()
st.info("Este modelo utiliza os indicadores IDA, IEG, IPS, IPP e IAN para calcular a vulnerabilidade acadêmica conforme os critérios do Datathon Fase 5.")
