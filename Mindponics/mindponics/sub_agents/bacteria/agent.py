"""BiofilterBuddy bacteria agent for managing nitrification cycle and biofilter health."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from . import prompt

MODEL = "gemini-1.5-flash"

def calculate_biofilter_size(fish_load_kg: float) -> float:
    """
    Calculates the required biofilter volume based on fish load.
    
    Formula: biofilter_volume = fish_load_kg * 5 (liters per kg of fish)
    This is a simplified formula - real-world calculations would be more complex.
    """
    return fish_load_kg * 5

def monitor_nitrification_cycle(ammonia: float, nitrite: float, nitrate: float) -> str:
    """
    Analyzes NH3, NO2, NO3 levels to determine nitrification cycle status.
    
    Returns a status message based on the parameters:
    - 'healthy': All parameters within normal ranges
    - 'warning': One parameter slightly out of range
    - 'critical': One or more parameters significantly out of range
    """
    status = "healthy"
    
    if ammonia > 1.0 or nitrite > 0.5 or nitrate > 100:
        status = "critical"
    elif ammonia > 0.5 or nitrite > 0.2 or nitrate > 80:
        status = "warning"
    
    return status

# Create tools for the agent
BiofilterSizingCalculatorTool = FunctionTool(
    #name="BiofilterSizingCalculator",
    #description="Calculates required biofilter volume based on fish load (in kg)",
    func=calculate_biofilter_size
)

NitrificationCycleMonitorTool = FunctionTool(
    #name="NitrificationCycleMonitor",
    #description="Analyzes NH3, NO2, NO3 levels to determine nitrification cycle status",
    func=monitor_nitrification_cycle
)

# Create the bacteria agent
BacteriaAgent = LlmAgent(
    model=MODEL,
    name="bacteria_agent",
    instruction=prompt.BACTERIA_PROMPT,
    tools=[BiofilterSizingCalculatorTool, NitrificationCycleMonitorTool],
    output_key="bacteria_agent_output"
)