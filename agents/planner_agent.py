from google.adk import Agent
import logging
from llm_models.model_provider import ModelProvider
from google.adk.tools import google_search
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.skills import load_skill_from_dir
from pathlib import Path

logger = logging.getLogger(__name__)


class PlannerAgent:
    """A factory class to create the planner agent with the desired model and configuration."""
    
    def __init__(self):
        self.agent = self.create_agent()
    
    def create_agent(self) -> Agent:
        """
        Creates and returns an Agent instance configured with the specified model.
        """
        current_dir = Path(__file__).resolve().parent

        skills_dir = current_dir.parent / "skills" / "research-planner"

        logger.info(f"Loading skill from directory: {skills_dir}")

        loaded_skill = load_skill_from_dir(skills_dir)

        logger.info(f"Loaded skill: {loaded_skill.name} with description: {loaded_skill.description}")

        my_skill_toolset = SkillToolset(skills=[loaded_skill])

        return Agent(
            name="Distributed_Software_Systems_Research_Planner",
            model=ModelProvider.get_model("gemma4"),
            output_key='research_plan',
            description="""A strategic research architect that deconstructs complex Distributed Software Systems topics into structured, sequential, and execution-ready research blueprints for downstream researcher agents.""",
            instruction="""You are the **Planner Agent**, an advanced orchestration system designed to generate comprehensive, highly technical execution plans for a downstream Research Agent. Your primary operational domain is distributed software systems architecture.

                ### 1. Behavioral Guardrails
                * **Do Not Perform the Research:** Your job is to plan, not to execute. Do not provide answers to the research questions; instead, write explicit, actionable instructions for the Research Agent to find those answers.
                * **Technical Rigor:** Use precise distributed systems terminology (e.g., CAP/PACELC theorem, consistent hashing, quorum reads, split-brain, MTTR, linearizability).
                * **Concrete Guidance:** Always provide specific real-world system examples (like Google Spanner, Apache Cassandra, Kafka, or Amazon Dynamo) within the tasks to give the research agent concrete reference points.

                ### 2. Execution Context
                Analyze the user's high-level distributed systems query, isolate the availability and scalability concerns, and output the final plan. Keep your instructions objective, technical, and ready for automated execution.""",
            #tools=[my_skill_toolset]
        )
