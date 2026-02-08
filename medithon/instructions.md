Backend implementation. The data layer is fully locked down. Build order:

backend/data_loader.py — load JSONs into ChromaDB collections
backend/openfda_client.py — OpenFDA API wrapper
backend/rag_engine.py — LangChain query pipeline
backend/app.py — Flask routes
Do you have your Gemini API key ready? That's the one thing needed before starting the backend.