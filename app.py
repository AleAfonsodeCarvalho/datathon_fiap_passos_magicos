import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

# --- 1. CARREGAMENTO DE ASSETS ---
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

def explicar_risco_tecnico(dados, prob_risco):
    indicadores_baixos = [k for k, v in dados.items() if v < 7.0]
    nomes_bonitos = {
        'IDA': 'Desempenho Acadêmico', 'IEG': 'Engajamento',
        'IPS': 'Socioemocional', 'IPP': 'Psicopedagógico', 'IPV': 'Ponto de Virada'
    }
    
    if prob_risco >= 0.40:
        msg = f"O modelo identificou um **risco de {prob_risco*100:.1f}%** com base nos padrões de defasagem. "
        if indicadores_baixos:
            detalhes = ", ".join([nomes_bonitos[idx] for idx in indicadores_baixos])
            msg += f"Este diagnóstico sugere atenção devido às oscilações em: **{detalhes}**. "
        msg += "Recomenda-se um olhar preventivo para apoiar a trajetória do aluno."
    else:
        msg = "Os indicadores atuais refletem um cenário de estabilidade e segurança."
    return msg

def gerar_comentario_ia(dados, risco_ajustado, probabilidade, api_key):
    if not api_key or api_key.strip() == "":
        return None
    try:
        genai.configure(api_key=api_key)
        llm = genai.GenerativeModel('gemini-pro')
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
        return "ℹ️ O Mentor Digital está indisponível agora. O diagnóstico técnico permanece válido."

# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="Mentor Passos Mágicos", layout="wide", page_icon="🌱")

st.sidebar.header("Configurações de IA")
GOOGLE_API_KEY = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.caption("Datathon Fase 5 | FIAP Pós-Tech")

st.title("🌱 Mentor Digital Passos Mágicos")
st.markdown("Plataforma de Diagnóstico Preventivo de Defasagem Escolar")

with st.expander("📖 Guia Rápido de Indicadores"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("📚 IDA: Desempenho Escolar | 🧠 IPP: Processo de Aprendizado")
    with col_b:
        st.write("🔥 IEG: Motivação e Frequência | ❤️ IPS: Relações e Emoções")

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
    # 1. PROCESSAMENTO
    input_dict = {'IDA': ida, 'IEG': ieg, 'IPS': ips, 'IPP': ipp, 'IPV': ipv}
    input_df = pd.DataFrame([input_dict])[features]
    prob_risco = model.predict_proba(input_df)[0][1]
    
    # Sensibilidade: Risco acima de 40% dispara o alerta
    alerta_ativo = prob_risco >= 0.40
    seguranca = (prob_risco) * 100

    st.divider()

    # --- 2. RESULTADOS VISUAIS EM COLUNAS ---
    col_texto, col_rosca, col_radar = st.columns([1.2, 1, 1.5])

    with col_texto:
        if alerta_ativo:
            st.error("⚠️ **Diagnóstico: Atenção Necessária**")
            st.warning(explicar_risco_tecnico(input_dict, prob_risco))
        else:
            st.success("✅ **Diagnóstico: Desenvolvimento Estável**")
            st.info("O aluno apresenta segurança nos indicadores atuais.")

    with col_rosca:
        fig_rosca = go.Figure(go.Pie(
            values=[seguranca, 100 - seguranca],
            labels=['Estabilidade', 'Risco'],
            hole=.7,
            marker_colors=['#2ecc71', '#e74c3c'],
            textinfo='none'
        ))
        fig_rosca.update_layout(showlegend=False, height=250, margin=dict(t=0, b=0, l=0, r=0),
                                annotations=[dict(text=f'{seguranca:.0f}%', x=0.5, y=0.5, font_size=30, showarrow=False)])
        st.plotly_chart(fig_rosca, use_container_width=True)
        st.caption("Índice de Estabilidade do Aluno")

    with col_radar:
        categories = ['IDA', 'IEG', 'IPS', 'IPP', 'IPV']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[ida, ieg, ips, ipp, ipv], theta=categories, fill='toself', name='Este Aluno'))
        fig_radar.add_trace(go.Scatterpolar(r=[baselines['historica'][c] for c in categories], theta=categories, name='Média Histórica', line_dash='dot'))
        fig_radar.add_trace(go.Scatterpolar(r=[baselines['2024'][c] for c in categories], theta=categories, name='Média 2024', line_color='green'))
        
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=350, margin=dict(t=30, b=30, l=80, r=80))
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- 3. COMENTÁRIO IA ---
    res_ia = gerar_comentario_ia(input_dict, alerta_ativo, prob_risco, GOOGLE_API_KEY)
    if res_ia:
        with st.expander("✨ Análise Humanizada do Mentor", expanded=True):
            st.write(res_ia)
    elif not GOOGLE_API_KEY:
        st.info("💡 Insira sua API Key na lateral para habilitar o comentário da IA.")
        
    # --- 4. GLOSSÁRIO E INTERPRETAÇÃO (Abaixo de tudo) ---
    st.markdown("---")
    with st.expander("❓ Entenda como ler este diagnóstico"):
        st.markdown("""
        ### **O que é o Índice de Estabilidade?**
        Este índice representa a segurança do desenvolvimento do aluno. Ele é o inverso da probabilidade de risco: 
        se o modelo detecta **20% de risco**, o aluno possui **80% de estabilidade**. 
        
        * **Acima de 60%:** Trajetória estável. O foco deve ser a manutenção e excelência.
        * **Abaixo de 60%:** Alerta preventivo. Indica que, estatisticamente, o aluno apresenta padrões que precedem a defasagem escolar.

        ### **Como ler o Gráfico Radar?**
        O gráfico radar compara o aluno atual com dois referenciais:
        1.  **Linha Azul (Este Aluno):** Desempenho atual inserido.
        2.  **Linha Pontilhada (Média Histórica):** Desempenho médio de todos os alunos desde o início do programa.
        3.  **Linha Verde (Média 2024):** O padrão de desempenho do último ano letivo.
        
        *Se a linha azul estiver "para dentro" das outras linhas, aquele indicador específico (ex: IEG ou IPS) precisa de atenção imediata.*
        """)
        teste = pd.DataFrame([[7.8, 8.4, 7.0, 7.0, 7.0]], columns=features)
print(model.predict_proba(teste))

  
