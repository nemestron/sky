import logging
from langchain.agents import initialize_agent, AgentType
from .agent_config import get_llm, get_memory, SYSTEM_PROMPT
from .tools import AGENT_TOOLS

# Configure logging for the agent module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentinelAgent:
    def __init__(self):
        """
        Initializes the SentinelAgent by assembling the LLM, memory, tools, and system prompt.
        Uses a structured chat zero-shot ReAct agent capable of handling multiple complex tools.
        """
        try:
            self.llm = get_llm()
            self.memory = get_memory(window_size=10)
            self.tools = AGENT_TOOLS
            
            # Initialize the agent with robust parsing error handling
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory,
                agent_kwargs={
                    "prefix": SYSTEM_PROMPT
                },
                handle_parsing_errors="Please check your output format and ensure it strictly conforms to the expected JSON structure. Use the provided tools."
            )
            logger.info("SentinelAgent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SentinelAgent: {str(e)}")
            self.agent_executor = None

    def chat(self, user_question: str) -> str:
        """
        Processes a user question, orchestrates tool calls, and returns the agent's natural language response.
        Includes graceful error handling for LLM or tool failures.
        """
        if not self.agent_executor:
            return "System Error: Sentinel Agent is not properly initialized. Please check configuration and API keys."
            
        try:
            # Invoke the agent executor with the user's input
            response = self.agent_executor.invoke({"input": user_question})
            return response.get("output", "I could not generate a response based on the available data.")
        except Exception as e:
            logger.error(f"Error during agent execution: {str(e)}")
            return "I encountered an internal error while analyzing the surveillance data. Please try rephrasing your question or ask about a different time/location."

# Creator: Dhiraj Malwade