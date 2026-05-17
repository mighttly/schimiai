import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SchimiAI 2.0 - F1 Strategy Hub", layout="wide", page_icon="🏎️")

# --- CUSTOM CSS (EMBELEZAMENTO NEON & GLASSMORPHISM) ---
st.markdown("""
<style>
    /* Configuração de Fundo Geral */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Título Principal com Glow */
    .main-title {
        font-family: 'Urbanist', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
        text-shadow: 0 0 20px rgba(222, 255, 154, 0.2);
    }
    .main-title span {
        color: #deff9a;
        text-shadow: 0 0 15px rgba(222, 255, 154, 0.6);
    }
    
    /* Estilização Premium dos Cards de Métrica (Streamlit) */
    div[data-testid="stMetric"] {
        background-color: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(222, 255, 154, 0.15) !important;
        border-radius: 16px !important;
        padding: 22px 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Efeito de Hover nos Cards (Glow Neon) */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(222, 255, 154, 0.6) !important;
        box-shadow: 0 12px 40px 0 rgba(222, 255, 154, 0.15) !important;
    }
    
    /* Customização dos textos internos das métricas */
    div[data-testid="stMetricValue"] > div {
        font-family: 'Urbanist', sans-serif !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #deff9a !important;
    }
    div[data-testid="stMetricLabel"] > div > p {
        font-family: 'Urbanist', sans-serif !important;
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-weight: 600 !important;
    }
    
    /* Estilização F1 das Abas (Tabs) */
    button[data-baseweb="tab"] {
        font-family: 'Urbanist', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        background-color: transparent !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #f8fafc !important;
    }
    button[aria-selected="true"] {
        color: #deff9a !important;
        border-bottom: 3px solid #deff9a !important;
    }
    div[data-testid="stTabs"] {
        border-bottom: 1px solid rgba(222, 255, 154, 0.1) !important;
        margin-bottom: 25px !important;
    }
    
    /* Barra Lateral Escura e Elegante */
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(222, 255, 154, 0.1) !important;
    }
    
    /* Esconder bordas desnecessárias de containers */
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- DICIONÁRIO DE TRADUÇÃO ---
st.sidebar.header("🌐 Language / Idioma")
language = st.sidebar.selectbox("Choose Language:", ["Português", "English"])

texts = {
    "Português": {
        "title": "SchimiAI 2.0",
        "subtitle": "Análise avançada de dados inspirada na engenharia de estratégia de Hannah Schmitz.",
        "tab0": "🏠 Info da Prova",
        "tab1": "📊 Ritmo & Pneus",
        "tab2": "🏁 Estratégia de Box",
        "tab3": "⚡ Telemetria Real",
        "select_year": "Ano:",
        "select_gp": "Grande Prêmio:",
        "select_drivers": "Pilotos:",
        "loading": "Sincronizando dados de telemetria...",
        "race_winner": "Vencedor da Prova",
        "fastest_lap": "Volta mais Rápida",
        "circuit_name": "Circuito",
        "location": "Localização",
        "track_length": "Extensão do Circuito",
        "total_km": "Distância Total Percorrida",
        "stint_title": "Histórico de Pneus (Stints)",
        "speed_analysis": "Análise de Velocidade Máxima",
        "no_data": "Dados não disponíveis.",
        "circuit_layout_title": "Traçado Dinâmico (Via Telemetria GPS)",
        "error_api": "Conexão com a OpenF1 API falhou ou a sessão não possui dados limpos."
    },
    "English": {
        "title": "SchimiAI 2.0",
        "subtitle": "Advanced analytics inspired by Hannah Schmitz's strategy engineering.",
        "tab0": "🏠 Race Info",
        "tab1": "📊 Pace & Tyres",
        "tab2": "🏁 Pit Strategy",
        "tab3": "⚡ Real Telemetry",
        "select_year": "Year:",
        "select_gp": "Grand Prix:",
        "select_drivers": "Drivers:",
        "loading": "Syncing live telemetry streams...",
        "race_winner": "Race Winner",
        "fastest_lap": "Fastest Lap",
        "circuit_name": "Circuit",
        "location": "Location",
        "track_length": "Track Length",
        "total_km": "Total Distance Covered",
        "stint_title": "Tyre History (Stints)",
        "speed_analysis": "Top Speed Analysis",
        "no_data": "Data not available.",
        "circuit_layout_title": "Dynamic Circuit Layout (Via GPS Telemetry)",
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
            st.markdown(f'<h1 class="main-title">🏎️ {t["title"]}: <span>Telemetry Hub</span></h1>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px;">{t["subtitle"]}</p>', unsafe_allow_html=True)
            
            # Criação de abas
            tab0, tab1, tab2, tab3 = st.tabs([t["tab0"], t["tab1"], t["tab2"], t["tab3"]])

            # --- ABA 0: INFO DA PROVA ---
            with tab0:
                col_stats, col_map = st.columns([1, 1.2], gap="large")
                
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
                length = track_meta.get(loc, 5.0)
                laps_count = max_lap if pd.notna(max_lap) else 0

                with col_stats:
                    st.metric(t["race_winner"], winner_name)
                    st.metric(t["fastest_lap"], fastest_lap_str)
                    st.metric(t["circuit_name"], session_info['circuit_short_name'])
                    st.metric(t["location"], f"{session_info['location']}, {session_info['country_name']}")
                    st.metric(t["track_length"], f"{length} km")
                    st.metric(t["total_km"], f"{round(length * laps_count, 2)} km")
                
                with col_map:
                    st.markdown(f'<h3 style="font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-bottom: 15px;">🏁 {t["circuit_layout_title"]}</h3>', unsafe_allow_html=True)
                    try:
                        with st.spinner(t["loading"]):
                            df_loc = get_data("location", {"session_key": sk, "driver_number": sel_nums[0]})
                        
                        if not df_loc.empty and 'x' in df_loc.columns and 'y' in df_loc.columns:
                            df_loc['x'] = pd.to_numeric(df_loc['x'], errors='coerce')
                            df_loc['y'] = pd.to_numeric(df_loc['y'], errors='coerce')
                            df_track = df_loc.iloc[::25].dropna(subset=['x', 'y'])
                            
                            if len(df_track) > 1:
                                fig_map = px.line(
                                    df_track, x="x", y="y",
                                    template="plotly_dark",
                                    color_discrete_sequence=['#deff9a']
                                )
                                fig_map.update_traces(line=dict(width=5, color='#deff9a'))
                                fig_map.update_layout(
                                    xaxis=dict(visible=False, showgrid=False, zeroline=False),
                                    yaxis=dict(visible=False, showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1),
                                    margin=dict(l=10, r=10, t=10, b=10),
                                    height=420,
                                    showlegend=False,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)'
                                )
                                st.plotly_chart(fig_map, use_container_width=True)
                            else:
                                st.info("GPS track layout data preview currently unavailable.")
                        else:
                            st.info("GPS track layout data preview currently unavailable.")
                    except Exception as e:
                        st.info("GPS track layout data preview currently unavailable.")

            # --- ABA 1: RITMO & PNEUS ---
            with tab1:
                try:
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
                            title="Race Pace Consistency (Lower is Better)",
                            labels={"lap_number": "Lap / Volta", "lap_duration": "Seconds / Segundos", "full_name": "Driver / Piloto"},
                            hover_data={"lap_duration": ":.3f", "lap_time_formatted": True},
                            template="plotly_dark",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        fig_pace.update_yaxes(autorange="reversed", gridcolor="rgba(255,255,255,0.05)")
                        fig_pace.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                        fig_pace.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(30,41,59,0.2)',
                            margin=dict(t=50, b=20, l=10, r=10)
                        )
                        st.plotly_chart(fig_pace, use_container_width=True)
                    else:
                        st.info(t["no_data"])
                except Exception as e:
                    st.info(t["no_data"])

            # --- ABA 2: ESTRATÉGIA DE BOX (Stints) ---
            with tab2:
                st.subheader(t["stint_title"])
                try:
                    with st.spinner(t["loading"]):
                        df_stints = get_data("stints", {"session_key": sk})
                    
                    if not df_stints.empty:
                        df_stints_sel = df_stints[df_stints['driver_number'].isin(sel_nums)].copy()
                        df_stints_sel = df_stints_sel.merge(df_drivers[['driver_number', 'full_name']], on='driver_number', how='left')
                        
                        if not df_stints_sel.empty:
                            df_stints_sel['lap_start'] = pd.to_numeric(df_stints_sel['lap_start'], errors='coerce')
                            df_stints_sel['lap_end'] = pd.to_numeric(df_stints_sel['lap_end'], errors='coerce')
                            df_stints_sel['stint_length'] = df_stints_sel['lap_end'] - df_stints_sel['lap_start'] + 1
                            
                            compound_colors = {"SOFT": "#EF4444", "MEDIUM": "#FBBF24", "HARD": "#F8FAFC", "INTERMEDIATE": "#10B981", "WET": "#3B82F6"}
                            
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
                            fig_stint.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(30,41,59,0.2)',
                                margin=dict(t=50, b=20, l=10, r=10)
                            )
                            fig_stint.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
                            st.plotly_chart(fig_stint, use_container_width=True)
                        else:
                            st.info(t["no_data"])
                    else:
                        st.info(t["no_data"])
                except Exception as e:
                    st.info(t["no_data"])

            # --- ABA 3: TELEMETRIA REAL ---
            with tab3:
                st.subheader(t["speed_analysis"])
                try:
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
                                    fig_speed.update_layout(
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(30,41,59,0.2)',
                                        margin=dict(t=50, b=20, l=10, r=10)
                                    )
                                    fig_speed.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
                                    fig_speed.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                                    st.plotly_chart(fig_speed, use_container_width=True)
                                else:
                                    st.info(f"{name}: {t['no_data']}")
                    else:
                        st.info(t["no_data"])
                except Exception as e:
                    st.info(t["no_data"])
        else:
            st.info("Selecione os pilotos na barra lateral / Select drivers in the sidebar.")
    else:
        st.error(t["error_api"])
else:
    st.error(t["error_api"])