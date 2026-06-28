import asyncio
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk import Event, Workflow

import logging
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging.config

from utils.mail_service import MailService

from .planner_agent import PlannerAgent
from .researcher_agent import ResearcherAgent
from .synthesizer_agent import SynthesizerAgent

load_dotenv()

# import io
# Force system standard streams to use UTF-8 encoding
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def setup_logging(config_file: str = "logging.json"):

    current_script = Path(__file__).resolve()
    
    # 2. Go up two levels: parent is script's folder, parent.parent is one level higher
    config_file_path = current_script.parent.parent / "logging.json"

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Load the JSON configuration
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    # Apply the configuration
    logging.config.dictConfig(config)
    
setup_logging()

logger = logging.getLogger(__name__)

def sendMail(query: str, response: str) -> None:
    mail_service = MailService()
    subject = f"Result for query: {query}"
    body = response

    # Send the email to a predefined recipient
    recipient_email = os.environ.get("MAIL_RECEPIENT")
    if recipient_email:
        success = mail_service.send_mail(
            to_email=recipient_email,
            subject=subject,
            body=body,
            is_html=False
        )
        if success:
            logging.info(f"result email sent to {recipient_email}")
        else:
            logging.error("Failed to send result email.")
    else:
        logging.warning("MAIL_RECEPIENT environment variable not set. Email not sent.")


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



planner_agent = PlannerAgent().agent
researcher_agent = ResearcherAgent().agent
synthesizer_agent = SynthesizerAgent().agent

root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", planner_agent, researcher_agent,  synthesizer_agent),
    ],
    context_cache_config=None
)


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

    all_responses = [] # To collect outputs from all agents in the workflow

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        logger.info(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Append each agent's final output instead of breaking the loop
                all_responses.append(event.content.parts[0].text)

            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                all_responses.append(final_response_text)

            # The loop naturally ends when ALL agents in the pipeline are done executing
            # Your ultimate output (the Synthesizer's work) will be the last item in the list
    if all_responses:
        final_response_text = all_responses[-1] 
        logger.info(f"\n>>> Final Response from Agent:\n{final_response_text}")
        


async def run_workflow():
    try:
        # 1. Run setup tasks and create/initialize the session inside the same loop
        session = await init_session(APP_NAME, USER_ID, SESSION_ID)
        query = "Explain AWS database services"
        
        # 2. Execute the workflow using await instead of a separate asyncio.run
        await call_agent_async(
            query,
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        
        logger.info("Agent execution completed. Fetching updated session state...")
        
        # 3. CRITICAL: Fetch the fresh state from the storage service
        # (Replace `runner.session_service` with your actual session service instance if named differently)
        updated_session = await runner.session_service.get_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        )
        
        # 4. Extract the final answer from the fresh session object
        final_response_text = updated_session.state.get("synthesized_report")

        if final_response_text:
            print(f"\n>>> Final Synthesized Report:\n{final_response_text}")
            logger.info(f"\n>>> Final Synthesized Report:\n{final_response_text}")
            sendMail(query, final_response_text)
        else:
            logger.warning("Workflow finished, but 'synthesized_report' was not found in state.")
            
    except Exception as e:
        logger.error(f"An error occurred during agent execution: {e}")

if __name__ == "__main__":
    # Orchestrate the entire flow through a single entry point loop
    asyncio.run(run_workflow())