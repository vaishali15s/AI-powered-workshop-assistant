from pathlib import Path

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


df = load_data()

st.sidebar.title("Workshop Filters")

work_order_col = "DEME NO."
machine_type_col = "TYPE OF MACHINE"
defect_col = "NATURE OF DEFECT"
date_col = "DATE"

search_term = st.sidebar.text_input("Search by Deme No. or machine type")

filtered_df = df.copy()
if search_term:
    search_mask = (
        filtered_df[work_order_col].astype(str).str.contains(search_term, case=False, na=False)
        | filtered_df[machine_type_col].astype(str).str.contains(search_term, case=False, na=False)
        | filtered_df[defect_col].astype(str).str.contains(search_term, case=False, na=False)
    )
    filtered_df = filtered_df[search_mask]

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