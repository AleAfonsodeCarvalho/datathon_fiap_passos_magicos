import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# 1. Carregamento dos artefatos processados
@st.cache_resource
def load_models():
    # Carregando os arquivos enviados: modelo, lista de features e médias históricas
    model = joblib.load('modelo_risco_passos.pkl')
    features = joblib.load('features_list.pkl')
    medias = joblib.load('medias_comparativas.pkl')
    return model, features, medias

model, features, medias = load_models()

# Configuração da Interface
st.set_page_config(page_title="Passos Mágicos - Mentor Digital", layout="wide")

st.title("🚀 Mentor Digital: Analisador de Risco de Defasagem")
st.markdown("""
Esta ferramenta auxilia na identificação precoce de alunos em risco, utilizando os indicadores 
acadêmicos, psicossociais e de engajamento da **Associação Passos Mágicos**.
""")

# Adicionando o descritivo dos índices em um menu retrátil (Glossário)
with st.expander("📖 Glossário: Entenda os Indicadores (INDE)"):
    st.markdown("""
    Os indicadores abaixo compõem o **Índice de Desenvolvimento Educacional (INDE)**:
    
    * **IDA (Índice de Desempenho Acadêmico):** Média das notas nas disciplinas principais (Português e Matemática).
    * **IEG (Índice de Engajamento):** Mede o compromisso com tarefas, presença e participação.
    * **IPS (Índice Psicossocial):** Bem-estar emocional e contexto familiar (avaliado pela Psicologia).
    * **IPP (Índice de Psicopedagogia):** Evolução cognitiva e superação de barreiras de aprendizagem.
    * **IPV (Índice de Ponto de Virada):** Maturidade e autonomia para o desenvolvimento independente.
    """)

st.divider()

# 2. Entrada de Dados no Corpo Principal
st.subheader("📝 Inserir Indicadores do Aluno")
input_data = {}

# Organizando os inputs em colunas
cols_input = st.columns(len(features))
for i, feature in enumerate(features):
    with cols_input[i]:
        label = feature.replace('_', ' ').upper()
        input_data[feature] = st.number_input(f"{label}", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

st.markdown("---")

# 3. Processamento e Exibição de Resultados
if st.button("Executar Análise de Risco", use_container_width=True):
    df_input = pd.DataFrame([input_data])
    
    # Cálculo da probabilidade de RISCO (Classe 0)
    prob_risco = model.predict_proba(df_input)[0][0]
    
    # Definição de cores e status
    if prob_risco > 0.6:
        cor_status = '#e74c3c' # Vermelho
        status_texto = "ALTO RISCO"
    elif prob_risco > 0.3:
        cor_status = '#f1c40f' # Amarelo
        status_texto = "PONTO DE ATENÇÃO"
    else:
        cor_status = '#2ecc71' # Verde
        status_texto = "SITUAÇÃO ESTÁVEL"

    # Layout de Colunas para os Gráficos
    col_metrics, col_chart = st.columns([1, 2])

    with col_metrics:
        st.subheader("Análise de Risco")
        
        # Gráfico de Rosca (Donut Chart)
        fig_donut = go.Figure(data=[go.Pie(
            values=[prob_risco, 1 - prob_risco],
            hole=.7,
            marker_colors=[cor_status, "#f0f2f6"],
            textinfo='none',
            hoverinfo='none'
        )])
        fig_donut.update_layout(
            annotations=[dict(text=f'{prob_risco*100:.0f}%', x=0.5, y=0.5, font_size=40, showarrow=False, font_color=cor_status)],
            showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown(f"<h3 style='text-align: center; color: {cor_status};'>{status_texto}</h3>", unsafe_allow_html=True)

        # 4. Plano de Ação Automático
        ponto_critico = min(input_data, key=input_data.get)
        nota_critica = input_data[ponto_critico]
        
        st.divider()
        with st.container(border=True):
            st.markdown(f"**🎯 Sugestão de Ação:**")
            if prob_risco > 0.6:
                st.write(f"**Urgente:** Intervenção focada em **{ponto_critico.upper()}**. Convocar equipe multidisciplinar para suporte imediato.")
            elif prob_risco > 0.3:
                st.write(f"**Preventivo:** Reforçar acompanhamento em **{ponto_critico.upper()}** e monitorar engajamento.")
            else:
                st.write("**Manutenção:** Continuar incentivando o bom desempenho atual.")

    with col_chart:
        st.subheader("📊 Perfil Comparativo (Radar)")
        
        categorias = [f.replace('_', ' ') for f in features]
        valores_aluno = list(input_data.values())
        valores_media = [medias.get(f, 5.0) for f in features]

        # Fechar o círculo do radar
        categorias.append(categorias[0])
        valores_aluno.append(valores_aluno[0])
        valores_media.append(valores_media[0])

        fig_radar = go.Figure()
        # Média Geral
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_media, theta=categorias, fill='toself', name='Média Geral',
            line_color='rgba(189, 195, 199, 0.8)'
        ))
        # Aluno
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_aluno, theta=categorias, fill='toself', name='Aluno',
            line_color=cor_status
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True, height=450, margin=dict(l=50, r=50, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# Rodapé
st.divider()
st.caption("Solução desenvolvida para a Associação Passos Mágicos | Datathon Fase 5")
