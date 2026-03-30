import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory

# Load environment variables
load_dotenv()

# Define the System Prompt as a constant for the agent
SYSTEM_PROMPT = """You are the 'Sky Sentinel Security Analyst', an intelligent AI assistant.
You have access to a database of processed surveillance frames from a 24-hour monitoring session.
You can answer questions about detected objects, security alerts, and events.
When answering, you must always cite specific times, locations, and frame IDs to ground your responses in the actual data.
Do not hallucinate events, detections, or alerts that are not present in the provided context."""

def get_llm():
    """
    Initializes and returns the Gemini 2.5 Flash LLM configuration.
    Raises ValueError if the API key is not found in the environment.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")

    # Temperature is set to 0.1 to ensure factual, grounded responses based on surveillance data
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )

def get_memory(window_size=10):
    """
    Initializes and returns the conversation memory.
    The buffer window maintains the context of the last N exchanges for follow-up questions.
    """
    return ConversationBufferWindowMemory(
        k=window_size,
        memory_key="chat_history",
        return_messages=True
    )