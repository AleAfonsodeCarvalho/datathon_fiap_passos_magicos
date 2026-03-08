
PÓS-TECH FIAP - DATA ANALYTICS

PROJETO: Mentor Digital - Sistema Preditivo de Risco de Defasagem
ENTIDADE: Associação Passos Mágicos

FASE 5: Deep Learning and Unstructured Data
DATA: 08 de março de 2026
 
ALUNO: Alexandre Afonso de Carvalho
RM: 358820
TURMA: 9DTAT

Sobre o Projeto
O Mentor Digital é uma aplicação preditiva desenvolvida para a Associação Passos Mágicos. Utilizando técnicas de Machine Learning e Analytics Engineering, a ferramenta identifica precocemente alunos em Risco de Defasagem.

O objetivo central é permitir que a equipe de orientadores atue de forma preventiva, focando não apenas no desempenho acadêmico, mas também em indicadores psicossociais e psicopedagógicos.

Tecnologias Utilizadas
Linguagem: Python 3.12

Framework Web: Streamlit
Machine Learning: Scikit-Learn (Random Forest Classifier)
Visualização: Plotly & Plotly Express
Manipulação de Dados: Pandas
Serialização: Joblib

Arquitetura da Solução
A aplicação baseia-se em cinco indicadores fundamentais do INDE (Índice de Desenvolvimento Educacional):

IDA: Indicador de Desempenho Acadêmico.
IEG: Indicador de Engajamento.
IPS: Indicador Psicossocial (Foco em vulnerabilidade).
IPP: Indicador Psicopedagógico (Foco em dificuldades de aprendizado).
IPV: Indicador de Autoconhecimento.

Diferenciais do Modelo
Lógica Híbrida: O modelo combina a predição estatística com regras de negócio para evitar inversões de classe e garantir que alunos com baixa nota em IPS/IPP recebam alertas de "Vulnerabilidade Silenciosa", mesmo com bom desempenho acadêmico.

Comparativo Histórico: Utiliza a mediana de 2024 como régua de comparação no gráfico radar, oferecendo um contexto real do progresso do aluno frente ao grupo.

Estrutura de Arquivos
app.py: Código fonte da aplicação Streamlit.

modelo_risco_passos.pkl: Modelo treinado (Random Forest).
medianas_comparativas.pkl: Dicionário com as medianas dos indicadores para 2024.
features_list.pkl: Ordem das colunas esperadas pelo modelo.
passos_magico_logo.png: Identidade visual da ONG.

Página de hospedagem do analisador do risco de defasagem
https://datathonfiappaappsmagicos-essuh5yqd6avjlhazgaano.streamlit.app/

gradecimentos
Agradeço à equipe da Associação Passos Mágicos pela oportunidade de aplicar tecnologia em prol de um impacto social real e à FIAP pela jornada de aprendizado nesta Pós-Tech.
