import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SchimiAI - F1 Race Pace Analyst", layout="wide", page_icon="🏎️")

# --- SELETOR DE IDIOMA (DICIONÁRIO DE TRADUÇÃO) ---
# Criamos uma estrutura simples de dicionário para alternar os textos do app
st.sidebar.header("🌐 Language / Idioma")
language = st.sidebar.selectbox("Choose Language:", ["Português", "English"])

texts = {
    "Português": {
        "title": "🏎️ SchimiAI: Análise de Ritmo de Corrida e Degradação de Pneus",
        "subtitle": "Este aplicativo extrai e analisa dados de tempos de volta diretamente da **OpenF1 API** para avaliar a consistência dos pilotos.",
        "sidebar_config": "Configurações da Corrida",
        "select_year": "Selecione o Ano:",
        "select_gp": "Selecione o Grande Prêmio (Sessão):",
        "select_drivers": "Selecione os Pilotos para Comparar:",
        "loading_gps": "Buscando GPs no OpenF1...",
        "loading_data": "Buscando dados de telemetria e voltas...",
        "summary_title": "📊 Resumo das Métricas de Ritmo de Corrida",
        "chart_title": "📈 Tendência de Ritmo e Evolução de Voltas",
        "chart_desc": "Ritmo de Corrida (Valores menores indicam voltas mais rápidas)",
        "best_lap": "Melhor Volta (s)",
        "median_pace": "Mediana (Ritmo)",
        "consistency": "Consistência (Desvio Padrão)",
        "warning_driver": "Por favor, selecione pelo menos um piloto na barra lateral.",
        "error_api": "A API OpenF1 está instável ou a sessão não possui dados de volta limpos no momento. Tente outro GP."
    },
    "English": {
        "title": "🏎️ SchimiAI: Race Pace & Tyre Degradation Analyst",
        "subtitle": "This application extracts and analyzes timing data directly from the open-source **OpenF1 API** to evaluate driver performance consistency.",
        "sidebar_config": "Race Configuration",
        "select_year": "Select Year:",
        "select_gp": "Select Grand Prix (Session):",
        "select_drivers": "Select Drivers to Compare:",
        "loading_gps": "Fetching GPs from OpenF1...",
        "loading_data": "Fetching telemetry and lap data...",
        "summary_title": "📊 Race Pace Metrics Summary",
        "chart_title": "📈 Lap-by-Lap Degradation and Pace Trend",
        "chart_desc": "Race Pace Evolution (Lower values indicate faster laps)",
        "best_lap": "Best Lap (s)",
        "median_pace": "Median Lap Time (s)",
        "consistency": "Consistency (Std Dev)",
        "warning_driver": "Please select at least one driver to render the analysis.",
        "error_api": "The OpenF1 API might be unstable or this session doesn't have clean lap data right now. Try another GP."
    }
}

t = texts[language]

# --- TÍTULO PRINCIPAL ---
st.title(t["title"])
st.markdown(t["subtitle"])

# --- FUNÇÃO PARA PEGAR DADOS DA API ---
@st.cache_data(show_spinner=False)
def get_f1_data(endpoint, params=None):
    base_url = "https://api.openf1.org/v1/"
    try:
        response = requests.get(base_url + endpoint, params=params, timeout=10)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        return pd.DataFrame()
    return pd.DataFrame()

# --- BARRA LATERAL (FILTROS DINÂMICOS) ---
st.sidebar.header(f"⚙️ {t['sidebar_config']}")

# 1. Escolha do Ano (2023 em diante)
year = st.sidebar.selectbox(t["select_year"], [2023, 2024, 2025, 2026])

# 2. Buscar dinamicamente todas as corridas (Sessões do tipo 'Race') daquele ano
with st.spinner(t["loading_gps"]):
    df_sessions = get_f1_data("sessions", {"year": year, "session_name": "Race"})

if not df_sessions.empty:
    # Criar uma opção amigável combinando País e Nome do Circuito
    df_sessions['gp_display'] = df_sessions['country_name'] + " - " + df_sessions['location']
    gp_options = df_sessions.set_index('session_key')['gp_display'].to_dict()
    
    selected_session_key = st.sidebar.selectbox(
        t["select_gp"], 
        options=list(gp_options.keys()), 
        format_func=lambda x: gp_options[x]
    )
    
    # 3. Buscar Pilotos e Voltas da Corrida Selecionada
    with st.spinner(t["loading_data"]):
        df_drivers = get_f1_data("drivers", {"session_key": selected_session_key})
        df_laps = get_f1_data("laps", {"session_key": selected_session_key})
        
    if not df_drivers.empty and not df_laps.empty:
        # Criar seletor dinâmico de pilotos baseado em quem correu aquela prova
        driver_mapping = dict(zip(df_drivers['broadcast_name'], df_drivers['driver_number']))
        driver_options = sorted(list(driver_mapping.keys()))
        
        selected_drivers = st.sidebar.multiselect(
            t["select_drivers"], 
            options=driver_options, 
            default=driver_options[:3] if len(driver_options) >= 3 else driver_options
        )
        
        # --- PROCESSAMENTO E ANÁLISE ---
        if selected_drivers:
            selected_numbers = [driver_mapping[name] for name in selected_drivers]
            
            # Tratamento de dados (Limpeza de Outliers / Pit Stops)
            df_laps_filtered = df_laps[df_laps['driver_number'].isin(selected_numbers)].copy()
            df_laps_filtered = df_laps_filtered.dropna(subset=['lap_duration'])
            df_laps_filtered = df_laps_filtered[df_laps_filtered['is_pit_out_lap'] == False]
            
            # Cruzamento de tabelas (Merge)
            df_analysis = df_laps_filtered.merge(df_drivers[['driver_number', 'broadcast_name', 'team_name']], on='driver_number', how='left')
            
            if not df_analysis.empty:
                # 📊 TABELA DE MÉTRICAS ESTATÍSTICAS
                st.subheader(t["summary_title"])
                
                metrics_list = []
                for driver in selected_numbers:
                    driver_laps = df_analysis[df_analysis['driver_number'] == driver]
                    if not driver_laps.empty:
                        name = df_drivers[df_drivers['driver_number'] == driver]['broadcast_name'].values[0]
                        team = df_drivers[df_drivers['driver_number'] == driver]['team_name'].values[0]
                        
                        metrics_list.append({
                            "Driver/Piloto": name,
                            "Team/Equipe": team,
                            t["median_pace"]: round(driver_laps['lap_duration'].median(), 3),
                            t["consistency"]: round(driver_laps['lap_duration'].std(), 3),
                            t["best_lap"]: round(driver_laps['lap_duration'].min(), 3)
                        })
                
                st.dataframe(pd.DataFrame(metrics_list).sort_values(by=t["median_pace"]), use_container_width=True)
                
                # 📈 GRÁFICO INTERATIVO COM PLOTLY
                st.subheader(t["chart_title"])
                
                fig = px.scatter(
                    df_analysis,
                    x="lap_number",
                    y="lap_duration",
                    color="broadcast_name",
                    trendline="lowess",  # Linha de tendência estatística para degradação de pneu
                    labels={"lap_number": "Lap / Volta", "lap_duration": "Time / Tempo (s)", "broadcast_name": "Driver / Piloto"},
                    title=t["chart_desc"]
                )
                
                fig.update_layout(height=600, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(t["error_api"])
        else:
            st.info(t["warning_driver"])
    else:
        st.error(t["error_api"])
else:
    st.error(t["error_api"])