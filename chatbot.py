from google import genai
from google.genai import types
import os
import re
from utils import get_current_weather, get_historical_weather
from rag import TravelRAG
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

rag_system = TravelRAG()
class TravelChatbot:
    def __init__(self):
        # load Gemini client
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        # init RAG
        self.rag = TravelRAG("Worldwide Travel Cities Dataset (Ratings and Climate).csv")

    def parse_prompt(self, message: str) -> dict:
        """
        Use Gemini to parse the user's free-text request into structured details.
        
        The function always returns a dict with the following keys:
        - place: the destination city
        - theme: one of the following themes: Culture, Adventure, Nature, Beaches, Nightlife, Cuisine, Wellness, Urban, Seclusion
        - duration: the length of the trip in days
        - time: a string indicating the time of year (e.g. "Today", "Next Week", "Summer", etc.)
        - extras: any additional information the user provided
        
        The function is very forgiving and will return defaults if the user does not provide all of the information.
        For example, if the user does not provide a theme, the function will default to "Culture".
        If the user does not provide a duration, the function defaults to 5.
        If the user does not provide a time, the function will default to "Today".
        """

        prompt = f"""
        You are a strict JSON parser. Read the user's travel request and return JSON ONLY.
        Rules:
        - Output MUST be a single JSON object, no prose, no code fences.
        - Keys: place (string), theme (string), duration (integer, days), time (string), extras (string).
        - Defaults if missing: theme="Culture", duration=5, time="Today", extras="".
        
        User request: {message}
        """

        print("🔹 Sending parse prompt to Gemini (trimmed preview):", prompt[:300])

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )

        text = response.text.strip()
        print("🔹 [parse_prompt] Gemini raw output:", text)

        # --- Fix: strip ```json ... ``` fences if present ---
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)   # remove opening fence (```json or ``` etc.)
            text = re.sub(r"```$", "", text)               # remove trailing fence
            text = text.strip()
            print("🔹 [parse_prompt] Cleaned output (after removing fences):", text)

        # --- Try parsing JSON ---
        try:
            details = json.loads(text)
        except Exception as e:
            print("❌ [parse_prompt] JSON parsing failed:", e)
            details = {
                "place": "Unknown",
                "theme": "Culture",
                "duration": 5,
                "time": "Today",
                "extras": ""
            }

        print("✅ [parse_prompt] Final parsed details:", details)
        return details

    def travel_planner(self, details: dict) -> dict:
        """
        Build full response: itinerary + weather + RAG info.
        """
        place = details.get("place", "Unknown")
        duration = details.get("duration", 5)
        theme = details.get("theme", "Culture")
        time = details.get("time", "Today")

        # --- Weather ---
        if time.lower() == "today":
            weather = get_current_weather(place)
        else:
            # crude month mapping
            month_map = {
                "january": 1, "february": 2, "march": 3,
                "april": 4, "may": 5, "june": 6,
                "july": 7, "august": 8, "september": 9,
                "october": 10, "november": 11, "december": 12
            }
            month = month_map.get(time.lower(), datetime.today().month)
            weather = get_historical_weather(place, month)

        # --- RAG info ---
        rag_info = self.rag.search(place)
        rag_summary = rag_info.split("🌍 Overview:")[-1].split("🌡️")[0].strip() \
        if "🌍 Overview:" in rag_info else rag_info[:200]

        # --- Itinerary (ask Gemini again, but now with context) ---
        planning_prompt = f"""
        You are a helpful travel agent. Based on the following details,
        suggest a day-by-day itinerary.

        Trip details:
        Place: {place}
        Duration: {duration} days
        Theme: {theme}
        Time: {time}
        Extra Info: {details.get("extras","")}

        Additional knowledge:
        {rag_info}

        Weather summary:
        {weather.get("summary","N/A")}
        """

        resp = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=planning_prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )

        itinerary_text = resp.text.strip()

        # --- Final structured output ---
        return {
            "parsed_prompt": details,
            "weather": weather,
            "rag_info_raw": rag_info,
            "rag_summary": rag_summary,
            "itinerary": itinerary_text
        }

    def generate_itinerary(self, message: str) -> dict:
        """
        Main entry point to generate a travel itinerary.

        The method takes a user's free-text request and returns a structured JSON
        with the following keys: parsed_prompt, weather, rag_info_raw, rag_summary, and itinerary.

        The method first calls parse_prompt to extract structured information from the request
        and then calls travel_planner to generate the itinerary based on the extracted information.
        """
        details = self.parse_prompt(message)
        result = self.travel_planner(details)
        return result







