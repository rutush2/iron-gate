# Iron Gate: Flexible API Gateway & Testing Engine

Iron Gate is a high-performance, asynchronous API gateway built using FastAPI and HTTPX. It features a dedicated flexible input testing mode designed to handle dynamic routing parameters across all standard HTTP verbs (GET, POST, PUT, DELETE, PATCH) while maintaining live dashboard compatibility.

## System Architecture

The gateway processes client entries through modular configurations, isolating administrative routes from the core execution engine to provide smooth local performance tracking.

* **API Gateway Engine:** Built with FastAPI utilizing wildcard pattern match configurations to resolve path structures.
* **Key Vault Storage:** Localized file system layer handling secure unique tracking distributions.
* **Telemetry Control:** Exposes administrative status updates, analytical logging tracking arrays, and live endpoint status states.

## Project Structure

```text
iron_gate/
├── main.py
├── app.py
├── README.md
├── utils/
│   └── load_balancer.py
├── storage/
│   └── key_vault.py
├── middleware/
│   ├── auth_guard.py
│   └── rate_limiter.py
└── router/
    └── proxy_engine.py

Setup and Installation

1) Install the required dependencies:
pip install fastapi uvicorn httpx streamlit pandas

2) Start the core API Gateway server application using Uvicorn:
uvicorn main:app --reload

3) Launch the live visual tracking dashboard interface using Streamlit:
streamlit run app.py

Interactive Module Layout:

System Configuration: Handles status verifications and API registration key generations (/admin/generate).

Flexible Input Testing Mode: Dynamic route processing matching specific entries without external network dependencies.
