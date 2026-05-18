<div align="center">

🏎️ SchimiAI 2.0: Race Strategy & Telemetry Hub

<p align="center">
<img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
<img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg" alt="Streamlit">
<img src="https://img.shields.io/badge/Data%20Source-OpenF1%20API-004351.svg" alt="OpenF1 API">
</p>

English Version • Versão em Português

<a name="en"></a>

[EN] Project Overview

SchimiAI 2.0 is an interactive, advanced data analytics dashboard designed to evaluate Formula 1 race pace, pit strategies, and high-frequency live telemetry.

The project is named after Hannah Schmitz, the legendary Principal Strategy Engineer at Red Bull Racing. She is famous for turning raw timing data, GPS telemetry, and weather forecasts into split-second, race-winning decisions. This hub is built to reflect that same data-driven tactical approach.

By directly consuming the open-source OpenF1 API, this app processes massive streams of live race data and visualizes them across four main functional pillars using responsive, interactive widgets and a premium dark-themed interface.

🚀 Live Demo

🔗 Click here to access the Live Application

📊 Feature Pillars & Data Engineering

1. 🏠 Race Info

Autonomous GPS Mapping: Built a native layout engine that bypasses unreliable external image CDNs. The app fetches coordinates (x, y) directly from the OpenF1 /location endpoint and mathematically projects the circuit shape using Plotly Line charts with aspect ratio locks (scaleanchor).


Session Highlights: Instantly displays the Race Winner, official Fastest Lap with custom driver mapping, circuit location, and dynamic calculations of total race distances.

2. 📊 Race Pace & Tyre Degradation

Standard F1 Time Formatting: Raw API timing in float seconds is parsed and converted using custom delta routines into standard broadcast format (MM:SS.mmm) for hover interactions.


Outlier Scrubbing: Filters out Pit In/Out laps to isolate pure track pace and easily spot tyre performance decay ("hitting the cliff").

3. 🏁 Pit Strategy Analysis

Stint Window Logic: Instead of relying on static tyre ages, the app computes live stint lengths on the fly (stint_length = lap_end - lap_start + 1).


Visual Color Regulations: Integrates custom, high-contrast color mapping corresponding to standard FIA compound specifications (Soft 🟥, Medium 🟨, Hard ⬜, Intermediate 🟩, Wet 🟦).

4. ⚡ Real-Time Telemetry Performance

Vectorized Downsampling: Throttles high-frequency engine streams (3.7Hz) using vectorized pandas slicing (iloc[::40]) to ensure seamless browser rendering without losing peak metrics like DRS top speeds.

<a name="pt"></a>

[PT] Visão Geral do Projeto

O SchimiAI 2.0 é um painel interativo de análise avançada de dados de F1 projetado para avaliar o ritmo de corrida, estratégias de pit stop e telemetria ao vivo de alta frequência.

O nome do projeto é um tributo a Hannah Schmitz, a Engenheira Principal de Estratégia da Red Bull Racing. Hannah é mundialmente conhecida por tomar decisões táticas em frações de segundo que definem vitórias, transformando dados brutos de tempo, telemetria e clima em pódios. Esse app foi desenvolvido para espelhar essa metodologia orientada a dados.

Consumindo dados diretamente da OpenF1 API (pública e de código aberto), a aplicação trata e renderiza fluxos pesados de informações da pista em quatro abas dinâmicas, interativas e com visual premium.

🚀 Demonstração Ao Vivo

🔗 Clique aqui para acessar a Aplicação em Produção

📊 Pilares de Funcionalidades & Engenharia de Dados

1. 🏠 Info da Prova

Traçado Autônomo por GPS: Abandonou a dependência de imagens externas que quebravam constantemente. Agora, o app lê as coordenadas espaciais (x, y) da própria telemetria da corrida e desenha o traçado dinamicamente no Plotly com proporções matemáticas perfeitas (scaleanchor).


Destaques da Sessão: Identificação direta do Vencedor, Volta Rápida oficial formatada, dados do circuito e cálculo dinâmico da quilometragem total.

2. 📊 Ritmo de Corrida & Desgaste de Pneus

Formatação Oficial de Tempo: Os segundos brutos fornecidos pela API são convertidos de forma matemática para o padrão oficial de transmissão da F1 (MM:SS.mmm), exibido nos balões de informação do gráfico de ritmo.


Consistência Limpa: Expurgamos automaticamente voltas com passagem pelos boxes para analisar o ritmo verdadeiro dos carros.

3. 🏁 Análise de Estratégia de Paradas

Duração de Stints: Mapeamento real de quantas voltas cada piloto completou com o mesmo jogo de pneus (stint_length = lap_end - lap_start + 1).


Identidade Visual Oficial: Gráficos adaptados com cores oficiais da FIA (Soft 🟥, Medium 🟨, Hard ⬜, Intermediate 🟩, Wet 🟦).

4. ⚡ Telemetria em Tempo Real

Amostragem Inteligente: Processa logs brutos de telemetria (que rodam a 3.7Hz) utilizando fatiamento vetorizado do Pandas (iloc[::40]) para garantir máxima fluidez visual sem omitir as velocidades de reta mais altas (Top Speed).

🛠️ Tech Stack / Tecnologias

Python 3.10+ • Streamlit • Pandas • Requests • Plotly Express

📦 Run Locally / Como Executar Localmente

[bash]
git clone [https://github.com/mighttly/SchimiAI.git](https://github.com/mighttly/SchimiAI.git)
cd SchimiAI
pip install -r requirements.txt
streamlit run app.py


Developed as an Advanced Data Analytics & Strategy Portfolio Project. 🏁

</div>
