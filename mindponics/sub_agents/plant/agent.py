"""FloraFriend plant growth agent for monitoring plant health and nutrient management."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from . import prompt
import json
import logging

MODEL = "gemini-2.5-pro"

# Sample plant database
PLANT_DATABASE = {
    "lettuce": {
        "scientific_name": "Lactuca sativa",
        "optimal_temp": (15, 21),
        "optimal_ph": (6.0, 7.0),
        "light_hours": 12,
        "nutrient_needs": {"N": "medium", "P": "medium", "K": "high"},
        "life_stages": {
            "seedling": {"light_multiplier": 1.2, "nutrient_adjust": 0.7},
            "vegetative": {"light_multiplier": 1.0, "nutrient_adjust": 1.0},
            "maturity": {"light_multiplier": 0.8, "nutrient_adjust": 0.9}
        }
    },
    "tomato": {
        "scientific_name": "Solanum lycopersicum",
        "optimal_temp": (18, 26),
        "optimal_ph": (5.5, 6.8),
        "light_hours": 14,
        "nutrient_needs": {"N": "high", "P": "high", "K": "very high"},
        "life_stages": {
            "seedling": {"light_multiplier": 1.1, "nutrient_adjust": 0.6},
            "vegetative": {"light_multiplier": 1.0, "nutrient_adjust": 1.0},
            "flowering": {"light_multiplier": 1.1, "nutrient_adjust": 1.2},
            "fruiting": {"light_multiplier": 1.0, "nutrient_adjust": 1.3}
        }
    }
}

# Plant symptom database
PLANT_SYMPTOM_DB = {
    "yellow leaves": {
        "issue": "Nitrogen deficiency",
        "treatment": "Increase nitrogen levels, check pH (optimal 5.5-6.5 for nutrient uptake)"
    },
    "purple leaves": {
        "issue": "Phosphorus deficiency",
        "treatment": "Increase phosphorus levels, ensure water temperature >18°C for uptake"
    },
    "brown leaf edges": {
        "issue": "Potassium deficiency or salt burn",
        "treatment": "Flush system, adjust potassium levels, check EC"
    },
    "white powdery spots": {
        "issue": "Powdery mildew",
        "treatment": "Improve air circulation, apply neem oil, reduce humidity"
    }
}

def get_plant_species_info(species: str, life_stage: str) -> dict:
    """
    Retrieves information about plant species and life stage from database.
    
    Args:
        species: Common name of plant (e.g., "lettuce", "tomato")
        life_stage: Life stage of plant ("seedling", "vegetative", etc.)
    
    Returns:
        Dictionary with plant information optimized for current life stage
    """
    plant_info = PLANT_DATABASE.get(species.lower(), {})
    life_stage_info = plant_info.get("life_stages", {}).get(life_stage, {})
    
    if not plant_info:
        return {"error": f"Plant species '{species}' not found in database"}
    
    # Apply life stage adjustments
    optimized_info = plant_info.copy()
    if life_stage_info:
        optimized_info["light_hours"] *= life_stage_info.get("light_multiplier", 1)
        nutrient_adjust = life_stage_info.get("nutrient_adjust", 1)
        optimized_info["nutrient_needs"] = {
            nutrient: f"{level} (adjusted)" 
            for nutrient, level in plant_info["nutrient_needs"].items()
        }
    
    return optimized_info

def identify_nutrient_deficiency(symptoms: str, nitrate_level: float, phosphate_level: float, potassium_level: float) -> dict:
    """
    Identifies nutrient deficiencies based on symptoms and nutrient levels.
    
    Args:
        symptoms: Comma-separated list of observed symptoms
        nitrate_level: Current nitrate level in ppm
        phosphate_level: Current phosphate level in ppm
        potassium_level: Current potassium level in ppm
    
    Returns:
        Dictionary with potential deficiencies and treatment recommendations
    """
    symptom_list = [s.strip().lower() for s in symptoms.split(",")]
    nutrient_levels = {
        "nitrogen": nitrate_level,
        "phosphorus": phosphate_level,
        "potassium": potassium_level
    }
    optimal_ranges = {
        "nitrogen": (20, 50),   # ppm
        "phosphorus": (10, 30), # ppm
        "potassium": (20, 40)   # ppm
    }
    
    deficiencies = []
    
    # Check symptoms against known issues
    for symptom, symptom_info in PLANT_SYMPTOM_DB.items():
        if any(s in symptom for s in symptom_list):
            deficiencies.append({
                "symptom": symptom,
                "issue": symptom_info["issue"],
                "treatment": symptom_info["treatment"]
            })
    
    # Check nutrient levels against optimal ranges
    for nutrient, level in nutrient_levels.items():
        low, high = optimal_ranges.get(nutrient, (0, 0))
        if level < low:
            deficiencies.append({
                "issue": f"{nutrient.capitalize()} deficiency",
                "cause": f"Level ({level} ppm) below optimal range ({low}-{high} ppm)",
                "treatment": f"Increase {nutrient} levels gradually"
            })
        elif level > high:
            deficiencies.append({
                "issue": f"{nutrient.capitalize()} excess",
                "cause": f"Level ({level} ppm) above optimal range ({low}-{high} ppm)",
                "treatment": f"Flush system and reduce {nutrient} inputs"
            })
    
    if not deficiencies:
        return {
            "status": "No nutrient deficiencies detected",
            "recommendation": "Maintain current nutrient regimen"
        }
    
    return {
        "symptoms": symptoms,
        "nutrient_levels": nutrient_levels,
        "deficiencies": deficiencies,
        "recommendation": "Adjust nutrient solution and monitor plant response"
    }

def check_plant_symptoms(symptoms: str) -> dict:
    """
    Checks plant symptoms against issue database and returns possible diagnoses.
    
    Args:
        symptoms: Comma-separated list of observed symptoms
    
    Returns:
        Dictionary with potential issues and treatments
    """
    symptom_list = [s.strip().lower() for s in symptoms.split(",")]
    matches = []
    
    for symptom, issue_info in PLANT_SYMPTOM_DB.items():
        if any(s in symptom for s in symptom_list):
            matches.append({
                "symptom": symptom,
                "issue": issue_info["issue"],
                "treatment": issue_info["treatment"]
            })
    
    if not matches:
        return {
            "status": "No matches found",
            "recommendation": "Monitor plants closely and check environmental conditions"
        }
    
    return {
        "symptoms": symptoms,
        "matches": matches,
        "recommendation": "Implement treatments and observe plant response"
    }

# Create tools for the agent
PlantSpeciesInfoTool = FunctionTool(
    name="PlantSpeciesInfo",
    description="Retrieves information about plant species and life stages from database",
    function=get_plant_species_info
)

NutrientDeficiencyIdentifierTool = FunctionTool(
    name="NutrientDeficiencyIdentifier",
    description="Identifies nutrient deficiencies based on symptoms and nutrient levels",
    function=identify_nutrient_deficiency
)

PlantSymptomCheckerTool = FunctionTool(
    name="PlantSymptomChecker",
    description="Checks plant symptoms against issue database and returns possible diagnoses",
    function=check_plant_symptoms
)

# Create the plant growth agent
class PlantGrowthAgent(LlmAgent):
    def __init__(self, name, **kwargs):
        super().__init__(
            model=MODEL,
            name=name,
            instruction=prompt.PLANT_PROMPT,
            tools=[PlantSpeciesInfoTool, NutrientDeficiencyIdentifierTool, PlantSymptomCheckerTool],
            output_key="plant_agent_output",
            **kwargs
        )
        self.orchestrator_id = kwargs.get("orchestrator_id", "orchestrator")
        logging.info(f"PlantGrowthAgent '{name}' initialized. Orchestrator: {self.orchestrator_id}")
    
    def step(self, state, mailbox):
        # Process incoming messages (nutrient levels from Orchestrator)
        messages = mailbox.receive()
        nutrient_levels = {}
        
        for sender_id, msg_content in messages:
            if "nutrient_levels" in msg_content:
                nutrient_levels = msg_content["nutrient_levels"]
                logging.debug(f"[{self.id}] Received nutrient levels: {nutrient_levels}")
        
        # Prepare analysis context
        context = {
            "nutrient_levels": nutrient_levels,
            "plant_species": state.get("plant_species", "lettuce"),
            "life_stage": state.get("life_stage", "vegetative"),
            "observed_symptoms": state.get("observed_symptoms", "")
        }
        
        # Run agent analysis
        analysis = super().step(context, mailbox)
        
        # Send results to orchestrator
        output = {
            "plant_health_analysis": analysis,
            "nutrient_levels": nutrient_levels
        }
        mailbox.send(self.orchestrator_id, output)
        
        return output