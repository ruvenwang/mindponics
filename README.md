# MindPonics - Multi-Agent Aquaponics AI

MindPonics is an AI-powered multi-agent system designed to assist with the design, monitoring, and management of aquaponic systems. It leverages Google Cloud's Agent Development Kit (ADK) and Gemini models.

## Project Goal

To create a collaborative team of specialized AI agents that can:
- Automate complex processes in aquaponics.
- Analyze data and provide insights.
- Offer intelligent assistance for system users.

This project is being developed for the "Agent Development Kit Hackathon with Google Cloud."

## Architecture

The system consists of several specialized agents orchestrated by a central `OrchestratorAgent`:
- **OrchestratorAgent (AquaMaestro):** Routes user queries and coordinates specialist agents.
- **WaterAgent (HydroGuardian):** Manages water quality information.
- *(Future Agents: FishAgent, PlantAgent, BacteriaAgent, EnvironmentAgent)*

## Prerequisites

- Python 3.10+
- Google Cloud SDK (`gcloud` CLI) authenticated
- A Google Cloud Project with Vertex AI API enabled
- `GOOGLE_CLOUD_PROJECT` environment variable set (or configured in `.env` / `config/settings.yaml`)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd mindponics
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure:**
    - Copy `.env.example` to `.env` (if you create an example) and set `GOOGLE_CLOUD_PROJECT`.
    - Review `config/settings.yaml` (though defaults should work with GCP project ID from `.env`).
