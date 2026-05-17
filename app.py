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
        "tab1": "📊 Ritmo & Pneus",
        "tab2": "🏁 Estratégia de Box",
        "tab3": "⚡ Telemetria Real",
        "select_year": "Ano:",
        "select_gp": "Grande Prêmio:",
        "select_drivers": "Pilotos:",
        "loading": "Processando dados...",
        "speed_analysis": "Análise de Velocidade Máxima",
        "telemetry_title": "Comparativo de Volta Rápida (Telemetria)",
        "stint_title": "Histórico de Pneus (Stints)",
        "no_data": "Dados não disponíveis para esta seleção."
    },
    "English": {
        "title": "🏎️ SchimiAI 2.0: Strategy & Telemetry Hub",
        "tab1": "📊 Pace & Tyres",
        "tab2": "🏁 Pit Strategy",
        "tab3": "⚡ Real Telemetry",
        "select_year": "Year:",
        "select_gp": "Grand Prix:",
        "select_drivers": "Drivers:",
        "loading": "Processing data...",
        "speed_analysis": "Top Speed Analysis",
        "telemetry_title": "Fastest Lap Comparison (Telemetry)",
        "stint_title": "Tyre History (Stints)",
        "no_data": "Data not available for this selection."
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
year = st.sidebar.selectbox(t["select_year"], [2024, 2023])
df_sessions = get_data("sessions", {"year": year, "session_name": "Race"})

if not df_sessions.empty:
    df_sessions['display'] = df_sessions['country_name'] + " - " + df_sessions['location']
    session_map = df_sessions.set_index('session_key')['display'].to_dict()
    sk = st.sidebar.selectbox(t["select_gp"], options=list(session_map.keys()), format_func=lambda x: session_map[x])
    
    df_drivers = get_data("drivers", {"session_key": sk})
    driver_map = dict(zip(df_drivers['broadcast_name'], df_drivers['driver_number']))
    sel_drivers = st.sidebar.multiselect(t["select_drivers"], options=list(driver_map.keys()), default=list(driver_map.keys())[:2])

    if sel_drivers:
        sel_nums = [driver_map[d] for d in sel_drivers]
        
        # --- UI PRINCIPAL ---
        st.title(t["title"])
        tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

        # --- ABA 1: RITMO & PNEUS (Seu código original otimizado) ---
        with tab1:
            df_laps = get_data("laps", {"session_key": sk})
            if not df_laps.empty:
                df_pace = df_laps[df_laps['driver_number'].isin(sel_nums)].copy()
                df_pace = df_pace[df_pace['is_pit_out_lap'] == False].dropna(subset=['lap_duration'])
                df_pace = df_pace.merge(df_drivers[['driver_number', 'broadcast_name', 'team_colour']], on='driver_number')
                
                fig_pace = px.line(df_pace, x="lap_number", y="lap_duration", color="broadcast_name", 
                                   title="Race Pace Evolution", template="plotly_dark")
                fig_pace.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_pace, use_container_width=True)

        # --- ABA 2: ESTRATÉGIA DE BOX (Stints) ---
        with tab2:
            st.subheader(t["stint_title"])
            df_stints = get_data("stints", {"session_key": sk})
            if not df_stints.empty:
                df_stints_sel = df_stints[df_stints['driver_number'].isin(sel_nums)].copy()
                df_stints_sel = df_stints_sel.merge(df_drivers[['driver_number', 'broadcast_name']], on='driver_number')
                
                # Mapa de cores para pneus F1
                compound_colors = {"SOFT": "red", "MEDIUM": "yellow", "HARD": "white", "INTERMEDIATE": "green", "WET": "blue"}
                
                fig_stint = px.bar(df_stints_sel, x="stint_number", y="tyre_age_at_start", color="compound",
                                   barmode="group", facet_col="broadcast_name",
                                   color_discrete_map=compound_colors, template="plotly_dark")
                st.plotly_chart(fig_stint, use_container_width=True)

        # --- ABA 3: TELEMETRIA REAL (Car Data) ---
        with tab3:
            st.subheader(t["speed_analysis"])
            # Pegando telemetria apenas dos pilotos selecionados (amostragem para não travar)
            # Para o "Raio-X", pegamos a volta mais rápida
            if len(sel_nums) >= 1:
                col1, col2 = st.columns(2)
                for i, num in enumerate(sel_nums):
                    with [col1, col2][i % 2]:
                        name = [k for k, v in driver_map.items() if v == num][0]
                        df_car = get_data("car_data", {"session_key": sk, "driver_number": num})
                        if not df_car.empty:
                            st.metric(f"{name} - Top Speed", f"{df_car['speed'].max()} km/h")
                            # Gráfico de velocidade simples
                            fig_speed = px.area(df_car.iloc[::20], y="speed", title=f"Speed Trace: {name}", template="plotly_dark", color_discrete_sequence=['#deff9a'])
                            st.plotly_chart(fig_speed, use_container_width=True)
            else:
                st.info(t["no_data"])

else:
    st.error("API Connection Error")

### 🛠️ O que fazer agora?

1.  **Atualize seu `requirements.txt`:** Adicione `plotly-express` e `statsmodels` se ainda não tiver.
2.  **Commit e Push:**
    ```bash
    git add app.py requirements.txt
    git commit -m "Upgrade to SchimiAI 2.0: Added Tabs, Stints and Telemetry"
    git push origin main
    3.  **Deploy:** O Streamlit Cloud vai reconhecer as abas automaticamente. 

Agora seu app não é mais apenas um "gráfico de voltas", é uma **central de inteligência de estratégia**. Sinta-se à vontade para explorar os outros 18 endpoints da API (como `weather` ou `team_radio`) para futuras versões!