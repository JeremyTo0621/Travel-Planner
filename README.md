# Travel-Planner
An AI-powered travel planning assistant that generates personalized itineraries, weather summaries, and location insights based on user input. Users simply describe their desired trip in plain English, and the system provides structured recommendations.

## Features
- **Interactive Chat UI** built with Streamlit
- **Smart itinerary generation** using a combination of RAG (Retrieval-Augmented Generation) and AI
- **Weather and location insights** for selected destinations
- **Graceful API handling** – warns when external API quotas (e.g., Gemini) are exceeded
- **Custom RAG module** using local city data for fast recommendations
- **Docker-ready** for easy deployment on cloud platforms like AWS EC2

## How it Works
1. User submits a trip request (e.g., "I want a 5-day cultural trip in Japan in June") via the Streamlit UI.
2. FastAPI backend processes the request and queries the RAG module for relevant destinations.
3. AI generates a detailed itinerary and summarizes weather, locations, and highlights.
4. The frontend displays:
   - **Itinerary**
   - **Weather & Location Overview**
   - **Prompt Analysis & RAG context**
5. If an external API quota is reached, the system shows a friendly warning instead of failing.

## Tech Stack
- **Python 3.9**  
- **FastAPI** – backend API for processing requests  
- **Streamlit** – interactive UI  
- **Pandas / NumPy** – data processing  
- **Faiss** – vector search for RAG module  
- **Docker** – containerization for deployment  

## Project Structure
├── main.py                 # FastAPI backend
├── chatbot.py              # TravelChatbot class
├── travel_ui.py            # Streamlit frontend
├── rag.py                  # RAG document retrieval module
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Optional multi-service deployment
├── .dockerignore           # Files to ignore in Docker build
├── .gitignore              # Git ignore file
└── README.md