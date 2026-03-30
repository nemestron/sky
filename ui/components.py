import streamlit as st

def render_creator_footer():
    """Renders the mandatory creator footer across all pages."""
    footer_html = """
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0a192f; padding: 12px; text-align: center; border-top: 1px solid #112240; z-index: 999;">
        <p style="margin: 0; font-size: 14px; color: #ccd6f6; font-family: sans-serif;">
            <strong>Creator: Dhiraj Malwade</strong> | 
            <a href="https://www.linkedin.com/in/dhiraj-malwade-6a8385399/" target="_blank" style="color: #64ffda; text-decoration: none; font-weight: bold;">LinkedIn</a> | 
            <a href="https://github.com/nemestron/sky" target="_blank" style="color: #64ffda; text-decoration: none; font-weight: bold;">GitHub</a>
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def load_css():
    """Loads custom CSS from the styles file."""
    try:
        with open("ui/styles.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass