🏎️ SchimiAI 2.0: Race Strategy & Telemetry Hub

<p align="center">
<img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
<img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg" alt="Streamlit">
<img src="https://img.shields.io/badge/Data%20Source-OpenF1%20API-004351.svg" alt="OpenF1 API">



<a href="#en">English</a> •
<a href="#pt">Português</a>
</p>

<a name="en"></a>

[EN] Project Overview

SchimiAI 2.0 is an interactive, advanced data analytics dashboard designed to evaluate Formula 1 race pace, pit strategies, and high-frequency live telemetry.

The project is named after Hannah Schmitz, the legendary Principal Strategy Engineer at Red Bull Racing. She is famous for turning raw timing data, GPS telemetry, and weather forecasts into split-second, race-winning decisions. This hub is built to reflect that same data-driven tactical approach.

By directly consuming the open-source OpenF1 API, this app processes massive streams of live race data and visualizes them across three main functional pillars using responsive, interactive widgets.

🚀 Live Demo

🔗 Click here to access the Live Application

📊 Feature Pillars & Data Engineering

1. Race Pace & Tyre Degradation (Pace & Tyres)

• Dynamic Outlier Removal: Filters out pit lane entries/exists and anomalous lap timings (is_pit_out_lap == False) to isolate the true raw pace of each driver.

• Degradation Assessment: Implements responsive multi-driver line chart overlays to monitor exactly when a tyre compound starts dropping in performance ("hitting the cliff").

2. Pit Strategy Analysis (Pit Strategy)

• Strategic Window Calculations: Instead of using raw, uninformative tire age from the start of a stint, the application dynamically calculates the duration of every stint run by the drivers (stint_length = lap_end - lap_start + 1).

• Visual Categorization: Leverages custom color mapping reflecting official FIA compound specifications (Soft 🟥, Medium 🟨, Hard ⬜, Intermediate 🟩, Wet 🟦) for high-impact visual storytelling.

3. Real-Time Telemetry Performance (Real Telemetry)

• Smart Downsampling: Live F1 telemetry stream data can run up to 3.7Hz, which can lag client-side rendering. The app implements dynamic vectorized Pandas slicing (iloc[::40]) to ensure ultra-fast plotting while retaining true peak speed points.

• Top Speed Sourcing: Parses and casts raw telemetry streams on the fly to isolate peak speed metrics.

🛠️ Tech Stack

• Language: Python 3.10+

• Framework: Streamlit (UI & Multi-tab navigation)

• Data Processing: Pandas (Type casting, vectorized sampling, delta calculations)

• API Ingestion: Requests (RESTful API interaction with @st.cache_data throttling layer)

• Visualization: Plotly Express (Dark-themed responsive graphs)

<a name="pt"></a>

[PT] Visão Geral do Projeto

O SchimiAI 2.0 é um painel interativo de análise avançada de dados de F1 projetado para avaliar o ritmo de corrida, estratégias de pit stop e telemetria ao vivo de alta frequência.

O nome do projeto é um tributo a Hannah Schmitz, a Engenheira Principal de Estratégia da Red Bull Racing. Hannah é mundialmente conhecida por tomar decisões táticas em frações de segundo que definem vitórias, transformando dados brutos de tempo, telemetria e clima em pódios. Esse app foi desenvolvido para espelhar essa metodologia orientada a dados.

Consumindo dados diretamente da OpenF1 API (pública e de código aberto), a aplicação trata e renderiza fluxos pesados de informações da pista em três abas dinâmicas e interativas.

🚀 Demonstração Ao Vivo

🔗 Clique aqui para acessar a Aplicação em Produção

📊 Pilares de Funcionalidades & Engenharia de Dados

1. Ritmo de Corrida & Desgaste de Pneus (Ritmo & Pneus)

• Remoção de Outliers: Filtra de forma inteligente voltas inválidas e tempos de entrada/saída de box (is_pit_out_lap == False), isolando a velocidade real de pista dos pilotos.

• Curva de Degradação: Gráficos de linhas interativos sobrepostos que auxiliam a identificar o momento exato em que a vida útil do composto acaba e o piloto perde rendimento.

2. Análise de Estratégia de Paradas (Estratégia de Box)

• Cálculo de Janelas Estratégicas: Substitui a exibição simplória da idade do pneu por um cálculo dinâmico da duração real de cada perna da corrida realizada pelo piloto (stint_length = lap_end - lap_start + 1).

• Identidade Visual Oficial: Aplica paletas de cores correspondentes à regulamentação oficial de compostos da FIA (Soft 🟥, Medium 🟨, Hard ⬜, Intermediate 🟩, Wet 🟦).

3. Telemetria em Tempo Real (Telemetria Real)

• Tratamento de Alta Frequência (Downsampling): Os logs brutos de telemetria dos carros rodam a 3.7Hz, gerando lentidão no navegador. O app implementa amostragem via Pandas Slicing (iloc[::40]) para garantir uma renderização ágil sem perder as marcas de velocidade máxima real (Top Speed).

• Velocidade Máxima Estrita: Faz o cast numérico dinâmico de telemetria bruta para encontrar picos de velocidade de reta.

🛠️ Tecnologias Utilizadas

• Linguagem: Python 3.10+

• Framework: Streamlit (UI e navegação por abas)

• Engenharia de Dados: Pandas (Processamento, amostragem e cálculos de deltas)

• Consumo de API: Requests (Chamadas REST com camada de cache inteligente @st.cache_data)

• Visualização: Plotly Express (Gráficos interativos integrados ao tema escuro)

📦 Run Locally / Como Executar Localmente

1. Clone the repository / Clone o repositório:

[bash]
git clone [https://github.com/mighttly/SchimiAI.git](https://github.com/mighttly/SchimiAI.git)
cd SchimiAI


2. Install requirements / Instale as dependências:

[bash]
pip install -r requirements.txt


3. Run Streamlit / Execute o app:

[bash]
streamlit run app.py


<p align="center">Developed as a Data Analytics Portfolio Project. 🏁</p>