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
with st.expander("Glossário: Entenda os Indicadores (INDE)"):
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
# 6. Processamento e Resultados
if st.button("Executar Análise de Risco", use_container_width=True):
    df_input = pd.DataFrame([input_data])
    
    # Pegamos as probabilidades das duas classes [Classe 0, Classe 1]
    probs = model.predict_proba(df_input)[0]
    
    # IMPORTANTE: Vamos identificar qual classe representa o risco.
    # Se a média das notas for ALTA (>6) e a probabilidade da Classe 0 for ALTA,
    # significa que a Classe 0 é 'Estável' e a Classe 1 é 'Risco'.
    media_atual = df_input.mean(axis=1).values[0]
    
    # Lógica de correção automática de inversão
    if media_atual > 6:
        # Se as notas são boas, o risco deve ser a menor probabilidade
        prob_risco = min(probs) 
    else:
        # Se as notas são baixas, o risco deve ser a maior probabilidade
        prob_risco = max(probs)

    # Definição de cores e status baseada na probabilidade corrigida
    if prob_risco > 0.6:
        cor_status, status_texto = '#e74c3c', "ALTO RISCO"
    elif prob_risco > 0.3:
        cor_status, status_texto = '#f1c40f', "PONTO DE ATENÇÃO"
    else:
        cor_status, status_texto = '#2ecc71', "SITUAÇÃO ESTÁVEL"

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
            st.markdown(f"**Sugestão de Ação:**")
            with st.container(border=True):
            # Lógica de Alerta de Vulnerabilidade Silenciosa
          # --- BLOCO CORRIGIDO E ALINHADO ---
  # --- BLOCO COM INDENTAÇÃO CORRIGIDA ---
with st.container(border=True):
    # O bloco abaixo deve ter 4 espaços a mais que o 'with' acima
    if prob_risco <= 0.3 and (input_data['IPS'] < 5 or input_data['IPP'] < 5):
        st.warning("⚠️ **Vulnerabilidade Silenciosa Detectada**")
        st.write("""
        Embora o risco acadêmico geral seja baixo, os indicadores socioemocionais (IPS/IPP) 
        estão em nível crítico. Recomenda-se apoio psicopedagógico preventivo.
        """)
        st.markdown(f"**Foco do Orientador:** Atenção especial em **{ponto_critico.upper()}**.")

    elif prob_risco > 0.6:
        st.error("⚠️ **ALTO RISCO**")
        st.write(f"**Urgente:** Intervenção focada em **{ponto_critico.upper()}**.")
        # ... restante do seu código de alto risco

    elif prob_risco > 0.3:
        st.warning("⚠️ **PONTO DE ATENÇÃO**")
        st.write(f"**Preventivo:** Reforçar acompanhamento em **{ponto_critico.upper()}**.")

    else:
        st.success("✅ **SITUAÇÃO ESTÁVEL**")
        st.write("**Manutenção:** Continuar incentivando o bom desempenho atual.")

    with col_chart:
        st.subheader("Perfil Comparativo (Radar)")
        
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
# --- RODAPÉ FINAL COM VÍDEO INSTITUCIONAL ---
st.divider()

col_footer1, col_footer2 = st.columns([2, 1])

with col_footer1:
    st.markdown("""
    ### Transformando o Brasil através da Educação
    Como vimos na história da Júlia no vídeo ao lado, a **Passos Mágicos** não entrega apenas ensino, 
    mas sim **perspectiva**. Este projeto de Analytics Engineering visa garantir que nenhum aluno 
    perca essa perspectiva por falta de uma intervenção no momento certo.
    """)

    st.divider()
    
with col_footer2:
    # Exibição do vídeo diretamente na aplicação
    st.video("https://youtu.be/hT_jOmLzpH4")
    st.caption("Assista: Qual a importância de um sonho? - Manifesto Passos Mágicos")

# Rodapé
st.divider()

with st.container():
    st.info("""
    **Você sabia?** O programa da Passos Mágicos inclui educação de qualidade, suporte psicopedagógico e 
    atividades de protagonismo. Este modelo preditivo é uma ferramenta de apoio para que 
    essa 'fórmula mágica' chegue a quem mais precisa no momento certo.
    
    [Visite o site da Associação](https://passosmagicos.org.br/)
    """)
    
st.divider()

with col_footer2:
    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
    st.link_button("Conheça o site oficial", "https://passosmagicos.org.br/")

st.caption("Protótipo desenvolvido para o Datathon Fase 5 - Pós Tech | Mentor Digital © 2026")

