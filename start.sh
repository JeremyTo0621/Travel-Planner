#!/bin/bash
# Start FastAPI in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit (keeps container running)
streamlit run travel_ui.py --server.address 0.0.0.0 --server.port 8501