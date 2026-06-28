from google.adk import Agent
import logging

from mcp import StdioServerParameters
from llm_models.model_provider import ModelProvider
from google.adk.tools import google_search
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.skills import load_skill_from_dir
from pathlib import Path
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
import sys

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """A factory class to create the research agent with the desired model and configuration."""
    
    def __init__(self):
        self.agent = self.create_agent()


    def create_agent(self) -> Agent:
        """
        Creates and returns an Agent instance configured with the specified model.
        """
        semantic_scholar_tools = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=[
                        "--from", 
                        "git+https://github.com/akapet00/semantic-scholar-mcp", 
                        "semantic-scholar-mcp"
                    ]
                )
            )
        )



        return Agent(
            name="Distributed_Software_Systems_Researcher",
            model=ModelProvider.get_model("gemma4"),
            output_key='research_findings',
            description="""Conducts technical deep-dives into specific distributed algorithms, failure modes, protocols, and industry case studies to gather accurate engineering facts.""",
            instruction="""
                Execute the research steps outlined in this plan: {{research_plan}}.
                Provide facts and data points.
                """,
            # tools=[semantic_scholar_tools]
        )
