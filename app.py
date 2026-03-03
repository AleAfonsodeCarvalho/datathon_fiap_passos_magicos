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

# --- FUNÇÃO 1: EXPLICAÇÃO TÉCNICA (Lógica de Alerta) ---
def explicar_risco_tecnico(dados, prob):
    indicadores_baixos = [k for k, v in dados.items() if v < 7.0]
    nomes_bonitos = {
        'IDA': 'Desempenho Acadêmico', 'IEG': 'Engajamento',
        'IPS': 'Socioemocional', 'IPP': 'Psicopedagógico', 'IPV': 'Ponto de Virada'
    }

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
    prob_risco = model.predict_proba(input_df)[0][1]
    seguranca = (1 - prob_risco) * 100

    st.divider()

    # --- COLUNAS DE RESULTADOS VISUAIS ---
    col_texto, col_rosca, col_radar = st.columns([1, 1, 1.5])

    with col_texto:
        if pro_riscob >= 0.40 or prob_risco <= 0.39:
           msg = f"O modelo identificou um **risco de {prob*100:.1f}%** com base nos padrões de defasagem. "
        if indicadores_baixos:
            detalhes = ", ".join([nomes_bonitos[idx] for idx in indicadores_baixos])
            msg += f"Este diagnóstico técnico sugere atenção devido às oscilações em: **{detalhes}**. "
        msg += "Recomenda-se um olhar preventivo para apoiar a trajetória do aluno."
    else:
        msg = "Os indicadores atuais refletem um cenário de estabilidade e segurança no desenvolvimento."
    return msg

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
# --- FUNÇÃO 2: COMENTÁRIO HUMANIZADO (IA) ---
def gerar_comentario_ia(dados, risco_ajustado, probabilidade):
    if not GOOGLE_API_KEY or GOOGLE_API_KEY.strip() == "":
        return None
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        llm = genai.GenerativeModel('gemini-pro')
        # Usamos o status baseado no nosso novo limiar de 40%
        status = "em atenção preventiva" if risco_ajustado else "estável"
        prompt = f"""
        Você é um consultor pedagógico da Associação Passos Mágicos.
        Analise os indicadores: IDA:{dados['IDA']}, IEG:{dados['IEG']}, IPS:{dados['IPS']}, IPP:{dados['IPP']}, IPV:{dados['IPV']}.
        Risco detectado: {probabilidade*100:.1f}%. Status: {status}.
        Escreva um comentário breve (3 frases) e motivador para a equipe de ensino.
        """
        response = llm.generate_content(prompt)
        return response.text
    except:
        return "ℹ️ O Mentor Digital está indisponível agora. O diagnóstico técnico acima permanece válido."

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Passos Mágicos - Diagnóstico", layout="centered", page_icon="🌱")

st.title("🌱 Mentor Digital Passos Mágicos")
st.markdown("Plataforma de Diagnóstico Preventivo de Defasagem Escolar")

with st.expander("📖 Guia Rápido de Indicadores"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**📚 IDA:** Desempenho Escolar")
        st.write("**🧠 IPP:** Processo de Aprendizado")
        st.write("**🔥 IEG:** Motivação e Frequência")
    with col_b:
        st.write("**❤️ IPS:** Relações e Emoções")
        st.write("**✨ IPV:** Protagonismo (Ponto de Virada)")

with st.form("predict_form"):
    st.subheader("Indicadores do Aluno")
    col1, col2 = st.columns(2)
    with col1:
        ida = st.number_input("IDA (Acadêmico)", 0.0, 10.0, 7.0, step=0.1)
        ieg = st.number_input("IEG (Engajamento)", 0.0, 10.0, 7.0, step=0.1)
        ips = st.number_input("IPS (Socioemocional)", 0.0, 10.0, 7.0, step=0.1)
    with col2:
        ipp = st.number_input("IPP (Psicopedagógico)", 0.0, 10.0, 7.0, step=0.1)
        ipv = st.number_input("IPV (Ponto de Virada)", 0.0, 10.0, 7.0, step=0.1)

    submit = st.form_submit_button("Realizar Diagnóstico")

if submit:
    # 1. PREPARAÇÃO E REORDENAÇÃO
    input_dict = {'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}
    input_df = pd.DataFrame([input_dict])
    input_df = input_df[features]

    # 2. PREDIÇÃO
    # Pegamos a probabilidade bruta da classe 1 (risco)
    prob_risco = model.predict_proba(input_df)[0][1]

    # AJUSTE DE SENSIBILIDADE: Se o risco for maior que 40%, já tratamos como Atenção Necessária
    alerta_ativo = prob_risco >= 0.40 or prob_risco < 0.50

    st.divider()

    # 3. RESULTADO TÉCNICO COM LIMIAR CUSTOMIZADO
    if alerta_ativo:
        st.error(f"⚠️ **Diagnóstico Técnico: Atenção Necessária**")
        st.warning(explicar_risco_tecnico(input_dict, prob_risco))
    else:
        st.success(f"✅ **Diagnóstico Técnico: Desenvolvimento Estável**")
        st.info("O aluno apresenta segurança nos indicadores atuais.")

    # 4. RESULTADO DA IA
    res_ia = gerar_comentario_ia(input_dict, alerta_ativo, prob_risco)
    if res_ia:
        with st.expander("✨ Análise Humanizada do Mentor", expanded=True):
            st.write(res_ia)
    elif not GOOGLE_API_KEY:
        st.info("💡 Para receber uma análise humanizada detalhada, configure sua API Key na barra lateral.")

st.sidebar.markdown("---")
st.sidebar.caption("Datathon Fase 5 | FIAP Pós-Tech")
