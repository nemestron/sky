import streamlit as st

def initialize_session_state():
    """Initializes shared state variables for cross-page persistence."""
    default_states = {
        'processed_frames': [],
        'alerts': [],
        'is_processing': False
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    st.set_page_config(
        page_title="Sky Sentinel - Drone Security Analyst",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    st.title("Sky Sentinel")
    st.markdown("### Intelligent Drone Surveillance Analytics")
    st.info("Please select a module from the sidebar navigation to begin.")

if __name__ == "__main__":
    main()

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
