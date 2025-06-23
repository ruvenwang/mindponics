"""PiscinePro fish health agent for monitoring fish health, diseases, and feeding."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from . import prompt
import json
import logging

MODEL = "gemini-2.5-pro"

# Sample fish database (could be loaded from JSON file or cloud storage)
FISH_DATABASE = {
    "tilapia": {
        "scientific_name": "Oreochromis niloticus",
        "optimal_temp": (22, 30),
        "optimal_ph": (6.5, 8.5),
        "feeding_rate": 0.02,  # % of body weight per day
        "life_stages": {
            "fry": {"feed_multiplier": 1.5, "temp_adjustment": 2},
            "juvenile": {"feed_multiplier": 1.2, "temp_adjustment": 1},
            "adult": {"feed_multiplier": 1.0, "temp_adjustment": 0}
        }
    },
    "trout": {
        "scientific_name": "Oncorhynchus mykiss",
        "optimal_temp": (10, 16),
        "optimal_ph": (6.5, 8.0),
        "feeding_rate": 0.015,
        "life_stages": {
            "fry": {"feed_multiplier": 1.8, "temp_adjustment": 2},
            "juvenile": {"feed_multiplier": 1.3, "temp_adjustment": 1},
            "adult": {"feed_multiplier": 1.0, "temp_adjustment": 0}
        }
    }
}

# Sample symptom database (could be connected to Vertex AI Search)
SYMPTOM_DATABASE = {
    "white spots": {
        "disease": "Ichthyophthirius multifiliis (Ich)",
        "treatment": "Increase temperature to 30°C for 3 days, add salt (1-3 g/L)"
    },
    "red sores": {
        "disease": "Aeromonas infection",
        "treatment": "Antibiotic treatment, improve water quality"
    },
    "rapid gilling": {
        "disease": "Low oxygen levels",
        "treatment": "Increase aeration, reduce stocking density"
    }
}

def get_fish_species_info(species: str, life_stage: str) -> dict:
    """
    Retrieves information about fish species and life stage from database.
    
    Args:
        species: Common name of fish species (e.g., "tilapia", "trout")
        life_stage: Life stage of fish ("fry", "juvenile", "adult")
    
    Returns:
        Dictionary with species information optimized for current life stage
    """
    species_info = FISH_DATABASE.get(species.lower(), {})
    life_stage_info = species_info.get("life_stages", {}).get(life_stage, {})
    
    if not species_info:
        return {"error": f"Species '{species}' not found in database"}
    
    # Apply life stage adjustments
    optimized_info = species_info.copy()
    if life_stage_info:
        optimized_info["feeding_rate"] *= life_stage_info.get("feed_multiplier", 1)
        temp_adjust = life_stage_info.get("temp_adjustment", 0)
        optimized_info["optimal_temp"] = (
            species_info["optimal_temp"][0] + temp_adjust,
            species_info["optimal_temp"][1] + temp_adjust
        )
    
    return optimized_info

def calculate_feeding(species: str, life_stage: str, fish_count: int, avg_weight_g: float) -> dict:
    """
    Calculates daily feeding amount based on fish species and life stage.
    
    Args:
        species: Fish species
        life_stage: Current life stage
        fish_count: Number of fish
        avg_weight_g: Average weight per fish in grams
    
    Returns:
        Dictionary with feeding recommendation
    """
    species_info = get_fish_species_info(species, life_stage)
    
    if "error" in species_info:
        return species_info
    
    total_weight_kg = (fish_count * avg_weight_g) / 1000
    daily_feed_kg = total_weight_kg * species_info["feeding_rate"]
    
    return {
        "species": species,
        "life_stage": life_stage,
        "total_weight_kg": total_weight_kg,
        "daily_feed_kg": daily_feed_kg,
        "feeding_rate": species_info["feeding_rate"],
        "recommendation": f"Feed {daily_feed_kg:.3f} kg per day in 2-3 meals"
    }

def check_fish_symptoms(symptoms: str) -> dict:
    """
    Checks fish symptoms against disease database and returns possible diagnoses.
    
    Args:
        symptoms: Comma-separated list of observed symptoms
    
    Returns:
        Dictionary with potential diseases and treatments
    """
    symptom_list = [s.strip().lower() for s in symptoms.split(",")]
    if not (matches := [
        {
            "symptom": symptom,
            "disease": disease_info["disease"],
            "treatment": disease_info["treatment"]
        }
        for symptom, disease_info in SYMPTOM_DATABASE.items()
        if any(s in symptom for s in symptom_list)
    ]):
        return {
            "status": "No matches found",
            "recommendation": "Monitor fish closely and check water parameters"
        }
    else:
        return {
            "symptoms": symptoms,
            "matches": matches,
            "recommendation": "Consult a fish health specialist for confirmation"
        }

# Create tools for the agent
FishSpeciesInfoTool = FunctionTool(
    #name="FishSpeciesInfo",
    #description="Retrieves information about fish species and life stages from database",
    func=get_fish_species_info
)

FeedingCalculatorTool = FunctionTool(
    #name="FeedingCalculator",
    #description="Calculates daily feeding amount based on fish species and life stage",
    func=calculate_feeding
)

FishSymptomCheckerTool = FunctionTool(
    #name="FishSymptomChecker",
    #description="Checks fish symptoms against disease database and returns possible diagnoses",
    func=check_fish_symptoms
)

# Create the fish health agent
class FishHealthAgent(LlmAgent):
    orchestrator_id: str = "orchestrator"
    def __init__(self, name, orchestrator_id: str = "orchestrator", **kwargs):
        super().__init__(
            model=MODEL,
            name=name,
            instruction=prompt.FISH_PROMPT,
            tools=[FishSpeciesInfoTool, FeedingCalculatorTool, FishSymptomCheckerTool],
            output_key="fish_agent_output",
            **kwargs
        )
        logging.info(f"FishHealthAgent '{name}' initialized. Orchestrator: {self.orchestrator_id}")
    
    def step(self, state, mailbox):
        # Process incoming messages (water parameters from Orchestrator)
        messages = mailbox.receive()
        water_params = {}
        
        for sender_id, msg_content in messages:
            if "water_parameters" in msg_content:
                water_params = msg_content["water_parameters"]
                logging.debug(f"[{self.id}] Received water params: {water_params}")
        
        # Prepare analysis context
        context = {
            "water_parameters": water_params,
            "fish_species": state.get("fish_species", "tilapia"),
            "life_stage": state.get("life_stage", "adult"),
            "fish_count": state.get("fish_count", 100),
            "avg_weight_g": state.get("avg_weight_g", 200)
        }
        
        # Run agent analysis
        analysis = super().step(context, mailbox)
        
        # Send results to orchestrator
        output = {
            "fish_health_analysis": analysis,
            "water_parameters": water_params
        }
        mailbox.send(self.orchestrator_id, output)
        
        return output