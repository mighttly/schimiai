import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(page_title="F1 Race Pace Analyst", layout="wide", page_icon="🏎️")

st.title("🏎️ Formula 1 Race Pace & Tyre Degradation Analyst")
st.markdown("This application extracts and analyzes telemetry/timing data directly from the open-source **OpenF1 API** to evaluate driver performance consistency.")

# Barra lateral para filtros - Usando dados fixos do GP de Abu Dhabi 2024 para garantir o funcionamento do piloto
st.sidebar.header("Race Selection (Demo)")
session_key = 9645  # Abu Dhabi 2024 Race
st.sidebar.text(code=f"Session Key: {session_key} (Abu Dhabi 2024)")

# URLs da OpenF1 API
DRIVERS_URL = f"https://api.openf1.org/v1/drivers?session_key={session_key}"
LAPS_URL = f"https://api.openf1.org/v1/laps?session_key={session_key}"
STINTS_URL = f"https://api.openf1.org/v1/stints?session_key={session_key}"

@st.cache_data
def load_data():
    # 1. Buscar Pilotos
    drivers_res = requests.get(DRIVERS_URL).json()
    df_drivers = pd.DataFrame(drivers_res)[['driver_number', 'broadcast_name', 'team_name', 'team_colour']]
    
    # 2. Buscar Voltas
    laps_res = requests.get(LAPS_URL).json()
    df_laps = pd.DataFrame(laps_res)[['driver_number', 'lap_number', 'lap_duration', 'is_pit_out_lap']]
    
    # 3. Buscar Stints (Pneus)
    stints_res = requests.get(STINTS_URL).json()
    df_stints = pd.DataFrame(stints_res)[['driver_number', 'stint_number', 'compound', 'tyre_age_at_start']]
    
    return df_drivers, df_laps, df_stints

try:
    with st.spinner("Fetching data from OpenF1 API..."):
        df_drivers, df_laps, df_stints = load_data()
    
    # Tratamento e cruzamento de dados (Data Wrangling)
    # Filtrar voltas inválidas (outlaps de pit ou valores nulos)
    df_laps = df_laps.dropna(subset=['lap_duration'])
    df_laps = df_laps[df_laps['is_pit_out_lap'] == False]
    
    # Mapear os stints para cada volta
    # Como o OpenF1 não dá o pneu por volta diretamente, cruzamos os dados aproximados por número de volta
    # Para simplificar o MVP, vamos focar nos top drivers selecionados pelo usuário
    
    # Filtro de Pilotos na interface
    driver_mapping = dict(zip(df_drivers['broadcast_name'], df_drivers['driver_number']))
    selected_drivers = st.multiselect("Select Drivers to Compare:", options=list(driver_mapping.keys()), default=list(driver_mapping.keys())[:3])
    
    if selected_drivers:
        selected_numbers = [driver_mapping[name] for name in selected_drivers]
        
        # Filtrar DataFrames
        df_laps_filtered = df_laps[df_laps['driver_number'].isin(selected_numbers)].copy()
        
        # Juntar com informações do piloto (Nome e Equipe)
        df_analysis = df_laps_filtered.merge(df_drivers, on='driver_number', how='left')
        
        # Métricas de Data Analyst: Mediana do ritmo de corrida e consistência (Desvio Padrão)
        st.subheader("📊 Race Pace Metrics Summary")
        
        metrics_list = []
        for driver in selected_numbers:
            driver_laps = df_analysis[df_analysis['driver_number'] == driver]
            name = df_drivers[df_drivers['driver_number'] == driver]['broadcast_name'].values[0]
            team = df_drivers[df_drivers['driver_number'] == driver]['team_name'].values[0]
            
            median_pace = driver_laps['lap_duration'].median()
            std_dev = driver_laps['lap_duration'].std()
            best_lap = driver_laps['lap_duration'].min()
            
            metrics_list.append({
                "Driver": name,
                "Team": team,
                "Median Lap Time (s)": round(median_pace, 3),
                "Consistency (Std Dev)": round(std_dev, 3),
                "Best Lap (s)": round(best_lap, 3)
            })
            
        st.dataframe(pd.DataFrame(metrics_list).sort_values(by="Median Lap Time (s)"), use_container_width=True)
        
        # Gráfico interativo com Plotly
        st.subheader("📈 Lap-by-Lap Degradation and Pace Trend")
        
        fig = px.scatter(
            df_analysis,
            x="lap_number",
            y="lap_duration",
            color="broadcast_name",
            trendline="lowess", # Linha de tendência para mostrar degradação de pneus/ritmo
            labels={"lap_number": "Lap Number", "lap_duration": "Lap Time (seconds)", "broadcast_name": "Driver"},
            title="Race Pace Evolution (Lower values indicate faster laps)"
        )
        
        fig.update_layout(height=600, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("Please select at least one driver to render the analysis.")

except Exception as e:
    st.error(f"An error occurred while loading or parsing the data: {e}")
    st.info("The OpenF1 API might be experiencing high traffic. Please refresh the page.")