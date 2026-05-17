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

# --- METADADOS DAS PISTAS (Distâncias Oficiais e IDs de Imagem da F1) ---
track_meta = {
    "Bahrain": {"length": 5.412, "img_id": "Bahrain"},
    "Jeddah": {"length": 6.174, "img_id": "Saudi_Arabia"},
    "Melbourne": {"length": 5.278, "img_id": "Australia"},
    "Suzuka": {"length": 5.807, "img_id": "Japan"},
    "Shanghai": {"length": 5.451, "img_id": "China"},
    "Miami": {"length": 5.412, "img_id": "Miami"},
    "Imola": {"length": 4.909, "img_id": "Emilia_Romagna"},
    "Monaco": {"length": 3.337, "img_id": "Monaco"},
    "Montreal": {"length": 4.361, "img_id": "Canada"},
    "Barcelona": {"length": 4.657, "img_id": "Spain"},
    "Spielberg": {"length": 4.318, "img_id": "Austria"},
    "Silverstone": {"length": 5.891, "img_id": "Great_Britain"},
    "Budapest": {"length": 4.381, "img_id": "Hungary"},
    "Spa": {"length": 7.004, "img_id": "Belgium"},
    "Zandvoort": {"length": 4.259, "img_id": "Netherlands"},
    "Monza": {"length": 5.793, "img_id": "Italy"},
    "Baku": {"length": 6.003, "img_id": "Azerbaijan"},
    "Singapore": {"length": 4.940, "img_id": "Singapore"},
    "Austin": {"length": 5.513, "img_id": "USA"},
    "Mexico City": {"length": 4.304, "img_id": "Mexico"},
    "Sao Paulo": {"length": 4.309, "img_id": "Brazil"},
    "Las Vegas": {"length": 6.201, "img_id": "Las_Vegas"},
    "Lusail": {"length": 5.419, "img_id": "Qatar"},
    "Abu Dhabi": {"length": 5.281, "img_id": "Abu_Dhabi"}
}

# --- FUNÇÃO AUXILIAR DE FORMATAÇÃO DE TEMPO ---
def format_lap_time(seconds):
    if pd.isna(seconds) or seconds <= 0:
        return "-"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes:02d}:{rem_seconds:06.3f}"[:-1]

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

    if not df_drivers.empty and not df_laps.empty:
        df_drivers['full_name'] = df_drivers['full_name'].fillna(df_drivers['broadcast_name'])
        driver_map = dict(zip(df_drivers['full_name'], df_drivers['driver_number']))
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
                
                df_laps['lap_number'] = pd.to_numeric(df_laps['lap_number'], errors='coerce')
                df_laps['lap_duration'] = pd.to_numeric(df_laps['lap_duration'], errors='coerce')
                
                max_lap = df_laps['lap_number'].max()
                last_laps = df_laps[df_laps['lap_number'] == max_lap]
                
                if not last_laps.empty:
                    if 'date' in last_laps.columns:
                        last_laps = last_laps.sort_values(by='date')
                    winner_num = last_laps.iloc[0]['driver_number']
                    winner_name = df_drivers[df_drivers['driver_number'] == winner_num]['full_name'].iloc[0]
                
                df_valid_laps = df_laps.dropna(subset=['lap_duration']).sort_values(by='lap_duration')
                if not df_valid_laps.empty:
                    fastest_lap_row = df_valid_laps.iloc[0]
                    fastest_lap_time = format_lap_time(fastest_lap_row['lap_duration'])
                    fastest_lap_driver = df_drivers[df_drivers['driver_number'] == fastest_lap_row['driver_number']]['full_name'].iloc[0]
                    fastest_lap_str = f"{fastest_lap_time} ({fastest_lap_driver})"
                else:
                    fastest_lap_str = t["no_data"]

                loc = session_info['location']
                metadata = track_meta.get(loc, {"length": 5.0, "img_id": "Unknown"})
                length = metadata["length"]
                laps_count = max_lap if pd.notna(max_lap) else 0

                with col_stats:
                    st.metric(t["race_winner"], winner_name)
                    st.metric(t["fastest_lap"], fastest_lap_str)
                    st.metric(t["circuit_name"], session_info['circuit_short_name'])
                    st.metric(t["location"], f"{session_info['location']}, {session_info['country_name']}")
                    st.metric(t["track_length"], f"{length} km")
                    st.metric(t["total_km"], f"{round(length * laps_count, 2)} km")
                
                with col_map:
                    # MODIFICAÇÃO: Utilização do mapeamento robusto de IDs de imagem da F1 CDN
                    img_id = metadata["img_id"]
                    map_url = f"https://media.formula1.com/image/upload/f_auto,q_auto/content/dam/fom-website/2018-redesign-assets/circuit-maps/16x9/{img_id}.png"
                    
                    if img_id != "Unknown":
                        st.image(map_url, caption=f"Circuit Layout: {session_info['circuit_short_name']}", use_container_width=True)
                    else:
                        st.info("Layout map preview currently unavailable for this circuit.")

            # --- ABA 1: RITMO & PNEUS ---
            with tab1:
                df_pace = df_laps[df_laps['driver_number'].isin(sel_nums)].copy()
                df_pace = df_pace[df_pace['is_pit_out_lap'] == False].dropna(subset=['lap_duration', 'lap_number'])
                df_pace = df_pace.merge(df_drivers[['driver_number', 'full_name']], on='driver_number', how='left')
                
                if not df_pace.empty:
                    df_pace['lap_time_formatted'] = df_pace['lap_duration'].apply(format_lap_time)
                    
                    fig_pace = px.line(
                        df_pace.sort_values(by='lap_number'), 
                        x="lap_number", 
                        y="lap_duration", 
                        color="full_name", 
                        title="Race Pace Evolution",
                        labels={"lap_number": "Lap / Volta", "lap_duration": "Seconds / Segundos", "full_name": "Driver / Piloto"},
                        hover_data={"lap_duration": ":.3f", "lap_time_formatted": True},
                        template="plotly_dark"
                    )
                    fig_pace.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig_pace, use_container_width=True)
                else:
                    st.info(t["no_data"])

            # --- ABA 2: ESTRATÉGIA DE BOX (Stints) ---
            with tab2:
                st.subheader(t["stint_title"])
                with st.spinner(t["loading"]):
                    df_stints = get_data("stints", {"session_key": sk})
                
                if not df_stints.empty:
                    df_stints_sel = df_stints[df_stints['driver_number'].isin(sel_nums)].copy()
                    df_stints_sel = df_stints_sel.merge(df_drivers[['driver_number', 'full_name']], on='driver_number', how='left')
                    
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
                            facet_col="full_name",
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

