import streamlit as st
import time

st.set_page_config(page_title="Agent Chat | Sky Sentinel", layout="wide")
st.title("Conversational Agent Chat")
st.markdown("Interact with the Sky Sentinel Security Analyst agent to query surveillance data.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
st.sidebar.header("Agent Controls")
if st.sidebar.button("Clear Chat History", type="primary"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.subheader("Example Questions")
example_questions = [
    "What objects were in the video?",
    "Were there any alerts?",
    "How many trucks were seen today?",
    "What happened at the main gate after 10 PM?"
]

# Handle example question clicks
selected_example = None
for q in example_questions:
    if st.sidebar.button(q):
        selected_example = q

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
user_input = st.chat_input("Ask a question about the surveillance data...")

# Override input if example question was clicked
if selected_example:
    user_input = selected_example

if user_input:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Simulate agent response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing surveillance data..."):
            time.sleep(1.5) # Simulate API latency
            
            # Mock response logic (Replaces actual LangChain execution for UI prototype)
            query_lower = user_input.lower()
            if "truck" in query_lower:
                full_response = "Based on the processed frames, there were 3 trucks detected today at the Main Gate."
            elif "alert" in query_lower:
                full_response = "Yes, there are 4 active alerts, including 1 CRITICAL alert regarding a person in a restricted area."
            elif "object" in query_lower:
                full_response = "I detected multiple vehicles (including a Blue Ford F-150 and a delivery truck) and individuals in dark clothing."
            elif "main gate" in query_lower:
                full_response = "After 10 PM at the Main Gate, no significant vehicle traffic was detected, but an individual was flagged for loitering."
            else:
                full_response = f"I am currently in prototype mode. You asked: '{user_input}'. In the full backend integration, this will trigger the LangChain tool suite against the SQLite database."
            
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

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
