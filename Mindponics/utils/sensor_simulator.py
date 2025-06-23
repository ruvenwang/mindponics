"""Utility functions for sensor data simulation and retrieval."""

import logging
import random

# Fallback sensor data simulator
def get_simulated_sensor_data() -> dict:
    """Generates simulated sensor data with realistic aquaponics values."""
    return {
        "ph": round(random.uniform(6.0, 8.0), 1),
        "ammonia": round(random.uniform(0.0, 1.0), 2),
        "nitrite": round(random.uniform(0.0, 0.5), 2),
        "nitrate": round(random.uniform(0.0, 200.0), 1),
        "temperature": round(random.uniform(18.0, 30.0), 1),
        "oxygen": round(random.uniform(4.0, 8.0), 1),
        "humidity": round(random.uniform(40.0, 80.0), 1),
        "light_level": random.randint(300, 1000)
    }

def get_water_parameters() -> dict:
    """
    Reads water parameters from sensor simulator.
    Returns a dictionary with pH, ammonia, nitrite, nitrate, temperature, and dissolved oxygen.
    """
    try:
        # Try to import the project-specific simulator
        from ..utils.sensor_simulator import get_simulated_sensor_data as project_simulator
        sensor_data = project_simulator()
    except ImportError:
        # Fall back to the default simulator
        sensor_data = get_simulated_sensor_data()
        logging.warning("Using fallback sensor data simulator")
    
    try:
        return {
            "ph": sensor_data.get("ph", 7.0),
            "ammonia": sensor_data.get("ammonia", 0.0),
            "nitrite": sensor_data.get("nitrite", 0.0),
            "nitrate": sensor_data.get("nitrate", 0.0),
            "temperature": sensor_data.get("temperature", 22.0),
            "dissolved_oxygen": sensor_data.get("oxygen", 6.5)
        }
    except Exception as e:
        logging.error(f"Error processing water parameters: {e}")
        # Return safe default values
        return {
            "ph": 7.0,
            "ammonia": 0.0,
            "nitrite": 0.0,
            "nitrate": 0.0,
            "temperature": 22.0,
            "dissolved_oxygen": 6.5
        }