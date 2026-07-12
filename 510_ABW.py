import random
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Intelligent Workshop Assistant", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #111418 0%, #0b0d10 100%);
        color: #e7ebef;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    .stSidebar {
        background: #15191f;
        border-right: 1px solid #2b3138;
    }
    div[data-testid="stMetric"] {
        background: #171b21;
        border: 1px solid #2f353d;
        padding: 1rem;
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    }
    .industrial-card {
        background: linear-gradient(180deg, #171b21 0%, #111418 100%);
        border: 1px solid #2f353d;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.22);
    }
    .gauge-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.35rem;
        margin: 0.25rem 0 0.5rem;
    }
    .gauge-shell {
        position: relative;
        width: 280px;
        height: 155px;
        overflow: hidden;
    }
    .gauge-shell::before {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        left: 0;
        top: 0;
        border-radius: 50%;
        background: conic-gradient(from 180deg, #2b3138 0deg, #ffe35a 74deg, #a7ff2f 136deg, #2b3138 180deg);
        box-shadow: inset 0 0 18px rgba(0, 0, 0, 0.35);
    }
    .gauge-shell::after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        left: 45px;
        top: 45px;
        border-radius: 50%;
        background: #111418;
        border: 1px solid #2f353d;
    }
    .gauge-needle {
        position: absolute;
        left: 50%;
        bottom: 24px;
        width: 4px;
        height: 92px;
        background: linear-gradient(180deg, #ffe35a 0%, #a7ff2f 100%);
        border-radius: 999px;
        transform-origin: bottom center;
        box-shadow: 0 0 10px rgba(167, 255, 47, 0.55);
    }
    .gauge-center {
        position: absolute;
        left: 50%;
        top: 88px;
        transform: translateX(-50%);
        z-index: 2;
        text-align: center;
    }
    .gauge-value {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        color: #dfffa4;
    }
    .gauge-subtitle {
        font-size: 0.78rem;
        color: #b9c2ca;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 0.25rem;
    }
    .history-list {
        color: #dfe4e8;
        margin-top: 0.25rem;
        padding-left: 1.15rem;
    }
    .history-list li {
        margin-bottom: 0.25rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    csv_path = Path(__file__).with_name("machine.csv")
    return pd.read_csv(csv_path)


def render_temperature_gauge(value: int, min_value: int = 0, max_value: int = 100):
    bounded_value = max(min_value, min(value, max_value))
    ratio = (bounded_value - min_value) / (max_value - min_value)
    angle = -90 + (ratio * 180)

    st.markdown(
        f"""
        <div class="industrial-card">
            <div class="gauge-wrap">
                <div class="gauge-shell">
                    <div class="gauge-needle" style="transform: translateX(-50%) rotate({angle}deg);"></div>
                    <div class="gauge-center">
                        <div class="gauge-value">{bounded_value}°C</div>
                        <div class="gauge-subtitle">Live Temperature Gauge</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


df = load_data()

st.sidebar.title("🛠 Workshop Access")
m_id = st.sidebar.text_input("Enter Machine ID")

st.title("🤖 Intelligent Workshop Assistant")

if m_id:
    machine_info = df[df["id"].astype(str) == m_id]

    if not machine_info.empty:
        data = machine_info.iloc[0]
        st.header(f"Machine: {data['name']}")

        live_temp = int(data["temp"]) + random.randint(-2, 2)

        col1, col2 = st.columns(2)
        col1.metric("Live Temperature", f"{live_temp}°C")
        col2.metric("Status", data["status"])

        render_temperature_gauge(live_temp)

        st.write(f"**Last Maintenance:** {data['last_maintenance']}")
        st.info(f"**Required Tools:** {data['tools']}")

        history_values = [item.strip() for item in str(data.get("History", "")).split(",") if item.strip()]
        if history_values:
            st.markdown("**Maintenance History:**")
            st.markdown("<ul class='history-list'>" + "".join(f"<li>{item}</li>" for item in history_values) + "</ul>", unsafe_allow_html=True)

        st.divider()
        st.subheader("🤖 AI Technical Assistant")

        user_query = st.text_input("Ask something about the machine (e.g., 'How to fix pressure leak?')")

        if user_query:
            if "pressure" in user_query.lower() or "leak" in user_query.lower():
                st.write("AI Assistant: For the hydraulic press, check the 'Pressure Gauge' and tighten the 'Seal'.")
            elif "start" in user_query.lower():
                st.write("AI Assistant: To start the machine, first turn ON the Main Power Switch.")
            else:
                st.write("AI Assistant: Let me check the manual for this and get back to you...")
    else:
        st.error("Machine ID not found!")
else:
    st.info("👈 Please enter a Machine ID in the sidebar to load the dashboard.")