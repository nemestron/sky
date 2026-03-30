import streamlit as st

st.set_page_config(page_title="Alerts Panel | Sky Sentinel", layout="wide")
st.title("Security Alerts Dashboard")

# Initialize mock alerts for UI demonstration if pipeline hasn't run
if 'alerts' not in st.session_state or not st.session_state['alerts']:
    st.session_state['alerts'] = [
        {"alert_id": "A-001", "severity": "CRITICAL", "message": "Person in restricted area", "timestamp": "02:15", "location": "North Perimeter", "is_resolved": False, "triggered_by": "Person in dark clothing"},
        {"alert_id": "A-002", "severity": "HIGH", "message": "Person loitering at main gate", "timestamp": "00:01", "location": "Main Gate", "is_resolved": False, "triggered_by": "Person standing stationary > 5m"},
        {"alert_id": "A-003", "severity": "MEDIUM", "message": "Unauthorised vehicle detected", "timestamp": "14:30", "location": "Garage", "is_resolved": True, "triggered_by": "White Van (Unknown Plate)"},
        {"alert_id": "A-004", "severity": "LOW", "message": "Repeated vehicle visit", "timestamp": "16:45", "location": "Main Gate", "is_resolved": False, "triggered_by": "Blue Ford F-150"}
    ]

alerts = st.session_state['alerts']

# Summary Metrics
st.markdown("### Alert Metrics")
total = len(alerts)
critical = len([a for a in alerts if a['severity'] == 'CRITICAL'])
high = len([a for a in alerts if a['severity'] == 'HIGH'])
medium = len([a for a in alerts if a['severity'] == 'MEDIUM'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Alerts", total)
col2.metric("Critical", critical)
col3.metric("High", high)
col4.metric("Medium", medium)

st.divider()

# Filters
st.markdown("### Active Filters")
f_col1, f_col2 = st.columns(2)
with f_col1:
    sev_filter = st.selectbox("Filter by Severity", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
with f_col2:
    locations = ["All"] + list(set([a.get('location', 'Unknown') for a in alerts]))
    loc_filter = st.selectbox("Filter by Location", locations)

filtered_alerts = alerts
if sev_filter != "All":
    filtered_alerts = [a for a in filtered_alerts if a['severity'] == sev_filter]
if loc_filter != "All":
    filtered_alerts = [a for a in filtered_alerts if a['location'] == loc_filter]

st.divider()

# Alert Rendering
st.markdown("### Alert Log")
if not filtered_alerts:
    st.info("No alerts match the current filter criteria.")
else:
    for i, alert in enumerate(filtered_alerts):
        # Determine color coding
        severity_color = {
            "CRITICAL": "#ff4b4b",
            "HIGH": "#ffa421",
            "MEDIUM": "#ffe234",
            "LOW": "#3dd56d"
        }.get(alert['severity'], "grey")
        
        with st.container():
            # Apply styling directly using markdown for the badge effect
            st.markdown(f"""
            <div style="border-left: 6px solid {severity_color}; padding: 15px; background-color: #262730; margin-bottom: 10px; border-radius: 4px;">
                <h4 style="margin-top:0px; margin-bottom:5px;">
                    <span style="color:{severity_color};">[{alert['severity']}]</span> {alert['timestamp']} - {alert['location']}
                </h4>
                <p style="margin-bottom:5px;"><strong>Alert:</strong> {alert['message']}</p>
                <p style="margin-bottom:10px;"><small><strong>Trigger:</strong> {alert['triggered_by']}</small></p>
                <p style="margin-bottom:0px; color:{'#3dd56d' if alert['is_resolved'] else '#ff4b4b'}">
                    <strong>Status:</strong> {'Resolved' if alert['is_resolved'] else 'Active Investigation'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Resolution action button
            if not alert['is_resolved']:
                if st.button("Mark as Resolved", key=f"resolve_{alert['alert_id']}_{i}"):
                    alert['is_resolved'] = True
                    st.rerun()

# UI Polish & Footer Injection
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from ui.components import render_creator_footer, load_css
    load_css()
    render_creator_footer()
except ImportError:
    pass
