🏎️ SchimiAI: F1 Race Pace & Strategy Analyst

<p align="center">
<img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
<img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg" alt="Streamlit">
<img src="https://img.shields.io/badge/Data%20Source-OpenF1%20API-004351.svg" alt="OpenF1 API">



<a href="#en-project-overview">English</a> •
<a href="#pt-visao-geral-do-projeto">Português</a>
</p>

[EN] Project Overview

SchimiAI is an interactive data analysis web application designed to evaluate Formula 1 race pace, driver consistency, and tire degradation.

The project's name is a tribute to Hannah Schmitz, the Principal Strategy Engineer at Red Bull Racing, renowned for making split-second, race-winning decisions driven entirely by data and statistical models. Just as Hannah transforms raw telemetry into podium finishes, this app aims to transform open-source data into clear, actionable strategic insights.

Using the OpenF1 API, SchimiAI ingests historical timing data, processes it using pandas to isolate true performance from race noise, and renders dynamic visualizations using plotly inside a streamlit web interface.

🚀 Live Demo

🔗 Click here to access the Live Application (Replace this with your actual Streamlit Cloud link once deployed)

🧠 Key Data Insights & Methodology

To analyze performance like a real race strategist, the app applies specific data-wrangling and statistical rules:

• Outlier Removal (Data Cleaning): Automatically filters out pit-out laps (is_pit_out_lap) and uncompleted laps. This ensures pit stop overhead doesn't skew the driver's actual on-track pace.

• Median Race Pace: Uses the Median instead of the Mean to measure core performance. In F1, a single yellow flag or a minor mistake creates a massive outlier (a very slow lap). The median is statistically robust against these anomalies.

• Consistency Metric (Standard Deviation): Calculates the standard deviation of lap times. A lower standard deviation indicates a highly consistent driver who can replicate lap times perfectly—a crucial factor for undercut/overcut strategies.

• LOWESS Trend Analysis: Applies Local Regression lines over the lap scatter plots to visually track performance decline as tires degrade over a stint.

🛠️ Tech Stack

• Language: Python 3

• Data Manipulation: pandas

• API Ingestion: requests

• Data Visualization: plotly & statsmodels (for trendlines)

• Web Framework: streamlit

📦 How to Run Locally (macOS / Linux / Windows)

1. Clone the repository:

[bash]
git clone [https://github.com/mighttly/SchimiAI.git](https://github.com/mighttly/SchimiAI.git)
cd SchimiAI


2. Create and activate a virtual environment:

[bash]
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


3. Install the required dependencies:

[bash]
pip install -r requirements.txt


4. Run the Streamlit application:

[bash]
streamlit run app.py


[PT] Visão Geral do Projeto

O SchimiAI é uma aplicação web interativa de análise de dados projetada para avaliar o ritmo de corrida, a consistência dos pilotos e a degradação dos pneus na Fórmula 1.

O nome do projeto é uma homenagem a Hannah Schmitz, Engenheira Principal de Estratégia da Red Bull Racing, reconhecida globalmente por tomar decisões cruciais que definem vitórias baseando-se puramente em dados e modelos estatísticos. Assim como a Hannah transforma telemetria bruta em pódios, este app busca transformar dados públicos em insights estratégicos claros e acionáveis.

Utilizando a OpenF1 API, o SchimiAI consome dados de tempos de volta, utiliza pandas para limpar os ruídos da corrida (como safety cars e paradas nos boxes) e renderiza visualizações dinâmicas através do plotly dentro de uma interface web ágil criada em streamlit.

🚀 Demonstração Ao Vivo

🔗 Clique aqui para aceder à Aplicação em Produção (Substitui pelo teu link do Streamlit Cloud após o deploy)

🧠 Principais Insights de Dados e Metodologia

Para analisar a performance como um estrategista de corrida real, a aplicação aplica regras específicas de tratamento de dados e estatística:

• Remoção de Outliers (Limpeza de Dados): Filtra automaticamente as voltas de saída de box (is_pit_out_lap) e voltas incompletas. Isso garante que o tempo gasto no pit lane não distorça o ritmo real do piloto na pista.

• Mediana do Ritmo de Corrida: Utiliza a Mediana em vez da Média para medir o desempenho central. Na F1, uma bandeira amarela ou um pequeno erro gera um outlier massivo (uma volta muito lenta). A mediana é estatisticamente robusta contra essas anomalias.

• Métrica de Consistência (Desvio Padrão): Calcula o desvio padrão dos tempos de volta. Um desvio padrão menor indica um piloto altamente consistente que consegue replicar tempos de volta com precisão — fator crucial para estratégias de undercut e overcut.

• Análise de Tendência LOWESS: Aplica linhas de Regressão Local sobre o gráfico de dispersão de voltas para acompanhar visualmente a perda de performance à medida que os pneus se desgastam ao longo de um stint.

🛠️ Tecnologias Utilizadas

• Linguagem: Python 3

• Manipulação de Dados: pandas

• Consumo de API: requests

• Visualização de Dados: plotly e statsmodels (para as linhas de tendência)

• Framework Web: streamlit

📦 Como Executar Localmente (macOS / Linux / Windows)

1. Clone o repositório:

[bash]
git clone [https://github.com/mighttly/SchimiAI.git](https://github.com/mighttly/SchimiAI.git)
cd SchimiAI


2. Crie e ative um ambiente virtual:

[bash]
python3 -m venv venv
source venv/bin/activate  # No Windows usa: venv\Scripts\activate


3. Instale as dependências necessárias:

[bash]
pip install -r requirements.txt


4. Execute a aplicação Streamlit:

[bash]
streamlit run app.py


<p align="center">Developed as a Data Analytics Portfolio Project. 🏁</p>
