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
    input_dict = {'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}
    input_df = pd.DataFrame([input_dict])[features]
    
    # Probabilidade vinda do modelo (Classe 1 = Risco)
    prob_risco_decimal = model.predict_proba(input_df)[0][1]
    
    porcentagem_risco = prob_risco_decimal * 100
    porcentagem_estabilidade = 100 - porcentagem_risco
    
    # NOVOS LIMITES DE ALERTA:
    # < 0.50: Verde | 0.50 a 0.80: Amarelo | > 0.80: Vermelho
    alerta_critico = prob_risco_decimal >= 0.80
    atencao_moderada = 0.50 <= prob_risco_decimal < 0.80

    st.divider()

    # --- 2. RESULTADOS VISUAIS ---
    col_texto, col_rosca, col_radar = st.columns([1.2, 1, 1.5])

    with col_texto:
        if alerta_critico:
            st.error("⚠️ **Diagnóstico: Atenção Necessária**")
            st.warning(explicar_resultado(input_dict, prob_risco_decimal))
        elif atencao_moderada:
            st.warning("🟡 **Diagnóstico: Observação Preventiva**")
            st.info(explicar_resultado(input_dict, prob_risco_decimal))
        else:
            st.success("✅ **Diagnóstico: Desenvolvimento Estável**")
            st.info(explicar_resultado(input_dict, prob_risco_decimal))

    with col_rosca:
        # Definindo a cor da rosca dinamicamente
        cor_grafico = '#2ecc71' # Verde
        if alerta_critico: cor_grafico = '#e74c3c' # Vermelho
        elif atencao_moderada: cor_grafico = '#f1c40f' # Amarelo

        fig_rosca = go.Figure(go.Pie(
            values=[porcentagem_estabilidade, porcentagem_risco],
            labels=['Estabilidade', 'Risco'],
            hole=.7,
            marker_colors=[cor_grafico, '#f0f2f6'], # Cor ativa vs Fundo cinza
            textinfo='none',
            sort=False
        ))
        fig_rosca.update_layout(
            showlegend=False, height=250, margin=dict(t=0, b=0, l=0, r=0),
            annotations=[dict(text=f'{porcentagem_estabilidade:.0f}%', x=0.5, y=0.5, font_size=30, showarrow=False)]
        )
        st.plotly_chart(fig_rosca, use_container_width=True)
        st.caption("<center>Índice de Estabilidade</center>", unsafe_allow_html=True)

    with col_radar:
        categories = ['IDA', 'IEG', 'IPS', 'IPP', 'IPV']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[ida, ieg, ips, ipp, ipv], theta=categories, fill='toself', name='Este Aluno'))
        fig_radar.add_trace(go.Scatterpolar(r=[baselines['historica'][c] for c in categories], theta=categories, name='Média Histórica', line_dash='dot'))
        fig_radar.add_trace(go.Scatterpolar(r=[baselines['2024'][c] for c in categories], theta=categories, name='Média 2024', line_color='green'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=350, margin=dict(t=50, b=20, l=80, r=80))
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- 3. COMENTÁRIO IA ---
    res_ia = gerar_comentario_ia(input_dict, alerta_critico, prob_risco_decimal, GOOGLE_API_KEY)
    if res_ia:
        with st.expander("✨ Análise Humanizada do Mentor", expanded=True):
            st.write(res_ia)

# --- 4. RODAPÉ ---
st.markdown("---")
st.caption("O Índice de Estabilidade calcula a probabilidade estatística de continuidade do sucesso escolar com base no histórico da associação.")
