import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# 1. Configuração da Interface (Sempre a primeira função de UI)
st.set_page_config(page_title="Passos Mágicos - Mentor Digital", layout="wide", page_icon="🪄")

# --- ESTILIZAÇÃO PERSONALIZADA (CSS) ---
st.markdown(f"""
    <style>
        /* Cor de fundo principal e cor do texto */
        .stApp {{
            background-color: #FFFFFF;
            color: #1E3A8A;
        }}
        
        /* Estilização dos Títulos */
        h1, h2, h3 {{
            color: #1E3A8A !important;
            font-weight: 700;
        }}

        /* Botão principal (Cor Amarela da Passos Mágicos) */
        div.stButton > button:first-child {{
            background-color: #FFC107;
            color: #1E3A8A;
            border-radius: 10px;
            border: none;
            font-weight: bold;
            height: 3em;
            transition: 0.3s;
        }}
        
        div.stButton > button:first-child:hover {{
            background-color: #1E3A8A;
            color: #FFFFFF;
        }}

        /* Estilização dos Expanders e Containers */
        .streamlit-expanderHeader {{
            background-color: #F0F2F6;
            color: #1E3A8A !important;
            border-radius: 5px;
        }}
    </style>
    """, unsafe_allow_html=True)

# 2. Carregamento dos artefatos processados
@st.cache_resource
def load_models():
    # Carregando os arquivos enviados: modelo, lista de features e médias históricas
    model = joblib.load('modelo_risco_passos.pkl')
    features = joblib.load('features_list.pkl')
    medias = joblib.load('medias_comparativas.pkl')
    return model, features, medias

model, features, medias = load_models()

# --- CABEÇALHO COM LOGO PERSONALIZADO (Apenas uma vez) ---
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        # Tenta carregar o logo do repositório
        st.image("passos_magico_logo.png", width=120)
    except:
        # Caso o arquivo não seja encontrado no GitHub
        st.write("🚀")

with col_titulo:
    st.markdown("""
        <style>
            .titulo-header {
                margin-top: 10px;
                color: #1E3A8A;
            }
        </style>
        <h1 class='titulo-header'>Mentor Digital: Analisador de Risco de Defasagem</h1>
    """, unsafe_allow_html=True)

st.markdown("Esta ferramenta auxilia na identificação precoce de alunos em risco utilizando indicadores da **Associação Passos Mágicos**.")

# --- GLOSSÁRIO ---
with st.expander("📖 Glossário: Entenda os Indicadores (INDE)"):
    st.markdown("""
    Os indicadores abaixo compõem o **Índice de Desenvolvimento Educacional (INDE)**:
    
    * **IDA:** Média das notas nas disciplinas principais (Português e Matemática).
    * **IEG:** Mede o compromisso com tarefas, presença e participação.
    * **IPS:** Bem-estar emocional e contexto familiar.
    * **IPP:** Evolução cognitiva e superação de barreiras de aprendizagem.
    * **IPV:** Maturidade e autonomia para o desenvolvimento independente.
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
                st.write(f"**Urgente:** Intervenção focada em **{ponto_critico.upper()}**. O aluno apresenta uma probabilidade alta de defasagem. Recomenda-se:")
                st.write(f"1. **Reunião de Triagem:** Convocar a família e a equipe de psicologia para entender o cenário atual.")
                st.write(f"2. **Foco no {ponto_critico.upper()}:** Como este é o menor índice ({nota_critica}), a intervenção deve priorizar esta área.")
                st.write(f"3. **Plano de Metas:** Estabelecer objetivos semanais de curto prazo para reverter o quadro.")
            elif prob_risco > 0.3:
                st.write(f"**Preventivo:** Reforçar acompanhamento em **{ponto_critico.upper()}** e monitorar engajamento.")
                st.write(f"**Ação Preventiva:** O aluno está em uma zona de alerta. Sugestões:")
                st.write(f"1. **Reforço Direcionado:** Intensificar o acompanhamento em {ponto_critico.upper()}.")
                st.write(f"2. **Mentoria:** Aproximar o aluno de um mentor para aumentar o engajamento.")
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

# --- TEXTO EXPLICATIVO DO GRÁFICO ---
        st.info("""
        **Como interpretar o gráfico:**
        * **Área Cinza:** Representa a média histórica dos alunos da Passos Mágicos.
        * **Área Colorida:** Representa o desempenho atual deste aluno. 
        * **Análise Visual:** Quanto mais "puxada" a teia estiver para as bordas, melhor o desempenho naquela dimensão. Pontas muito próximas ao centro indicam áreas que necessitam de atenção pedagógica.
        """)

# Rodapé
st.divider()
st.caption("Solução desenvolvida para a Associação Passos Mágicos | Datathon Fase 5")
