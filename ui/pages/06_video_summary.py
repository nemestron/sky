import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Session Summary | Sky Sentinel", layout="wide")
st.title("Post-Session Summary & Statistics")

st.markdown("### Executive Summary")

# Mock Summary Data
summary_text = (
    "During the 24-hour monitoring session, multiple vehicles were detected "
    "at the Main Gate, including a Blue Ford F-150 that was observed repeatedly. One person was "
    "detected loitering near the Garage at 00:01, triggering a HIGH severity alert. An unauthorized "
    "person was also seen at the North Perimeter. All other activity remained within normal operating parameters."
)

st.info(summary_text)

if st.button("Regenerate Summary", type="primary"):
    with st.spinner("Regenerating summary via LLM..."):
        import time
        time.sleep(2)
    st.success("Summary regenerated based on latest database index.")

st.divider()
st.markdown("### Surveillance Statistics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Detections by Location")
    # Mock bar chart data
    bar_data = pd.DataFrame({
        "Location": ["Main Gate", "Garage", "North Perimeter", "South Fence"],
        "Detections": [45, 12, 3, 8]
    }).set_index("Location")
    st.bar_chart(bar_data)

with col2:
    st.subheader("Alerts by Severity")
    # Mock pie chart data using matplotlib
    labels = 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    sizes = [1, 2, 5, 8]
    colors = ['#ff4b4b', '#ffa421', '#ffe234', '#3dd56d']
    
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    
    # Make background transparent to match Streamlit dark theme
    fig1.patch.set_alpha(0.0)
    for text in ax1.texts:
        text.set_color('white')
    
    st.pyplot(fig1)

st.divider()
st.subheader("Activity Timeline (24-Hour Coverage)")

# Mock timeline data using line chart
time_indices = [f"{i:02d}:00" for i in range(24)]
# Simulate spikes in activity
activity_volume = np.random.poisson(lam=2, size=24)
activity_volume[8] += 15  # Morning rush
activity_volume[17] += 10 # Evening rush

timeline_data = pd.DataFrame(
    activity_volume,
    columns=['Activity Volume'],
    index=time_indices
)
st.line_chart(timeline_data)

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
