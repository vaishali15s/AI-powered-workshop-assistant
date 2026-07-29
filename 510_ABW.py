from pathlib import Path
import requests
import time

# Database Endpoint Settings
FIREBASE_URL = "https://ai-powered-workshop-assistant-default-rtdb.asia-southeast1.firebasedatabase.app/sensor_data.json"
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Workshop Defect Dashboard", layout="wide")

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
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.55);
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
        color: #000000;
    }
    .gauge-subtitle {
        font-size: 0.78rem;
        color: #9aa4b2;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 0.25rem;
    }
    .history-list {
        color: #dfe4e8;
        margin-top: 0.25rem;
        padding-left: 1.15rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #e7ebef;
    }
    .stButton > button {
        background: #171b21;
        color: #e7ebef;
        border: 1px solid #2f353d;
        font-weight: 700;
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
    csv_path = Path(__file__).with_name("workshop.csv")
    data = pd.read_csv(csv_path)
    data.columns = [column.strip() for column in data.columns]
    return data


def render_summary_card(title: str, value: str, subtitle: str):
    st.markdown(
        f"""
        <div class="industrial-card">
            <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: #b9c2ca;">{title}</div>
            <div style="font-size: 2rem; font-weight: 800; margin-top: 0.35rem; color: #dfffa4;">{value}</div>
            <div style="font-size: 0.9rem; color: #c7ced5; margin-top: 0.1rem;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def generate_assistant_response(query: str, row: pd.Series) -> str:
    query_text = query.lower().strip()
    machine_name = str(row[machine_type_col])
    defect_name = str(row[defect_col])
    defect_text = defect_name.lower()

    if not query_text:
        return f"Ask about {machine_name}, the defect, probable checks, or maintenance steps."

    if any(keyword in query_text for keyword in ["what", "issue", "problem", "defect"]):
        return f"The record shows {machine_name} with the reported defect: {defect_name}."

    if any(keyword in query_text for keyword in ["fix", "repair", "resolve", "how"]):
        if "electrical" in defect_text:
            return "Inspect power supply, wiring, fuses, connectors, and control circuits. Verify safe isolation before testing."
        if "mechanical" in defect_text or "leak" in defect_text:
            return "Check belts, bearings, seals, moving parts, and hydraulic or fluid lines for wear or leakage."
        if "service" in defect_text or "calibration" in defect_text:
            return "Schedule preventive maintenance, verify calibration, and complete the service log after inspection."
        return "Review the defect note, isolate the machine, and follow the maintenance checklist for the reported issue."

    if any(keyword in query_text for keyword in ["priority", "urgent", "severity"]):
        if "not working" in defect_text or "electrical" in defect_text:
            return "This looks high priority because it affects machine availability and could indicate a power or functional failure."
        return "Treat it as a maintenance priority based on operational impact and the equipment condition on the report."

    if any(keyword in query_text for keyword in ["date", "when"]):
        return f"The issue was recorded on {row[date_col]}."

    return (
        f"For {machine_name}, the current record notes '{defect_name}'. "
        "You can ask for probable checks, repair guidance, or priority assessment."
    )


df = load_data()

st.sidebar.title("Workshop Filters")

work_order_col = "DEME NO."
machine_type_col = "TYPE OF MACHINE"
defect_col = "NATURE OF DEFECT"
date_col = "DATE"

available_deme_numbers = sorted(
    df[work_order_col].dropna().astype(str).unique().tolist()
)
selected_deme_no = st.sidebar.selectbox(
    "Deme No. (click to view list)",
    options=["All"] + available_deme_numbers,
    index=0,
    help="Choose a Deme No. from the list to filter the dashboard.",
)

filtered_df = df.copy()
if selected_deme_no != "All":
    filtered_df = filtered_df[filtered_df[work_order_col].astype(str) == selected_deme_no]

selected_row = None
if not filtered_df.empty:
    selected_label = st.sidebar.selectbox(
        "Choose a record",
        filtered_df.apply(
            lambda row: f"{row[work_order_col]} | {row[machine_type_col]}", axis=1
        ).tolist(),
    )
    selected_row = filtered_df[
        filtered_df.apply(
            lambda row: f"{row[work_order_col]} | {row[machine_type_col]}", axis=1
        ) == selected_label
    ].iloc[0]

st.title("Workshop Defect Dashboard")
st.caption("Browse maintenance records from workshop.csv and inspect defect details quickly.")

# --- Live Data Placeholders ---
alert_container = st.empty()
live_col1, live_col2 = st.columns(2)

with live_col1:
    temp_stat = st.empty()
with live_col2:
    vibe_stat = st.empty()

summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.metric("Total Records", f"{len(df)}")
summary_col2.metric("Filtered Records", f"{len(filtered_df)}")
summary_col3.metric("Unique Machines", f"{df[machine_type_col].nunique()}")

if selected_row is not None:
    st.header(f"Record: {selected_row[work_order_col]}")

    left_col, right_col = st.columns([1.15, 0.85])
    with left_col:
        st.markdown(
            f"""
            <div class="industrial-card">
                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: #b9c2ca;">Machine Type</div>
                <div style="font-size: 2rem; font-weight: 800; margin-top: 0.35rem; color: #dfffa4;">{selected_row[machine_type_col]}</div>
                <div style="font-size: 0.95rem; color: #c7ced5; margin-top: 0.45rem;">Nature of defect: {selected_row[defect_col]}</div>
                <div style="font-size: 0.95rem; color: #c7ced5; margin-top: 0.2rem;">Date: {selected_row[date_col]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Quick context**")
        st.write(
            f"This record links {selected_row[machine_type_col]} to the reported defect '{selected_row[defect_col]}' on {selected_row[date_col]}."
        )

        st.divider()
        st.subheader("Suggested Technician Notes")
        defect_text = str(selected_row[defect_col]).lower()
        if "electrical" in defect_text:
            st.write("Check power supply, wiring continuity, connectors, and breakers before restarting the unit.")
        elif "mechanical" in defect_text or "leak" in defect_text:
            st.write("Inspect moving parts, seals, belts, bearings, and hydraulic lines for wear or leakage.")
        elif "service" in defect_text or "calibration" in defect_text:
            st.write("Schedule preventive maintenance, calibrate the machine, and record the service completion.")
        else:
            st.write("Review the defect note and confirm the machine condition with the maintenance team.")

        st.divider()
        st.subheader("AI Technical Assistant")
        assistant_query = st.text_input(
            "Ask about the selected record",
            placeholder="Example: How do I fix this issue?",
            key=f"assistant_query_{selected_row[work_order_col]}",
        )
        if assistant_query:
            st.info(generate_assistant_response(assistant_query, selected_row))
        else:
            st.caption("Try questions like: What is the defect, how do I fix it, or is it urgent?")

    with right_col:
        st.markdown(
            f"""
            <div class="industrial-card">
                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: #b9c2ca;">Report Snapshot</div>
                <div style="margin-top: 0.75rem;">
                    <div style="color: #c7ced5; font-size: 0.9rem;">Deme No.</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f2f5f7; margin-bottom: 0.5rem;">{selected_row[work_order_col]}</div>
                    <div style="color: #c7ced5; font-size: 0.9rem;">Machine Type</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f2f5f7; margin-bottom: 0.5rem;">{selected_row[machine_type_col]}</div>
                    <div style="color: #c7ced5; font-size: 0.9rem;">Defect</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f2f5f7; margin-bottom: 0.5rem;">{selected_row[defect_col]}</div>
                    <div style="color: #c7ced5; font-size: 0.9rem;">Date</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f2f5f7;">{selected_row[date_col]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        top_defects = filtered_df[defect_col].value_counts().head(5)
        st.markdown("**Top defects in the current view**")
        if not top_defects.empty:
            st.bar_chart(top_defects)
        else:
            st.info("No matching records for the current filter.")
else:
    st.info("Use the sidebar to search by Deme No., machine type, or defect.")


   
# LIVE DATA TRACKING LOOP
# This runs continuously at the bottom to fill the placeholders at the top

try:
    # Connect directly to your Firebase URL to pull the live data
    response = requests.get(FIREBASE_URL)
    if response.status_code == 200:
        data = response.json()
        
        if data:
            # 1. Pull the data values sent by the ESP32
            live_temp = data.get("temperature", 0.0)
            live_vibe = data.get("vibration", 0.0)
            warning_flag = data.get("warning", False)
            warning_msg = data.get("message", "System Safe")

            # 2. Update the Alert Banner at the top dynamically
            if warning_flag:
                alert_container.error(f"⚠️ ALERT: {warning_msg}")
            else:
                alert_container.success("✅ Live Operational Status: All Systems Normal")

            # 3. Inject the live numbers straight into your metric card layout slots
            if live_temp == -127.00:
                temp_stat.metric(label="🔴 Live Temperature", value="Sensor Error", delta="Check 4.7k Resistor")
            else:
                temp_stat.metric(label="🌡️ Live Temperature", value=f"{live_temp:.1f} °C")

            vibe_stat.metric(label="📳 Live Vibration Magnitude", value=f"{live_vibe:.2f} m/s²")
            
except Exception as e:
    # If the internet drops temporarily, fail silently so the dashboard doesn't crash
    pass