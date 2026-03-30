import streamlit as st
import time

st.set_page_config(page_title="Live Analysis | Sky Sentinel", layout="wide")
st.title("Live Frame Analysis")

if 'processed_frames' not in st.session_state or not st.session_state['processed_frames']:
    st.info("No processed data available. Please run the processing pipeline in the 'Upload & Process' module first.")
    st.stop()

logs = st.session_state['processed_frames']

# Filtering Layout
st.markdown("### Filters")
col1, col2 = st.columns(2)
with col1:
    locations = list(set([log.get('location', 'Unknown') for log in logs]))
    selected_location = st.selectbox("Filter by Location", ["All"] + locations)
with col2:
    selected_object = st.text_input("Filter by Object Type (e.g., 'truck', 'person')")

st.divider()

# Apply logic filters
filtered_logs = logs
if selected_location != "All":
    filtered_logs = [log for log in filtered_logs if log.get('location') == selected_location]
if selected_object:
    filtered_logs = [log for log in filtered_logs if any(selected_object.lower() in obj.lower() for obj in log.get('objects', []))]

# Live Feed Rendering
feed_container = st.container()

with feed_container:
    for log in filtered_logs:
        # Styled Card using Streamlit columns
        card_col1, card_col2 = st.columns([1, 4])
        
        with card_col1:
            # Placeholder for extracted frame thumbnail
            st.image("https://via.placeholder.com/150x100.png?text=Frame+" + str(log.get('frame_id')), use_column_width=True)
        
        with card_col2:
            st.markdown(f"**Timestamp:** {log.get('timestamp')} | **Location:** {log.get('location')}")
            st.markdown(f"**Detected Objects:** {', '.join(log.get('objects', []))}")
            st.markdown(f"**Activity:** {log.get('activity')}")
        
        st.markdown("---")
        time.sleep(0.1) # Simulate real-time feed arrival delay for UX

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
