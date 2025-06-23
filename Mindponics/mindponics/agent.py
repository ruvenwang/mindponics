"""Top-level agent definition for the Mindponics aquaponics system."""

from google.adk.agents import LlmAgent  
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.water import WaterQualityAgent
from .sub_agents.fish import FishHealthAgent
from .sub_agents.plant import PlantGrowthAgent
from .sub_agents.bacteria import BacteriaAgent
from .sub_agents.environment import EnvironmentAgent

MODEL = "gemini-2.5-pro"

water_agent_instance = WaterQualityAgent(name="HydroGuardian")
fish_agent_instance = FishHealthAgent(name="PiscinePro", orchestrator_id="orchestrator")
plant_agent_instance = PlantGrowthAgent(name="FloraFriend", orchestrator_id="orchestrator")
environment_agent_instance = EnvironmentAgent(name="ClimateController", orchestrator_id="orchestrator", target_temp=25.0, target_humidity=65.0)

orchestrator = LlmAgent(
    name="AquaMaestro",
    model=MODEL,
    description=(
        "A central orchestrator AI for aquaponic system management. "
        "It routes user queries and coordinates specialist agents."
        "It manages water quality, fish health, plant growth, bacteria levels, and environmental conditions. "
        "It provides a unified interface for monitoring and controlling the aquaponic system. "
        "It can also provide insights and recommendations based on the data collected from the system. "
        "It is designed to be user-friendly and efficient, "
        "allowing users to easily manage their aquaponic systems. "
        "It can also provide insights and recommendations based on the data collected from the system. "
        "It is designed to be user-friendly and efficient, "
        "allowing users to easily manage their aquaponic systems. "
    ),
    instruction=prompt.MINDPONICS_PROMPT,
    output_key="mindponics_output",
    tools=[
        AgentTool(agent=water_agent_instance),
        AgentTool(agent=fish_agent_instance),
        AgentTool(agent=plant_agent_instance),
        AgentTool(agent=BacteriaAgent),
        AgentTool(agent=environment_agent_instance),
    ],
)

root_agent = orchestrator
