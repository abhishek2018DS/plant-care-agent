# 🌱 Plant Care Assistant

A conversational AI agent built with **Google ADK (Agent Development Kit)** that helps plant owners care for indoor greenery, compute custom fertilizer dilution ratios, manage plant catalog records, generate botanical visuals, and locate nearby plant nurseries.

![Plant Care Assistant Demo](./demo.gif)

---

## 🌟 Implemented Capabilities & Wired-Up Services

This project implements the following Google Cloud services, AI tools, and frameworks as defined in `app/` and `agents-cli-manifest.yaml`:

### 🧠 Core Agent & Frameworks
- **Google ADK (Agent Development Kit)**: Orchestrates the core reasoning loop (`root_agent`) with session state management and memory callbacks.
- **Agent Engine Sandbox Code Executor**: Executes Python math calculations safely (`AgentEngineSandboxCodeExecutor`) for custom fertilizer N-P-K dilution ratios (`compute_fertilizer_ratio`).
- **A2UI (Agent-to-User Interface v0.8)**: Generates structured, client-rendered card surfaces (Card, Column, Row, Text, Image) via `a2ui_callback`.

### ⚡ Gemini & Vertex AI Models
- **Gemini Flash (`gemini-flash-latest`)**: Serves as the primary conversational LLM for instruction following and tool selection.
- **Gemini Image (`gemini-3.1-flash-lite-image`)**: Generates custom plant health visuals in the `global` region (`generate_plant_image`).
- **Gemini Omni (`gemini-omni-flash-preview`)**: Generates short plant care video demonstrations via the Vertex AI Interactions API in the `global` region (`generate_plant_video`).

### 🗄️ Database, Storage & Memory
- **Google Cloud Firestore**: Persists indoor plant metadata (`list_plants_in_catalog`, `get_plant_details`, `add_or_update_plant`).
- **Google Cloud Storage (GCS)**: Stores and serves generated plant images and videos directly from a public media bucket (`plant-care-agent-media-8a5b8`).
- **ADK Memory Bank (`PreloadMemoryTool`, `LoadMemoryTool`)**: Persists user plant preferences, watering history, and allergies across sessions.

### 📍 External Tools & Integrations
- **Google Maps API**: Geocodes user locations (`geocode_address`) and finds nearby plant nurseries or garden centers (`find_nearby_places`).
- **Botanical API**: Searches botanical species databases (`search_botanical_species`).

> [!NOTE]
> **Planned / Unimplemented Features**:
> - *RAG Vector Search*: Planned for future release (not yet implemented in current codebase).

---

## 📁 Repository Structure

```
plant-care-agent/
├── app/
│   ├── agent.py               # Root ADK agent configuration & tool registration
│   ├── firestore_db.py        # Firestore CRUD operations for plant catalog
│   ├── image_tool.py          # Gemini image generation & Cloud Storage upload
│   ├── video_tool.py          # Gemini Omni video generation & Cloud Storage upload
│   ├── maps_tools.py          # Google Maps Geocoding & Places tools
│   ├── botanical_api.py       # Botanical species lookup tool
│   ├── a2ui_utils.py          # A2UI Basic Catalog (v0.8) surface renderer
│   ├── fast_api_app.py        # FastAPI server bridging A2A chat requests
│   └── __init__.py            # App package initializer
├── frontend/
│   ├── static/index.html      # Responsive web UI with prompt chips & A2UI renderer
│   ├── main.py                # Frontend FastAPI proxy
│   └── Dockerfile             # Container configuration for Cloud Run
├── demo.gif                   # Looping video recording of agent interactions
├── agents-cli-manifest.yaml   # Manifest for agents-cli deployment
└── requirements.txt           # Python dependencies
```

---

## 🚀 Setup & Local Execution

### Prerequisites
- **Python 3.12+**
- **Google Cloud SDK (`gcloud`)**
- **`agents-cli`** (`uv tool install google-agents-cli`)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Set the target Agent Engine resource name and directory:
```bash
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<REGION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
```

### 3. Run Agent Engine Proxy Locally
To launch the FastAPI proxy server for local testing:
```bash
python main.py
```

### 4. Deploy to Agent Runtime & Cloud Run
Deploy the reasoning engine backend and frontend proxy using Google Cloud tools:

```bash
# Deploy agent to Agent Runtime
agents-cli deploy

# Deploy frontend proxy to Cloud Run
cd frontend
gcloud run deploy plant-care-frontend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="$AGENT_ENGINE_RESOURCE_NAME",AGENT_DIRECTORY="$AGENT_DIRECTORY"
```
