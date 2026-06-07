import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter

from core.processor import load_data, load_config, get_cycle_ids
from core.replay import ReplayEngine
from core.classifier import StateClassifier
from core.validator import ValidationEngine
from core.anomaly import AnomalyDetector
from services.timeline import TimelineService
from services.report import ReportGenerator

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Telemetry Validation Platform",
    layout="wide"
)

st.title("Telemetry Operations & Validation Platform")
st.caption("NASA Battery Dataset — Discharge Cycle Monitoring")

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.markdown("## 🛰 Telemetry Platform")
st.sidebar.markdown("---")
st.sidebar.subheader("Replay Controls")

df = load_data()
cycle_ids = get_cycle_ids(df)

selected_cycle = st.sidebar.selectbox(
    "Select Cycle", cycle_ids, index=0
)

speed = st.sidebar.select_slider(
    "Replay Speed",
    options=[1, 5, 10, 50, 100, 1000],
    value=1000
)

run = st.sidebar.button("▶ Run Replay")

# ── Layout ────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
metric_voltage    = col1.empty()
metric_current    = col2.empty()
metric_temp       = col3.empty()
metric_capacity   = col4.empty()
metric_power    = col5.empty()

st.divider()

col_state, col_anomaly = st.columns([1, 2])
with col_state:
    st.subheader("Current State")
    state_box = st.empty()

with col_anomaly:
    st.subheader("Latest Anomaly")
    anomaly_box = st.empty()

st.divider()

st.subheader("Live Telemetry")
chart_placeholder = st.empty()

st.divider()

col_timeline, col_report = st.columns(2)
with col_timeline:
    st.subheader("Event Timeline")
    timeline_placeholder = st.empty()

with col_report:
    st.subheader("Mission Summary")
    report_placeholder = st.empty()

# ── State colors ──────────────────────────────────────────
STATE_COLORS = {
    'NOMINAL':          '🟢',
    'THERMAL_WARNING':  '🟡',
    'HIGH_LOAD':        '🟠',
    'LOW_BATTERY':      '🔴',
    'DEGRADED':         '🔴',
    'EOL':              '⛔',
}

STATE_COLORS_HEX = {
    'NOMINAL':         '#00C49F',
    'THERMAL_WARNING': '#FFB347',
    'HIGH_LOAD':       '#FFA500',
    'LOW_BATTERY':     '#FF6B6B',
    'DEGRADED':        '#FF6B6B',
    'EOL':             '#FF0000'
}

if run:
    engine     = ReplayEngine(df, speed=float(speed))
    classifier = StateClassifier()
    validator  = ValidationEngine()
    detector   = AnomalyDetector()
    timeline   = TimelineService()
    report     = ReportGenerator()

    times, voltages, currents, temps = [], [], [], []
    latest_anomaly = "None"
    update_every = 5
    row_count = 0

    for row in engine.stream(cycle_id=int(selected_cycle)):
        state      = classifier.classify(row)
        validation = validator.validate(row, state)
        anomalies  = detector.detect(row)
        timeline.update(row, state, anomalies, validation)
        report.update(row, state, anomalies, validation)

        row_count += 1

        times.append(row['time'])
        voltages.append(row['voltage_measured'])
        currents.append(row['current_abs'])
        temps.append(row['temperature_measured'])

        metric_voltage.metric("Voltage (V)", f"{row['voltage_measured']:.3f}")
        metric_current.metric("Current (A)", f"{row['current_abs']:.3f}")
        metric_temp.metric("Temperature (°C)", f"{row['temperature_measured']:.1f}")
        metric_capacity.metric("Capacity (%)", f"{row['capacity_pct']:.1f}")
        metric_power.metric("Power (W)", f"{row['voltage_measured'] * row['current_abs']:.2f}")

        icon = STATE_COLORS.get(state, '⚪')
        color = STATE_COLORS_HEX.get(state, '#FFFFFF')
        state_box.markdown(
            f"<h2 style='color:{color}'>{icon} {state}</h2>",
            unsafe_allow_html=True
        )

        if anomalies:
            latest_anomaly = anomalies[-1]['reason']
        anomaly_box.warning(latest_anomaly)

        if row_count % update_every == 0:
            window = 50
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times, y=voltages,
                name='Voltage (V)', line=dict(color='royalblue')
            ))
            fig.add_trace(go.Scatter(
                x=times, y=temps,
                name='Temperature (°C)', line=dict(color='tomato')
            ))
            fig.add_trace(go.Scatter(
                x=times, y=currents,
                name='Current (A)', line=dict(color='green')
            ))

            events = timeline.get_events()
            for event in events:
                event_time = event['time']
                if event['type'] == 'STATE_CHANGE':
                    fig.add_vline(
                        x=event_time,
                        line_dash='dash',
                        line_color='gray',
                        annotation_text=event['description'].split('→')[-1].strip(),
                        annotation_position='top'
                    )
                elif 'ANOMALY' in event['type']:
                    fig.add_vline(
                        x=event_time,
                        line_dash='dot',
                        line_color='red',
                        annotation_text='⚠',
                        annotation_position='top'
                    )

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation='h')
            )
            chart_placeholder.plotly_chart(fig, use_container_width=True)

            events = timeline.get_events()
            if events:
                timeline_placeholder.dataframe(
                    pd.DataFrame(events)[['time', 'type', 'description']],
                    use_container_width=True
                )

            summary = report.generate()
            report_data = {
                'Metric': [
                    'Total Cycles', 'Total Rows', 'Total Duration (s)',
                    'Time in NOMINAL (s)', 'Time in NOMINAL (%)',
                    'Time in THERMAL_WARNING (s)', 'Time in THERMAL_WARNING (%)',
                    'Total Anomalies', 'Current Spikes', 'Validation Failures'
                ],
                'Value': [
                    summary['total_cycles'],
                    summary['total_rows'],
                    summary['total_duration_seconds'],
                    summary['state_durations_seconds'].get('NOMINAL', 0),
                    summary['state_duration_pct'].get('NOMINAL', 0),
                    summary['state_durations_seconds'].get('THERMAL_WARNING', 0),
                    summary['state_duration_pct'].get('THERMAL_WARNING', 0),
                    summary['total_anomalies'],
                    summary['anomaly_counts'].get('CURRENT_SPIKE', 0),
                    summary['validation_failures']
                ]
            }
            report_placeholder.dataframe(
                pd.DataFrame(report_data),
                use_container_width=True,
                hide_index=True
            )

    report.save_json()
    report.save_csv()
    st.success("Replay complete. Reports saved.")