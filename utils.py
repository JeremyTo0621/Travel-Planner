import os
import requests
from datetime import datetime
from meteostat import Point, Daily, Monthly
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

geolocator = Nominatim(user_agent="travel_chatbot")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_coordinates(place: str):
    """
    Given a human-readable place name, returns (latitude, longitude) coordinates.
    Uses the Nominatim geocoder service.

    Args:
        place (str): human-readable place name

    Returns:
        tuple or None: (latitude, longitude) if successful; None if not
    """
    geolocator = Nominatim(user_agent="travel_chatbot")
    location = geolocator.geocode(place)
    if location:
        return (location.latitude, location.longitude)
    return None

def get_current_weather(place: str):
    """
    Given a human-readable place name, returns current weather data as a dictionary:
    {
        "source": "openweather",  # source of the weather data
        "summary": "Short text summary of the weather",  # short text summary (e.g. "Sunny, 22°C")
        "details": { ... }  # more detailed weather data from the OpenWeather API
    }

    Args:
        place (str): human-readable place name

    Returns:
        dict or None: if successful, a dictionary with weather data; None if not
    """
    coords = get_coordinates(place)
    if not coords:
        return {"source": "none", "summary": "Could not determine location", "details": {}}

    lat, lon = coords
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()

    return {
        "source": "openweather",
        "summary": f"{data['weather'][0]['description'].capitalize()}, {data['main']['temp']}°C",
        "details": data
    }

def get_historical_weather(place: str, month: int):
    """
    Given a human-readable place name and a month (1-12), returns average temperature for that month as a dictionary:
    {
        "source": "meteostat",  # source of the weather data
        "summary": "Short text summary of the weather",  # short text summary (e.g. "Average temperature 10°C in May (2024)")
        "details": { ... }  # more detailed weather data from the Meteostat API
    }

    Args:
        place (str): human-readable place name
        month (int): month of the year (1-12)

    Returns:
        dict or None: if successful, a dictionary with weather data; None if not
    """
    coords = get_coordinates(place)
    if not coords:
        return {"source": "none", "summary": "Could not determine location", "details": {}}

    lat, lon = coords
    location = Point(lat, lon)
    data = Monthly(location, start=datetime(2024, month, 1), end=datetime(2024, month, 28))
    data = data.fetch()
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_str = months[month - 1]
    if data.empty:
        return {"source": "meteostat", "summary": "No data found", "details": {}}

    avg_temp = round(data["tavg"].mean(), 1)
    return {
        "source": "meteostat",
        "summary": f"Average temperature {avg_temp}°C in month {month_str} (2024)",
        "details": data.to_dict()
    }