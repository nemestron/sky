import streamlit as st
import pandas as pd

st.set_page_config(page_title="Query Interface | Sky Sentinel", layout="wide")
st.title("Frame Index Query Engine")

# Sidebar Query Builder
st.sidebar.header("Query Builder")
st.sidebar.markdown("Define search parameters across multiple domains.")

time_range = st.sidebar.slider("Time Range (Hour)", 0, 23, (0, 23))
obj_type = st.sidebar.text_input("Object Type (e.g., 'truck', 'person')")
location = st.sidebar.selectbox("Location", ["All", "Main Gate", "Garage", "North Perimeter", "South Fence"])
alerts_only = st.sidebar.checkbox("Show Frames with Alerts Only")
search_term = st.sidebar.text_input("Full-Text Search (VLM Description)")

st.markdown("### Query Results")

if st.sidebar.button("Execute Query", type="primary"):
    # Simulated query execution delay
    with st.spinner("Executing multi-dimensional query across index..."):
        import time
        time.sleep(1)
        
    st.success("Query executed successfully.")
    
    # Mock DataFrame for demonstration (Replaces actual SQLite integration in prototype phase)
    mock_data = [
        {"Frame ID": 104, "Timestamp": "08:15", "Location": "Main Gate", "Detected Objects": "Blue Ford F-150", "Alert Status": "None"},
        {"Frame ID": 215, "Timestamp": "14:30", "Location": "Garage", "Detected Objects": "Delivery Truck, Person", "Alert Status": "None"},
        {"Frame ID": 844, "Timestamp": "02:15", "Location": "North Perimeter", "Detected Objects": "Person in dark clothing", "Alert Status": "CRITICAL"}
    ]
    
    # Filter simulation based on 'alerts_only' checkbox
    if alerts_only:
        mock_data = [d for d in mock_data if d["Alert Status"] != "None"]
        
    if not mock_data:
        st.warning("No records matched your specific query parameters.")
    else:
        df = pd.DataFrame(mock_data)
        st.dataframe(df, use_container_width=True)
        
        # CSV Export Functionality
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name='sentinel_query_results.csv',
            mime='text/csv',
        )
else:
    st.info("Configure your parameters in the sidebar and click 'Execute Query' to search the frame index.")

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
