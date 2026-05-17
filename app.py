import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SchimiAI 2.0 - F1 Strategy Hub", layout="wide", page_icon="🏎️")

# --- DICIONÁRIO DE TRADUÇÃO ---
st.sidebar.header("🌐 Language / Idioma")
language = st.sidebar.selectbox("Choose Language:", ["Português", "English"])

texts = {
    "Português": {
        "title": "🏎️ SchimiAI 2.0: Strategy & Telemetry Hub",
        "subtitle": "Análise avançada inspirada na engenharia de estratégia de Hannah Schmitz.",
        "tab0": "🏠 Info da Prova",
        "tab1": "📊 Ritmo & Pneus",
        "tab2": "🏁 Estratégia de Box",
        "tab3": "⚡ Telemetria Real",
        "select_year": "Ano:",
        "select_gp": "Grande Prêmio:",
        "select_drivers": "Pilotos:",
        "loading": "Processando dados...",
        "race_winner": "Vencedor da Prova",
        "fastest_lap": "Volta mais Rápida",
        "circuit_name": "Circuito",
        "location": "Localização",
        "track_length": "Comprimento da Pista",
        "total_km": "Distância Total",
        "stint_title": "Histórico de Pneus (Stints)",
        "speed_analysis": "Análise de Velocidade Máxima",
        "no_data": "Dados não disponíveis.",
        "error_api": "Conexão com a OpenF1 API falhou ou a sessão não possui dados limpos."
    },
    "English": {
        "title": "🏎️ SchimiAI 2.0: Strategy & Telemetry Hub",
        "subtitle": "Advanced analytics inspired by Hannah Schmitz's strategy engineering.",
        "tab0": "🏠 Race Info",
        "tab1": "📊 Pace & Tyres",
        "tab2": "🏁 Pit Strategy",
        "tab3": "⚡ Real Telemetry",
        "select_year": "Year:",
        "select_gp": "Grand Prix:",
        "select_drivers": "Drivers:",
        "loading": "Processing data...",
        "race_winner": "Race Winner",
        "fastest_lap": "Fastest Lap",
        "circuit_name": "Circuit",
        "location": "Location",
        "track_length": "Track Length",
        "total_km": "Total Distance",
        "stint_title": "Tyre History (Stints)",
        "speed_analysis": "Top Speed Analysis",
        "no_data": "Data not available.",
        "error_api": "Connection to OpenF1 API failed or the session has no clean data."
    }
}
t = texts[language]

# --- METADADOS DAS PISTAS (Distâncias Oficiais em KM) ---
track_meta = {
    "Bahrain": 5.412, "Jeddah": 6.174, "Melbourne": 5.278, "Suzuka": 5.807, "Shanghai": 5.451,
    "Miami": 5.412, "Imola": 4.909, "Monaco": 3.337, "Montreal": 4.361, "Barcelona": 4.657,
    "Spielberg": 4.318, "Silverstone": 5.891, "Budapest": 4.381, "Spa": 7.004, "Zandvoort": 4.259,
    "Monza": 5.793, "Baku": 6.003, "Singapore": 4.940, "Austin": 5.513, "Mexico City": 4.304,
    "Sao Paulo": 4.309, "Las Vegas": 6.201, "Lusail": 5.419, "Abu Dhabi": 5.281
}

# --- FUNÇÕES DE API ---
@st.cache_data(show_spinner=False)
def get_data(endpoint, params=None):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        res = requests.get(url, params=params, timeout=15)
        return pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    except:
        return pd.DataFrame()

# --- SIDEBAR: FILTROS ---
st.sidebar.title("🛠️ Settings")
year = st.sidebar.selectbox(t["select_year"], [2026, 2025, 2024, 2023])

with st.spinner(t["loading"]):
    df_sessions = get_data("sessions", {"year": year, "session_name": "Race"})

if not df_sessions.empty:
    df_sessions['display'] = df_sessions['country_name'] + " - " + df_sessions['location']
    session_map = df_sessions.set_index('session_key')['display'].to_dict()
    sk = st.sidebar.selectbox(t["select_gp"], options=list(session_map.keys()), format_func=lambda x: session_map[x])
    
    session_info = df_sessions[df_sessions['session_key'] == sk].iloc[0]
    
    with st.spinner(t["loading"]):
        df_drivers = get_data("drivers", {"session_key": sk})
        df_laps = get_data("laps", {"session_key": sk})

    if not df_drivers.empty:
        driver_map = dict(zip(df_drivers['broadcast_name'], df_drivers['driver_number']))
        selected_driver_names = sorted(list(driver_map.keys()))
        
        sel_drivers = st.sidebar.multiselect(
            t["select_drivers"], 
            options=selected_driver_names, 
            default=selected_driver_names[:2] if len(selected_driver_names) >= 2 else selected_driver_names
        )

        if sel_drivers:
            sel_nums = [driver_map[d] for d in sel_drivers]
            
            # --- UI PRINCIPAL ---
            st.title(t["title"])
            st.markdown(t["subtitle"])
            
            tab0, tab1, tab2, tab3 = st.tabs([t["tab0"], t["tab1"], t["tab2"], t["tab3"]])

            # --- ABA 0: INFO DA PROVA ---
            with tab0:
                col_stats, col_map = st.columns([1, 1])
                
                winner_name = t["no_data"]
                fastest_lap_time = t["no_data"]
                fastest_lap_driver = ""
                
                if not df_laps.empty:
                    # Forçar tipagem correta para garantir operações
                    df_laps['lap_number'] = pd.to_numeric(df_laps['lap_number'], errors='coerce')
                    df_laps['lap_duration'] = pd.to_numeric(df_laps['lap_duration'], errors='coerce')
                    
                    # CORREÇÃO: A coluna correta de timestamp na OpenF1 API é 'date'
                    max_lap = df_laps['lap_number'].max()
                    last_laps = df_laps[df_laps['lap_number'] == max_lap]
                    
                    if not last_laps.empty and 'date' in last_laps.columns:
                        last_laps = last_laps.sort_values(by='date')
                        winner_num = last_laps.iloc[0]['driver_number']
                        winner_name = df_drivers[df_drivers['driver_number'] == winner_num]['broadcast_name'].iloc[0]
                    elif not last_laps.empty:
                        # Fallback seguro caso 'date' falte em sessões específicas
                        winner_num = last_laps.iloc[0]['driver_number']
                        winner_name = df_drivers[df_drivers['driver_number'] == winner_num]['broadcast_name'].iloc[0]
                    
                    # Encontrar Volta mais Rápida de forma segura
                    df_valid_laps = df_laps.dropna(subset=['lap_duration']).sort_values(by='lap_duration')
                    if not df_valid_laps.empty:
                        fastest_lap_row = df_valid_laps.iloc[0]
                        fastest_lap_time = f"{round(fastest_lap_row['lap_duration'], 3)}s"
                        fastest_lap_driver = df_drivers[df_drivers['driver_number'] == fastest_lap_row['driver_number']]['broadcast_name'].iloc[0]

                with col_stats:
                    st.metric(t["race_winner"], winner_name)
                    st.metric(t["fastest_lap"], f"{fastest_lap_time} ({fastest_lap_driver})" if fastest_lap_driver else fastest_lap_time)
                    st.metric(t["circuit_name"], session_info['circuit_short_name'])
                    st.metric(t["location"], f"{session_info['location']}, {session_info['country_name']}")
                    
                    loc = session_info['location']
                    length = track_meta.get(loc, 5.0)
                    laps_count = df_laps['lap_number'].max() if not df_laps.empty else 0
                    st.metric(t["track_length"], f"{length} km")
                    st.metric(t["total_km"], f"{round(length * laps_count, 2)} km")
                
                with col_map:
                    circuit_raw_name = session_info['circuit_short_name'].replace(" ", "_")
                    map_url = f"https://www.formula1.com/content/dam/fom-website/manual/Misc/2024-Master-Circuit-Maps/{circuit_raw_name}.png"
                    try:
                        st.image(map_url, caption=f"Circuit Layout: {session_info['circuit_short_name']}", use_container_width=True)
                    except:
                        st.info("Layout map preview currently unavailable for this circuit.")

            # --- ABA 1: RITMO & PNEUS ---
            with tab1:
                if not df_laps.empty:
                    df_pace = df_laps[df_laps['driver_number'].isin(sel_nums)].copy()
                    df_pace = df_pace[df_pace['is_pit_out_lap'] == False].dropna(subset=['lap_duration', 'lap_number'])
                    df_pace = df_pace.merge(df_drivers[['driver_number', 'broadcast_name']], on='driver_number', how='left')
                    
                    if not df_pace.empty:
                        fig_pace = px.line(
                            df_pace.sort_values(by='lap_number'), 
                            x="lap_number", 
                            y="lap_duration", 
                            color="broadcast_name", 
                            title="Race Pace Evolution",
                            labels={"lap_number": "Lap / Volta", "lap_duration": "Time / Tempo (s)", "broadcast_name": "Driver / Piloto"},
                            template="plotly_dark"
                        )
                        fig_pace.update_yaxes(autorange="reversed")
                        st.plotly_chart(fig_pace, use_container_width=True)
                    else:
                        st.info(t["no_data"])
                else:
                    st.info(t["no_data"])

            # --- ABA 2: ESTRATÉGIA DE BOX (Stints) ---
            with tab2:
                st.subheader(t["stint_title"])
                with st.spinner(t["loading"]):
                    df_stints = get_data("stints", {"session_key": sk})
                
                if not df_stints.empty:
                    df_stints_sel = df_stints[df_stints['driver_number'].isin(sel_nums)].copy()
                    df_stints_sel = df_stints_sel.merge(df_drivers[['driver_number', 'broadcast_name']], on='driver_number', how='left')
                    
                    if not df_stints_sel.empty:
                        df_stints_sel['lap_start'] = pd.to_numeric(df_stints_sel['lap_start'], errors='coerce')
                        df_stints_sel['lap_end'] = pd.to_numeric(df_stints_sel['lap_end'], errors='coerce')
                        df_stints_sel['stint_length'] = df_stints_sel['lap_end'] - df_stints_sel['lap_start'] + 1
                        
                        compound_colors = {"SOFT": "red", "MEDIUM": "yellow", "HARD": "white", "INTERMEDIATE": "green", "WET": "blue"}
                        
                        fig_stint = px.bar(
                            df_stints_sel.dropna(subset=['stint_length']), 
                            x="stint_number", 
                            y="stint_length", 
                            color="compound",
                            barmode="group", 
                            facet_col="broadcast_name",
                            color_discrete_map=compound_colors, 
                            labels={"stint_number": "Stint", "stint_length": "Laps Driven / Voltas Completadas", "compound": "Compound / Pneu"},
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_stint, use_container_width=True)
                    else:
                        st.info(t["no_data"])
                else:
                    st.info(t["no_data"])

            # --- ABA 3: TELEMETRIA REAL ---
            with tab3:
                st.subheader(t["speed_analysis"])
                
                if len(sel_nums) >= 1:
                    cols = st.columns(len(sel_nums))
                    for i, num in enumerate(sel_nums):
                        with cols[i]:
                            name = [k for k, v in driver_map.items() if v == num][0]
                            with st.spinner(f"{t['loading']} ({name})"):
                                df_car = get_data("car_data", {"session_key": sk, "driver_number": num})
                            
                            if not df_car.empty:
                                df_car['speed'] = pd.to_numeric(df_car['speed'], errors='coerce')
                                max_speed = df_car['speed'].max()
                                
                                st.metric(f"{name} - Top Speed", f"{max_speed} km/h")
                                
                                fig_speed = px.area(
                                    df_car.iloc[::40].dropna(subset=['speed']), 
                                    y="speed", 
                                    title=f"Speed Trace: {name}", 
                                    template="plotly_dark", 
                                    color_discrete_sequence=['#deff9a']
                                )
                                st.plotly_chart(fig_speed, use_container_width=True)
                            else:
                                st.info(f"{name}: {t['no_data']}")
                else:
                    st.info(t["no_data"])
        else:
            st.info("Selecione os pilotos na barra lateral / Select drivers in the sidebar.")
    else:
        st.error(t["error_api"])
else:
    st.error(t["error_api"])