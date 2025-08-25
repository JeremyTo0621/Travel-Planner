from google import genai
from google.genai import types
import os
from utils import get_attractions, optimize_itinerary, get_weather_info, get_crowd_info
from rag import TravelRAG

client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))
rag_system = TravelRAG()

def research_agent(city: str, theme: str) -> dict:
    """Agent that researches destinations using RAG and recommends attractions

    Args:
        city (str): City of interest
        theme (str): Theme of interest

    Returns:
        dict: Research and recommended attractions
    """

    # Use RAG to find relevant information
    query = f"{city} {theme} travel attractions recommendations"
    relevant_docs = rag_system.search(query, top_k=3)
    
    prompt = f"""
    You are a travel research agent. Based on this knowledge:
    {' '.join(relevant_docs)}
    
    Research and recommend attractions in {city} for someone interested in {theme}.
    Return a JSON-like response with attractions and brief descriptions.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3)
    )
    
    return {"research": response.text, "rag_sources": relevant_docs}

def planning_agent(city: str, theme: str, days: int) -> dict:
    """Agent that creates optimized itineraries based on research
    
    Args:
        city (str): City of interest
        theme (str): Theme of interest
        days (int): Number of days for the trip
    
    Returns:
        dict: Enhanced itinerary
    """

    # Get research from research agent
    research = research_agent(city, theme)
    
    # Get attractions (enhanced with research)
    attractions = get_attractions(city, theme)
    
    # Get additional info
    weather = get_weather_info(city)
    crowd_info = get_crowd_info(city)
    
    # Optimize itinerary
    itinerary = optimize_itinerary(attractions, days)
    
    prompt = f"""
    You are a travel planning agent. Create a detailed itinerary for {city} over {days} days.
    
    Research context: {research['research']}
    Weather info: {weather}
    Crowd information: {crowd_info}
    
    Base itinerary: {itinerary}
    
    Enhance this itinerary with:
    1. Best times to visit each location
    2. Transportation recommendations
    3. Weather-appropriate advice
    4. Crowd-avoiding tips
    5. Local food recommendations
    
    Format as a clear day-by-day plan.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7)
    )
    
    return {
        "itinerary": itinerary,
        "enhanced_plan": response.text,
        "weather": weather,
        "crowd_info": crowd_info,
        "research_sources": research['rag_sources']
    }

def planner_agent(city: str, theme: str, days: int):
    """Main orchestrating agent"""
    return planning_agent(city, theme, days)