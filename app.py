import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from agents.root_agent import SSDExpertAgent
import logging
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging.config



load_dotenv()

def setup_logging(config_file: str = "logging.json"):

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Load the JSON configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Apply the configuration
    logging.config.dictConfig(config)
    
setup_logging()

logger = logging.getLogger(__name__)

# @title Setup Session Service and Runner

# --- Session Management ---
# Key Concept: SessionService stores conversation history & state.
# InMemorySessionService is simple, non-persistent storage for this tutorial.
session_service = InMemorySessionService()

# Define constants for identifying the interaction context
APP_NAME = "ask_ssd_expert_app"
USER_ID = "user_1"
SESSION_ID = "session_1" # Using a fixed ID for simplicity


async def init_session(app_name:str,user_id:str,session_id:str) -> InMemorySessionService:
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    logger.info(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session

session = asyncio.run(init_session(APP_NAME,USER_ID,SESSION_ID))

root_agent = SSDExpertAgent().agent

# --- Runner ---
# Key Concept: Runner orchestrates the agent execution loop.
runner = Runner(
    agent=root_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
logger.info(f"Runner created for agent '{runner.agent.name}'.")

# @title Define Agent Interaction Function


async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  logger.info(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  logger.info(f"<<< Agent Response: {final_response_text}")

if __name__ == "__main__":
    try:
        asyncio.run(call_agent_async("Explain the trade-offs between availability and scalability in distributed software systems, and provide a detailed research plan for a downstream agent to investigate these trade-offs.",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID))
    except Exception as e:
        logger.error(f"An error occurred: {e}")