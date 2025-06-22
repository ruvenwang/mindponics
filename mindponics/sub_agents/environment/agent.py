
"""ClimateController environment agent for monitoring and controlling environmental conditions."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from utils.sensor_simulator import get_simulated_sensor_data
from . import prompt
import logging

MODEL = "gemini-2.5-pro"

def get_ambient_conditions() -> dict:
    """
    Reads environmental conditions from sensor simulator.
    Returns a dictionary with temperature, humidity, and light_level.
    """
    try:
        sensor_data = get_simulated_sensor_data()
        return {
            "temperature": sensor_data.get("temperature", 22.0),
            "humidity": sensor_data.get("humidity", 60.0),
            "light_level": sensor_data.get("light_level", 500)
        }
    except Exception as e:
        logging.error(f"Error reading sensor data: {e}")
        return {"temperature": 22.0, "humidity": 60.0, "light_level": 500}

def suggest_climate_control(current_temp: float, target_temp: float, 
                            current_humidity: float, target_humidity: float) -> str:
    """
    Recommends climate control actions based on current vs target conditions.
    Returns a string with specific recommendations.
    """
    recommendations = []
    
    # Temperature adjustments
    temp_diff = current_temp - target_temp
    if abs(temp_diff) > 1.0:
        if temp_diff > 0:
            recommendations.append("Increase ventilation or cooling")
            if temp_diff > 3.0:
                recommendations.append("Activate evaporative cooling system")
        else:
            recommendations.append("Activate heating system")
            if temp_diff < -3.0:
                recommendations.append("Increase insulation or close vents")
    
    # Humidity adjustments
    humidity_diff = current_humidity - target_humidity
    if abs(humidity_diff) > 5.0:
        if humidity_diff > 0:
            recommendations.append("Increase ventilation to reduce humidity")
        else:
            recommendations.append("Activate humidification system")
    
    # Light cycle adjustments
    if current_temp < target_temp - 2.0 and current_humidity > target_humidity + 5.0:
        recommendations.append("Extend light cycle to boost temperature and reduce humidity")
    
    if not recommendations:
        return "Environmental conditions are optimal. No adjustments needed."
    
    return "Recommendations: " + "; ".join(recommendations)

# Create tools for the agent
GetAmbientConditionsTool = FunctionTool(
    name="GetAmbientConditions",
    description="Reads current ambient temperature, humidity, and light levels from sensors",
    function=get_ambient_conditions
)

ClimateControlSuggesterTool = FunctionTool(
    name="ClimateControlSuggester",
    description="Recommends climate control adjustments based on current vs target conditions",
    function=suggest_climate_control
)

# Create the environment agent
class EnvironmentAgent(LlmAgent):
    def __init__(self, name, **kwargs):
        super().__init__(
            model=MODEL,
            name=name,
            instruction=prompt.ENVIRONMENT_PROMPT,
            tools=[GetAmbientConditionsTool, ClimateControlSuggesterTool],
            output_key="environment_agent_output",
            **kwargs
        )
        self.target_temp = kwargs.get("target_temp", 25.0)
        self.target_humidity = kwargs.get("target_humidity", 65.0)
        logging.info(f"EnvironmentAgent '{name}' initialized. Targets: Temp={self.target_temp}°C, Humidity={self.target_humidity}%")
    
    def step(self, state, mailbox):
        # Get current conditions
        current_conditions = GetAmbientConditionsTool.function()
        
        # Generate recommendations
        recommendations = ClimateControlSuggesterTool.function(
            current_conditions["temperature"],
            self.target_temp,
            current_conditions["humidity"],
            self.target_humidity
        )
        
        # Prepare output
        output = {
            "current_conditions": current_conditions,
            "recommendations": recommendations,
            "targets": {
                "temperature": self.target_temp,
                "humidity": self.target_humidity
            }
        }
        
        # Log and send to orchestrator
        logging.info(f"[EnvironmentAgent] Conditions: {current_conditions}, Recommendations: {recommendations}")
        mailbox.send("orchestrator", output)
        
        return output