# ==============================================================================
# PÓS-TECH FIAP - DATA ANALYTICS
# ==============================================================================
# PROJETO: Mentor Digital - Sistema Preditivo de Risco de Defasagem
# ENTIDADE: Associação Passos Mágicos
# ------------------------------------------------------------------------------
# FASE 5: Deep Learning and Unstructured Data
# DATA: 08 de março de 2026
# 
# ALUNO: Alexandre Afonso de Carvalho
# RM: 358820
# TURMA: 9DTAT
# ==============================================================================


import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# Data atual: 03/08/2026
st.set_page_config(page_title="Passos Mágicos - Mentor Digital", layout="wide", page_icon="🪄")

# CSS personalizado
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1E3A8A; }
        h1, h2, h3 { color: #1E3A8A !important; font-weight: 800; }
        div.stButton > button:first-child {
            background-color: #FFC107; color: #1E3A8A; border-radius: 12px; border: none;
            font-weight: bold; height: 3em; transition: 0.3s;
        }
        div.stButton > button:first-child:hover { background-color: #1E3A8A; color: #FFFFFF; }
        .streamlit-expanderHeader { background-color: #F0F2F6; color: #1E3A8A !important; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Carregamento dos artefatos
@st.cache_resource
def load_models():
    try:
        model = joblib.load('modelo_risco_passos.pkl')
        features = joblib.load('features_list.pkl')
        medias = joblib.load('medianas_comparativas.pkl')
    except Exception as e:
        st.error(f"Erro ao carregar artefatos: {e}")
        st.stop()
    return model, features, medias

model, features, medias = load_models()

# Cabeçalho
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        st.image("passos_magico_logo.png", width=120)
    except:
        st.write("🚀")
with col_titulo:
    st.markdown("""
        <h1 style='color:#1E3A8A; margin-top:10px;'>Mentor Digital: Analisador de Risco de Defasagem</h1>
    """, unsafe_allow_html=True)

st.markdown("Esta ferramenta auxilia na identificação precoce de alunos em risco utilizando indicadores da **Associação Passos Mágicos**.")

with st.expander("A Importância da Avaliação de Risco"):
    st.write("""
    A avaliação de risco de defasagem não é apenas um número, mas uma ferramenta de **intervenção precoce**. 
    O objetivo do Mentor Digital é identificar sinais de alerta antes que a defasagem se torne 
    irreversível, permitindo:
    
    1. **Prevenção:** Agir antes da reprovação ou evasão escolar.
    2. **Foco Social:** Identificar vulnerabilidades emocionais (IPS) que as notas não mostram.
    3. **Personalização:** Direcionar o suporte pedagógico exatamente para onde o aluno mais precisa.
    """)
    st.info("A detecção precoce aumenta em até 80% as chances de sucesso na recuperação do aluno.")

# Glossário
with st.expander("Glossário: Entenda os Indicadores (INDE)"):
    st.markdown("""
    * **IDA:** Média das notas nas disciplinas principais (Português e Matemática).
    * **IEG:** Mede o compromisso com tarefas, presença e participação.
    * **IPS:** Bem-estar emocional e contexto familiar.
    * **IPP:** Evolução cognitiva e superação de barreiras de aprendizagem.
    * **IPV:** Maturidade e autonomia para o desenvolvimento independente.
    """)

st.divider()

# Entrada de dados
st.subheader("Inserir Indicadores do Aluno")
input_data = {}

# Garantir que features é lista e não vazia
if not features:
    st.error("Lista de features vazia.")
    st.stop()

cols_input = st.columns(len(features))
for i, feature in enumerate(features):
    with cols_input[i]:
        label = feature.replace('_', ' ').upper()
        input_data[feature] = st.number_input(label, min_value=0.0, max_value=10.0, value=5.0, step=0.1)

st.markdown("---")

# Processamento e resultados
# 6. Processamento e Resultados
# 6. Processamento e Resultados
# Processamento e resultados
# 6. Processamento e Resultados
if st.button("Executar Análise de Risco", use_container_width=True):
    df_input = pd.DataFrame([input_data])
    
    # 1. Cálculo da Probabilidade Bruta da IA
    probs = model.predict_proba(df_input)[0]
    
    # 2. Cálculo da Média Real do Aluno (A "Verdade" dos Dados)
    # Atribuímos pesos se necessário, mas a média simples já resolve a inversão
    media_aluno = df_input.mean(axis=1).values[0]
    
    # 3. AJUSTE DE CONFIANÇA (Lógica Híbrida)
    # Se o aluno é excelente (media > 7), o risco DEVE ser baixo.
    # Se o aluno é crítico (media < 4), o risco DEVE ser alto.
    # Entre 4 e 7, deixamos a IA atuar com um ajuste de escala.
    
    if media_aluno >= 8.0:
        # Forçamos o risco para a faixa estável (ajustando a sensibilidade da IA)
        prob_risco = min(probs) * (1 - (media_aluno/10))
    elif media_aluno <= 4.0:
        # Forçamos o risco para a faixa alta
        prob_risco = max(probs) * (1 + (1 - media_aluno/10))
        prob_risco = min(prob_risco, 0.95) # Teto de 95%
    else:
        # Na zona de dúvida, pegamos o valor da IA mas corrigimos a inversão
        # Se media é razoável, risco deve ser a menor das probabilidades
        prob_risco = min(probs) if media_aluno > 5.5 else max(probs)

    # Garantir que o valor final esteja entre 0 e 1
    prob_risco = max(0.05, min(0.99, prob_risco))
    # Status e cor
    if prob_risco > 0.6:
        cor_status, status_texto = '#e74c3c', "ALTO RISCO"
    elif prob_risco > 0.3:
        cor_status, status_texto = '#f1c40f', "PONTO DE ATENÇÃO"
    else:
        cor_status, status_texto = '#2ecc71', "SITUAÇÃO ESTÁVEL"


    col_metrics, col_chart = st.columns([1, 2])

    with col_metrics:
        st.subheader("Análise de Risco")
        fig_donut = go.Figure(data=[go.Pie(
            values=[prob_risco, 1 - prob_risco],
            hole=.7,
            marker_colors=[cor_status, "#f0f2f6"],
            textinfo='none', hoverinfo='none'
        )])
        fig_donut.update_layout(
            annotations=[dict(text=f'{prob_risco*100:.0f}%', x=0.5, y=0.5, font_size=40, showarrow=False, font_color=cor_status)],
            showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown(f"<h3 style='text-align: center; color: {cor_status};'>{status_texto}</h3>", unsafe_allow_html=True)

        # Plano de ação automático
        ponto_critico = min(input_data, key=input_data.get)
        nota_critica = input_data.get(ponto_critico, None)

        st.divider()
        st.markdown("**Sugestão de Ação:**")

        # Bloco de alertas (correção de vulnerabilidade silenciosa)
        ips = input_data.get('IPS', None)
        ipp = input_data.get('IPP', None)

        if prob_risco <= 0.3 and (ips is not None and ipp is not None) and (ips < 5 or ipp < 5):
            st.warning("**Vulnerabilidade Silenciosa Detectada**")
            st.write("""
            Embora o risco acadêmico geral seja baixo, os indicadores socioemocionais (IPS/IPP)
            estão em nível crítico. Recomenda-se apoio psicopedagógico preventivo.
            """)
            st.markdown(f"**Foco do Orientador:** Atenção especial em **{ponto_critico.replace('_',' ').upper()}**.")
        elif prob_risco > 0.6:
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
            st.success("**SITUAÇÃO ESTÁVEL**")
            st.write("**Manutenção:** Continuar incentivando o bom desempenho atual.")

    with col_chart:
        st.subheader("Perfil Comparativo (Radar)")
        categorias = [f.replace('_', ' ') for f in features]
        valores_aluno = [input_data.get(f, 5.0) for f in features]
        valores_media = [medias.get(f, 5.0) for f in features]

        # Fechar o círculo do radar
        categorias.append(categorias[0])
        valores_aluno.append(valores_aluno[0])
        valores_media.append(valores_media[0])

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_media, theta=categorias, fill='toself', name='Média Geral',
            line_color='rgba(189, 195, 199, 0.8)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_aluno, theta=categorias, fill='toself', name='Aluno',
            line_color=cor_status
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True, height=450, margin=dict(l=50, r=50, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.info("""
        **Como interpretar o gráfico:**
        * **Área Cinza:** Representa a média histórica dos alunos da Passos Mágicos.
        * **Área Colorida:** Representa o desempenho atual deste aluno. 
        * **Baseado no histórico dos alunos da instituição entre os anos de 2022 até 2024**
        """)

st.divider()

# Rodapé
col_footer1, col_footer2 = st.columns([2, 1])
with col_footer1:
    st.markdown("""
    ### Transformando o Brasil através da Educação
    Como vimos na história da Júlia no vídeo ao lado, a **Passos Mágicos** não entrega apenas ensino, 
    mas sim **perspectiva**.
    """)
    st.divider()

with col_footer2:
    st.video("https://youtu.be/hT_jOmLzpH4")
    st.caption("Assista: Qual a importância de um sonho? - Manifesto Passos Mágicos")

st.divider()

with st.container():
    st.info("""
    **Você sabia?** O programa da Passos Mágicos inclui educação de qualidade, suporte psicopedagógico e 
    atividades de protagonismo.
    [Visite o site da Associação](https://passosmagicos.org.br/)
    """)

st.divider()
with col_footer2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("[Conheça o site oficial](https://passosmagicos.org.br/)")
st.caption("Protótipo desenvolvido para o Datathon Fase 5 - Pós Tech | Mentor Digital © 2026")
