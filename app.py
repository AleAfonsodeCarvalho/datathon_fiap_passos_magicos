import streamlit as st
import joblib
import pandas as pd
import google.generativeai as genai

# --- CARREGAMENTO DE ASSETS ---
model = joblib.load('modelo_risco_passos.pkl')
features = joblib.load('features_list.pkl')

# --- CONFIGURAÇÃO DA API KEY (SIDEBAR) ---
st.sidebar.header("Configurações de IA")
GOOGLE_API_KEY = st.sidebar.text_input(
    "Insira sua Gemini API Key", 
    type="password", 
    help="Opcional: Necessária apenas para o comentário do Mentor Digital."
)

# --- FUNÇÃO 1: EXPLICAÇÃO TÉCNICA (Lógica de Alerta) ---
def explicar_risco_tecnico(dados, prob):
    indicadores_baixos = [k for k, v in dados.items() if v < 7.0]
    nomes_bonitos = {
        'IDA': 'Desempenho Acadêmico', 'IEG': 'Engajamento',
        'IPS': 'Socioemocional', 'IPP': 'Psicopedagógico', 'IPV': 'Ponto de Virada'
    }
    
    # Mensagem para quando há risco detectado
    if prob >= 0.40: # Ajustamos o limiar para 40% para ser mais preventivo
        msg = f"O modelo identificou um **risco de {prob*100:.1f}%** com base nos padrões de defasagem. "
        if indicadores_baixos:
            detalhes = ", ".join([nomes_bonitos[idx] for idx in indicadores_baixos])
            msg += f"Este diagnóstico técnico sugere atenção devido às oscilações em: **{detalhes}**. "
        msg += "Recomenda-se um olhar preventivo para apoiar a trajetória do aluno."
    else:
        msg = "Os indicadores atuais refletem um cenário de estabilidade e segurança no desenvolvimento."
    return msg

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
    alerta_ativo = prob_risco >= 0.40

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
