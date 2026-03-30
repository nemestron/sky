import streamlit as st
import os
import time

st.set_page_config(page_title="Upload & Process | Sky Sentinel", layout="wide")
st.title("Upload and Process Video")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Video Input")
    uploaded_file = st.file_uploader("Upload Surveillance Video (MP4/AVI)", type=["mp4", "avi"])
    
    use_sample = st.button("Use Sample Video (Bundled)")
    
    video_path = None
    if uploaded_file is not None:
        video_path = os.path.join("data", "uploaded_video.mp4")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name} successfully.")
    elif use_sample:
        sample_path = os.path.join("data", "sample_surveillance.mp4")
        if os.path.exists(sample_path):
            video_path = sample_path
            st.success("Loaded sample_surveillance.mp4")
        else:
            st.warning("Sample video not found. Please ensure it exists in the data directory.")

with col2:
    st.subheader("Processing Control")
    if video_path and st.button("Start Processing", type="primary"):
        st.session_state['is_processing'] = True
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Integration point: In production, this imports and triggers the Phase 3/4/5 pipeline
        # Here we simulate the pipeline execution loop to demonstrate UI state management
        total_frames = 100
        simulated_logs = []
        
        for i in range(total_frames):
            # Update UI Progress
            progress = int(((i + 1) / total_frames) * 100)
            progress_bar.progress(progress)
            status_text.text(f"Processing frame {i+1} of {total_frames}...")
            
            # Simulate a generated log entry attached to session state
            if i % 15 == 0:
                simulated_logs.append({
                    "frame_id": i,
                    "timestamp": f"12:{(i//15):02d}",
                    "location": "Main Gate" if i % 2 == 0 else "Garage",
                    "objects": ["Blue Ford F-150"] if i % 2 == 0 else ["Person in dark clothing"],
                    "activity": "Vehicle moving through gate" if i % 2 == 0 else "Loitering near entrance"
                })
            
            time.sleep(0.02) # Simulate VLM API delay
            
        st.session_state['processed_frames'] = simulated_logs
        st.session_state['is_processing'] = False
        
        status_text.text("Processing Complete!")
        st.success(f"Successfully processed {total_frames} frames.")
        
        st.info("Navigate to 'Live Analysis' or 'Alerts Panel' to view results.")

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
