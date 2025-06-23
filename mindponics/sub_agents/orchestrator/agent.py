"""AquaMaestro orchestrator agent for coordinating the aquaponics system."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.agents import BaseAgent
from . import prompt
import logging

MODEL = "gemini-2.5-pro"

def create_orchestrator_agent(water_agent, fish_agent, plant_agent, bacteria_agent, environment_agent):
    """Creates the orchestrator agent with delegation tools to all sub-agents."""
    
    # Create delegation tools for each sub-agent
    def delegate_to_water_agent(query: str) -> str:
        """Delegates water-related queries to the WaterQualityAgent."""
        logging.info(f"[Orchestrator] Delegating to WaterQualityAgent: {query}")
        return water_agent.process_query(query)

    def delegate_to_fish_agent(query: str) -> str:
        """Delegates fish-related queries to the FishHealthAgent."""
        logging.info(f"[Orchestrator] Delegating to FishHealthAgent: {query}")
        return fish_agent.process_query(query)

    def delegate_to_plant_agent(query: str) -> str:
        """Delegates plant-related queries to the PlantGrowthAgent."""
        logging.info(f"[Orchestrator] Delegating to PlantGrowthAgent: {query}")
        return plant_agent.process_query(query)

    def delegate_to_bacteria_agent(query: str) -> str:
        """Delegates bacteria-related queries to the BacteriaAgent."""
        logging.info(f"[Orchestrator] Delegating to BacteriaAgent: {query}")
        return bacteria_agent.process_query(query)

    def delegate_to_environment_agent(query: str) -> str:
        """Delegates environment-related queries to the EnvironmentAgent."""
        logging.info(f"[Orchestrator] Delegating to EnvironmentAgent: {query}")
        return environment_agent.process_query(query)

    def synthesize_responses(responses: list) -> str:
        """Synthesizes responses from multiple agents into a cohesive summary."""
        logging.info("[Orchestrator] Synthesizing responses from multiple agents")
        summary = "\n\n".join(responses)
        return f"Here's a comprehensive summary based on all agents:\n\n{summary}"

    # Create tools for the orchestrator
    DelegateToWaterQualityAgentTool = FunctionTool(
        name="DelegateToWaterQualityAgent",
        description="Delegate water quality related questions to the WaterQualityAgent",
        function=delegate_to_water_agent
    )

    DelegateToFishHealthAgentTool = FunctionTool(
        name="DelegateToFishHealthAgent",
        description="Delegate fish health related questions to the FishHealthAgent",
        function=delegate_to_fish_agent
    )

    DelegateToPlantGrowthAgentTool = FunctionTool(
        name="DelegateToPlantGrowthAgent",
        description="Delegate plant growth related questions to the PlantGrowthAgent",
        function=delegate_to_plant_agent
    )

    DelegateToBacteriaAgentTool = FunctionTool(
        name="DelegateToBacteriaAgent",
        description="Delegate bacteria and biofilter related questions to the BacteriaAgent",
        function=delegate_to_bacteria_agent
    )

    DelegateToEnvironmentAgentTool = FunctionTool(
        name="DelegateToEnvironmentAgent",
        description="Delegate environment related questions to the EnvironmentAgent",
        function=delegate_to_environment_agent
    )

    SynthesizeInformationTool = FunctionTool(
        name="SynthesizeInformation",
        description="Combine responses from multiple agents into a cohesive summary",
        function=synthesize_responses
    )

    # Create the orchestrator agent
    return LlmAgent(
        model=MODEL,
        name="AquaMaestro",
        instruction=prompt.ORCHESTRATOR_PROMPT,
        tools=[
            DelegateToWaterQualityAgentTool,
            DelegateToFishHealthAgentTool,
            DelegateToPlantGrowthAgentTool,
            DelegateToBacteriaAgentTool,
            DelegateToEnvironmentAgentTool,
            SynthesizeInformationTool
        ],
        output_key="orchestrator_output"
    )