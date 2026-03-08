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
    df_input = pd.DataFrame([input_data])
    
    # 1. Pegamos a probabilidade da CLASSE 0 (Risco)
    prob_risco = model.predict_proba(df_input)[0][0]
    
    # 2. Pegamos a classe final predita (0 ou 1)
    classe_predita = model.predict(df_input)[0]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Nível de Risco", f"{prob_risco*100:.1f}%")
        
        # Lógica corrigida: baseada na probabilidade de RISCO
        if prob_risco > 0.6: # Ajustado para 0.6 pois seu modelo dá 0.66 para notas baixas
            st.error("⚠️ ALTO RISCO: Intervenção imediata recomendada.")
        elif prob_risco > 0.3:
            st.warning("PONTOS DE ATENÇÃO: Monitorar evolução.")
        else:
            st.success("SITUAÇÃO ESTÁVEL: Aluno em bom desenvolvimento.")
            
    with col2:
        # Exibe se o modelo classificou como Risco (0) ou Estável (1)
        status = "Risco de Defasagem" if classe_predita == 0 else "Desenvolvimento Normal"
        st.subheader(f"Status Final: {status}")
        
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
