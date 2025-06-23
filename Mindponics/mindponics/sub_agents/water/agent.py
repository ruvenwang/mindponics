"""HydroGuardian water quality agent for monitoring and managing water parameters."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from utils.sensor_simulator import get_simulated_sensor_data
from . import prompt
import logging

MODEL = "gemini-2.5-pro"

# Optimal water parameter ranges
OPTIMAL_RANGES = {
    "ph": (6.5, 7.5),
    "ammonia": (0.0, 0.5),     # mg/L
    "nitrite": (0.0, 0.2),     # mg/L
    "nitrate": (5.0, 150.0),   # mg/L
    "temperature": (18.0, 30.0), # °C - species dependent
    "dissolved_oxygen": (5.0, 8.0) # mg/L
}

def get_water_parameters() -> dict:
    """
    Reads water parameters from sensor simulator.
    Returns a dictionary with pH, ammonia, nitrite, nitrate, temperature, and dissolved oxygen.
    """
    try:
        sensor_data = get_simulated_sensor_data()
        return {
            "ph": sensor_data.get("ph", 7.0),
            "ammonia": sensor_data.get("ammonia", 0.0),
            "nitrite": sensor_data.get("nitrite", 0.0),
            "nitrate": sensor_data.get("nitrate", 0.0),
            "temperature": sensor_data.get("temperature", 22.0),
            "dissolved_oxygen": sensor_data.get("oxygen", 6.5)
        }
    except Exception as e:
        logging.error(f"Error reading water parameters: {e}")
        # Return safe default values
        return {"ph": 7.0, "ammonia": 0.0, "nitrite": 0.0, 
                "nitrate": 0.0, "temperature": 22.0, "dissolved_oxygen": 6.5}

def diagnose_water_quality(parameters: dict) -> dict:
    """
    Diagnoses water quality issues based on parameters.
    Returns a dictionary with issues and severity levels.
    """
    issues = []
    
    # Check each parameter against optimal ranges
    for param, value in parameters.items():
        if param in OPTIMAL_RANGES:
            low, high = OPTIMAL_RANGES[param]
            if value < low:
                issues.append({
                    "parameter": param,
                    "value": value,
                    "issue": f"Low {param}",
                    "severity": "critical" if param in ["ammonia", "nitrite", "dissolved_oxygen"] else "warning"
                })
            elif value > high:
                issues.append({
                    "parameter": param,
                    "value": value,
                    "issue": f"High {param}",
                    "severity": "critical" if param in ["ammonia", "nitrite"] else "warning"
                })
    
    # Special case: Ammonia + Nitrite combination
    if parameters["ammonia"] > 1.0 and parameters["nitrite"] > 0.5:
        issues.append({
            "parameter": "ammonia+nitrite",
            "value": f"{parameters['ammonia']}/{parameters['nitrite']}",
            "issue": "Toxic ammonia and nitrite levels",
            "severity": "critical",
            "priority": 1
        })
    
    # Special case: Low oxygen + high temperature
    if parameters["dissolved_oxygen"] < 4.0 and parameters["temperature"] > 28.0:
        issues.append({
            "parameter": "oxygen+temperature",
            "value": f"{parameters['dissolved_oxygen']}/{parameters['temperature']}",
            "issue": "Low oxygen exacerbated by high temperature",
            "severity": "critical",
            "priority": 1
        })
    
    # Sort issues by severity and priority
    severity_order = {"critical": 0, "warning": 1}
    issues.sort(key=lambda x: (severity_order.get(x.get("severity", "warning"), x.get("priority", 2)), x.get("priority", 2)))

    return {
        "parameters": parameters,
        "issues": issues,
        "status": "issues_detected" if issues else "optimal"
    }

def suggest_corrective_actions(parameters: dict, diagnosis: dict) -> dict:
    """
    Suggests corrective actions based on water parameters and diagnosis.
    Returns a dictionary with recommended actions.
    """
    actions = []
    params = parameters.copy()
    
    # Handle critical issues first
    for issue in diagnosis.get("issues", []):
        if issue["severity"] == "critical":
            if "ammonia" in issue["parameter"]:
                actions.extend([
                    "Perform immediate 25-50% water change",
                    "Reduce feeding immediately",
                    "Check biofilter function",
                    "Add salt (1-3 ppt) to protect fish",
                    "Increase aeration immediately",
                    "Reduce stocking density if possible",
                    "Add additional air stones or surface agitation"
                ])
            elif "oxygen" in issue["parameter"]:
                actions.extend([
                    "Increase aeration immediately",
                    "Reduce stocking density if possible",
                    "Add additional air stones or surface agitation"
                ])
    
    # Handle specific parameter adjustments
    if params["ph"] < 6.0:
        actions.append("Add potassium bicarbonate to raise pH gradually")
    elif params["ph"] > 8.0:
        actions.append("Add phosphoric acid to lower pH gradually")
    
    if params["ammonia"] > 0.5:
        actions.extend([
            "Reduce feeding by 50%",
            "Add beneficial bacteria supplement"
        ])
    
    if params["nitrate"] > 150:
        actions.extend([
            "Perform 20% water change",
            "Increase plant density to consume more nitrates"
        ])
    
    if params["temperature"] > 30.0:
        actions.extend([
            "Install water chiller or shade system",
            "Increase aeration as warm water holds less oxygen"
        ])
    
    # General recommendations
    if not actions:
        actions.append("Maintain current water parameters")
    else:
        actions.append("Retest water parameters after 24 hours")
    
    return {
        "diagnosis": diagnosis,
        "actions": actions,
        "priority": "immediate" if any(issue["severity"] == "critical" for issue in diagnosis.get("issues", [])) else "routine"
    }

# Create tools for the agent
GetWaterParametersTool = FunctionTool(
    #name="GetWaterParameters",#
    #description="Reads current water parameters from sensors",#
    func=get_water_parameters
)

WaterQualityDiagnosisTool = FunctionTool(
    #name="WaterQualityDiagnosis",#
    #description="Diagnoses water quality issues based on parameters",#
    func=diagnose_water_quality
)

CorrectiveActionSuggesterTool = FunctionTool(
    #name="CorrectiveActionSuggester",#
    #description="Recommends corrective actions for water quality issues",#
    func=suggest_corrective_actions
)

# Create the water quality agent
class WaterQualityAgent(LlmAgent):
    orchestrator_id: str = "orchestrator"
    
    def __init__(self, name, orchestrator_id: str = "orchestrator", **kwargs):
        super().__init__(
            model=MODEL,
            name=name,
            instruction=prompt.WATER_PROMPT,
            tools=[GetWaterParametersTool, WaterQualityDiagnosisTool, CorrectiveActionSuggesterTool],
            output_key="water_agent_output",
            **kwargs
        )
        logging.info(f"WaterQualityAgent '{name}' initialized. Orchestrator: {self.orchestrator_id}")
    
    def step(self, state, mailbox):
        # Get current water parameters
        parameters = GetWaterParametersTool.function()
        
        # Diagnose water quality
        diagnosis = WaterQualityDiagnosisTool.function(parameters)
        
        # Suggest corrective actions
        actions = CorrectiveActionSuggesterTool.function(parameters, diagnosis)
        
        # Prepare output
        output = {
            "water_parameters": parameters,
            "diagnosis": diagnosis,
            "corrective_actions": actions
        }
        
        # Log and send to orchestrator
        logging.info(f"[WaterQualityAgent] Parameters: {parameters}, Diagnosis: {diagnosis.get('status')}")
        mailbox.send(self.orchestrator_id, output)
        
        return output