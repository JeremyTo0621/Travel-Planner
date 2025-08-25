import requests
import os
import random
from datetime import datetime

def get_attractions(city, theme):
    """Enhanced attraction finder with more data, might get from real API later"""
    sample_data = {
        "Tokyo": {
            "history": ["Sensoji Temple", "Edo-Tokyo Museum", "Imperial Palace", "Meiji Shrine"],
            "food": ["Tsukiji Market", "Shinjuku Omoide Yokocho", "Ramen Street", "Ginza Food Halls"],
            "culture": ["Harajuku", "Shibuya Crossing", "Tokyo National Museum", "Kabuki Theater"],
            "nature": ["Ueno Park", "Shinjuku Gyoen", "Tokyo Bay", "Mount Takao"]
        },
        "Kyoto": {
            "history": ["Kinkaku-ji", "Fushimi Inari Shrine", "Nijo Castle", "Kiyomizu-dera"],
            "food": ["Nishiki Market", "Kaiseki Restaurant", "Matcha Cafes", "Tofu Cuisine"],
            "culture": ["Gion District", "Bamboo Grove", "Traditional Tea Houses", "Geisha Districts"],
            "nature": ["Philosopher's Path", "Maruyama Park", "Arashiyama", "Temple Gardens"]
        },
        "Paris": {
            "history": ["Louvre", "Notre-Dame", "Versailles", "Arc de Triomphe"],
            "food": ["Local Bistros", "Patisseries", "Wine Bars", "Markets"],
            "culture": ["Montmartre", "Latin Quarter", "Museums", "Opera Houses"],
            "nature": ["Seine River", "Luxembourg Gardens", "Tuileries", "Bois de Boulogne"]
        }
    }
    
    return sample_data.get(city, {}).get(theme, ["Local Attractions", "City Center", "Main Square"])

def optimize_itinerary(attractions, days):
    """Smarter itinerary optimization"""
    if not attractions or days <= 0:
        return {}
    
    random.shuffle(attractions)
    itinerary = {}
    
    # Distribute attractions evenly across days
    attractions_per_day = max(1, len(attractions) // days)
    remainder = len(attractions) % days
    
    start_idx = 0
    for day in range(1, days + 1):
        # Add extra attraction to first 'remainder' days
        day_attractions = attractions_per_day + (1 if day <= remainder else 0)
        end_idx = start_idx + day_attractions
        
        itinerary[f"Day {day}"] = attractions[start_idx:end_idx]
        start_idx = end_idx
    
    return itinerary

def get_weather_info(city):
    """Simulated weather info - replace with real API later"""
    weather_data = {
        "Tokyo": "Mild temperatures, occasional rain. Pack umbrella.",
        "Kyoto": "Pleasant weather, perfect for temple visits.",
        "Paris": "Cool and cloudy, dress in layers."
    }
    return weather_data.get(city, "Check local weather forecast before traveling.")

def get_crowd_info(city):
    """Simulated crowd information, might get from API later"""
    crowd_data = {
        "Tokyo": "Very busy during rush hours (7-9 AM, 5-7 PM). Avoid major attractions on weekends.",
        "Kyoto": "Crowded during cherry blossom season and fall. Early morning visits recommended.",
        "Paris": "Peak tourist season in summer. Book attractions in advance."
    }
    return crowd_data.get(city, "Check local events and peak seasons before visiting.")