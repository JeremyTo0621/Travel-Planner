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
        Use Gemini to parse the user’s free-text request into structured details.
        Always returns a dict with keys: place, theme, duration, time, extras.
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
        Entry point called from FastAPI.
        """
        details = self.parse_prompt(message)
        result = self.travel_planner(details)
        return result

# class TravelChatbot:
#     def __init__(self):
#         self.client = client
#         self.rag = rag

#     def parse_prompt(self, user_prompt: str) -> dict:
#         """
#         Ask Gemini to extract fields. Returns a dict:
#         {
#           "place": "Tokyo, Japan",
#           "theme": "culture",
#           "duration_days": 5,
#           "time_expression": "June",   # or "today" if unspecified
#           "extra": "any extra text user gave"
#         }
#         """
#         instruction = f"""
# You are an extractor. Given the user's travel request, output ONLY a single JSON object (no explanation).
# Extract and normalize these fields (use null if unknown):
# - place: city or "city, country" if present
# - theme: travel theme (e.g., culture, food, beach)
# - duration_days: integer number of days (e.g., 5) or null
# - time_expression: a date/month/season phrase from the prompt (e.g., "June", "winter", "next few weeks") or "today" if none given
# - extra: any other constraints (budget, mobility needs) or null

# User input:
# \"\"\"{user_prompt}\"\"\"
# """
#         resp = self.client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=instruction,
#             config=types.GenerateContentConfig(temperature=0.0)
#         )
#         text = resp.text.strip()

#         # try to extract the first JSON object from the model output
#         try:
#             parsed = json.loads(text)
#         except Exception:
#             import re
#             m = re.search(r'(\{.*\})', text, re.S)
#             if m:
#                 parsed = json.loads(m.group(1))
#             else:
#                 # fallback defaults
#                 parsed = {
#                     "place": None,
#                     "theme": "culture",
#                     "duration_days": 5,
#                     "time_expression": "today",
#                     "extra": None
#                 }

#         # normalize defaults
#         if not parsed.get("place"):
#             parsed["place"] = None
#         if not parsed.get("theme"):
#             parsed["theme"] = "culture"
#         if not parsed.get("duration_days"):
#             parsed["duration_days"] = 5
#         if not parsed.get("time_expression"):
#             parsed["time_expression"] = "today"

#         # convert duration to int if possible
#         try:
#             parsed["duration_days"] = int(parsed["duration_days"])
#         except Exception:
#             parsed["duration_days"] = 5

#         return parsed

#     def generate_itinerary(self, user_prompt: str) -> str:
#         """
#         High-level flow:
#         1. parse user prompt -> struct
#         2. get RAG context for place/theme
#         3. get weather summary via weather.get_weather_for_trip(parsed)
#         4. ask Gemini to generate the itinerary using structured fields + RAG + weather
#         Return final textual itinerary that begins with the extracted JSON (for UI).
#         """
#         parsed = self.parse_prompt(user_prompt)

#         # build rag query
#         rag_query = parsed.get("place") or ""
#         if parsed.get("theme"):
#             rag_query = f"{rag_query} {parsed['theme']}".strip()

#         kb_docs = self.rag.search(rag_query, top_k=3)  # list of short doc strings

#         # get weather
#         weather_summary = get_weather_for_trip(parsed)  # dict with summary and details

#         # craft planning prompt
#         plan_prompt = f"""
# You are a helpful travel planner.
# Use the structured trip details below and the knowledge snippets to produce a clear, day-by-day itinerary.

# STRUCTURED DETAILS:
# {json.dumps(parsed, ensure_ascii=False, indent=2)}

# KNOWLEDGE SNIPPETS:
# {json.dumps(kb_docs, ensure_ascii=False, indent=2)}

# WEATHER SUMMARY:
# {json.dumps(weather_summary, ensure_ascii=False, indent=2)}

# TASK:
# - Produce a {parsed['duration_days']}-day itinerary (or suggest 3-5 days if duration missing).
# - For each day include morning/afternoon/evening suggestions, a short reason why the spot fits the theme, and one food suggestion.
# - If weather suggests changes (e.g., rainy days), propose alternatives or moved activities.
# - If the plan could be improved by moving date or choosing a nearby city, offer 1 short alternative and why.

# Return the itinerary as plain text. Start the output with a single JSON line containing 'parsed' and 'weather_summary' for the UI to read.
# """
#         resp = self.client.models.generate_content(
#             model="gemini-2.0-flash-exp",
#             contents=plan_prompt,
#             config=types.GenerateContentConfig(temperature=0.7)
#         )

#         return resp.text.strip()






