## 📂 Project Structure

├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├      
│   │       └── routes.py           # Gathers all v1 endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Environment variables (API keys, DB URIs)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── itinerary.py            # Pydantic models for travel plans
│   │   └── request.py              # Pydantic models for incoming requests
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_manager.py        # Orchestration logic (the "brain")
│   │   ├── agent_worker.py         # Worker with optimization algorithms
│   │   ├── llm_service.py          # Gemini/LLM interaction logic
│   │   └── verifier_service.py     # Data validation logic
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base_provider.py        # Base class for providers
│   │   ├── air_mcp.py              # Flight API client
│   │   ├── rail_mcp.py             # Train API client
│   │   └── bus_mcp.py              # Bus API client
│   └── db/
│       ├── __init__.py
│       ├── database.py             # MongoDB / Redis connection logic
│       └── models.py               # Database models (optional)
│
│
├── .env                            # Store secrets and environment variables
├── .gitignore
├── Dockerfile                      # Containerize the application
├── main.py                         # Entrypoint to start the FastAPI app
└── requirements.txt                # Project dependencies