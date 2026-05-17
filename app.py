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
        "tab1": "📊 Ritmo & Pneus",
        "tab2": "🏁 Estratégia de Box",
        "tab3": "⚡ Telemetria Real",
        "select_year": "Ano:",
        "select_gp": "Grande Prêmio:",
        "select_drivers": "Pilotos:",
        "loading": "Processando dados...",
        "speed_analysis": "Análise de Velocidade Máxima",
        "stint_title": "Histórico de Pneus (Stints)",
        "no_data": "Dados não disponíveis para esta seleção.",
        "error_api": "Conexão com a OpenF1 API falhou ou a sessão não possui dados limpos."
    },
    "English": {
        "title": "🏎️ SchimiAI 2.0: Strategy & Telemetry Hub",
        "subtitle": "Advanced analytics inspired by Hannah Schmitz's strategy engineering.",
        "tab1": "📊 Pace & Tyres",
        "tab2": "🏁 Pit Strategy",
        "tab3": "⚡ Real Telemetry",
        "select_year": "Year:",
        "select_gp": "Grand Prix:",
        "select_drivers": "Drivers:",
        "loading": "Processing data...",
        "speed_analysis": "Top Speed Analysis",
        "stint_title": "Tyre History (Stints)",
        "no_data": "Data not available for this selection.",
        "error_api": "Connection to OpenF1 API failed or the session has no clean data."
    }
}
t = texts[language]

# --- FUNÇÕES DE API ---
@st.cache_data(show_spinner=False)
def get_data(endpoint, params=None):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        res = requests.get(url, params=params, timeout=15)
        return pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()
    except:
        return pd.DataFrame()

# --- SIDEBAR: SELEÇÃO DE SESSÃO ---
st.sidebar.title("🛠️ Settings")

# Modificado para incluir 2025 e 2026 na lista de seleção
year = st.sidebar.selectbox(t["select_year"], [2026, 2025, 2024, 2023])

with st.spinner(t["loading"]):
    df_sessions = get_data("sessions", {"year": year, "session_name": "Race"})

if not df_sessions.empty:
    df_sessions['display'] = df_sessions['country_name'] + " - " + df_sessions['location']
    session_map = df_sessions.set_index('session_key')['display'].to_dict()
    sk = st.sidebar.selectbox(t["select_gp"], options=list(session_map.keys()), format_func=lambda x: session_map[x])
    
    with st.spinner(t["loading"]):
        df_drivers = get_data("drivers", {"session_key": sk})
    
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
            
            tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

            # --- ABA 1: RITMO & PNEUS ---
            with tab1:
                with st.spinner(t["loading"]):
                    df_laps = get_data("laps", {"session_key": sk})
                
                if not df_laps.empty:
                    df_pace = df_laps[df_laps['driver_number'].isin(sel_nums)].copy()
                    
                    df_pace['lap_number'] = pd.to_numeric(df_pace['lap_number'], errors='coerce')
                    df_pace['lap_duration'] = pd.to_numeric(df_pace['lap_duration'], errors='coerce')
                    
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
                        compound_colors = {"SOFT": "red", "MEDIUM": "yellow", "HARD": "white", "INTERMEDIATE": "green", "WET": "blue"}
                        
                        fig_stint = px.bar(
                            df_stints_sel, 
                            x="stint_number", 
                            y="tyre_age_at_start", 
                            color="compound",
                            barmode="group", 
                            facet_col="broadcast_name",
                            color_discrete_map=compound_colors, 
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