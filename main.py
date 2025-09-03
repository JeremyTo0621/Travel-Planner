from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import TravelChatbot
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Travel Planner", version="2.0.0")
chatbot = TravelChatbot()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Main chat endpoint (synchronous).
    Returns structured JSON with itinerary, weather, rag info, and parsed prompt.
    """
    try:
        result = chatbot.generate_itinerary(request.message)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "Travel Chatbot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
