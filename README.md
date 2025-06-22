# Mindponics: Aquaponics Multi-Agent System

Mindponics is an advanced aquaponics monitoring and management system powered by Google's Agent Development Kit (ADK). This project uses a multi-agent architecture where specialized AI agents collaborate to optimize and maintain a balanced aquaponics ecosystem.

## Key Features

- **Multi-Agent Architecture:** Six specialized agents working in harmony
- **Real-time Monitoring:** Continuous tracking of water, fish, plant, and environmental parameters
- **Intelligent Recommendations:** AI-driven insights for system optimization
- **Predictive Maintenance:** Early detection of potential issues
- **Modular Design:** Easy to extend with new agents and functionality

## System Architecture

graph TD
    A[AquaMaestro<br>Orchestrator] --> B[HydroGuardian<br>Water Quality]
    A --> C[PiscinePro<br>Fish Health]
    A --> D[FloraFriend<br>Plant Growth]
    A --> E[BiofilterBuddy<br>Bacteria Management]
    A --> F[ClimateController<br>Environment]
    B --> G[External Sensors]
    C --> H[Fish Health Database]
    D --> I[Plant Knowledge Base]

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
