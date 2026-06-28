from google.adk import Agent
import logging
from llm_models.model_provider import ModelProvider
from google.adk.tools import google_search
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.skills import load_skill_from_dir
from pathlib import Path

logger = logging.getLogger(__name__)


class SynthesizerAgent:
    """A factory class to create the research agent with the desired model and configuration."""
    
    def __init__(self):
        self.agent = self.create_agent()

    def create_agent(self) -> Agent:
        """
        Creates and returns an Agent instance configured with the specified model.
        """
        return Agent(
            name="Distributed_Software_Systems_Synthesizer",
            model=ModelProvider.get_model("gemma4"),
            output_key="synthesized_report",
            description="""Merges fragmented research data into a cohesive, production-ready System Design Document, resolving architectural trade-offs and formatting structural layout.""",
            instruction="""
                Review the original plan: {{research_plan}}.
                Analyze the collected findings: {{research_findings}}.
                Write a final cohesive report answering the user's original request.
            """,
        )
