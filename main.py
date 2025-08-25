from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import planner_agent
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Travel Planner", version="1.0.0")

class TripRequest(BaseModel):
    city: str
    theme: str
    days: int

@app.get("/")
def read_root():
    return {"message": "AI Travel Planner API is running!"}

@app.post("/plan")
def plan_trip(request: TripRequest):
    try:
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not found")
        
        result = planner_agent(request.city, request.theme, request.days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}