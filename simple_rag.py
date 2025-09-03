import os
import pandas as pd
import random

class TravelRAG:
    def __init__(self, csv_path="cities.csv"):
        """
        Simplified TravelRAG without sentence_transformers or FAISS.
        Uses basic keyword matching to return city info.
        """
        self.csv_path = csv_path
        self.df = None
        self.docs = []
        self.load()

    def load(self):
        """
        Load the CSV file or fallback to a default list of cities.
        """
        if not os.path.exists(self.csv_path):
            # fallback docs if CSV missing
            self.df = pd.DataFrame({
                "city": ["Tokyo","Kyoto","Paris","Bangkok"],
                "country": ["Japan","Japan","France","Thailand"],
                "short_description": [
                    "major cultural sites, great food, efficient transport",
                    "temples, traditional culture, best during cherry blossom and autumn",
                    "museums, cafes, art, lively nightlife",
                    "street food, temples, vibrant nightlife"
                ],
                "region": ["Kanto","Kansai","Ile-de-France","Central Thailand"],
                "avg_temp_monthly": ["10-25°C","8-27°C","5-20°C","25-32°C"],
                "budget_level": ["$$$","$$","$$$","$"],
                "ideal_durations": ["5-7 days","3-5 days","4-6 days","3-5 days"],
                "culture":[5,5,5,4],
                "adventure":[3,2,3,4],
                "nature":[3,3,4,3],
                "beaches":[1,1,2,4],
                "nightlife":[4,3,5,5],
                "cuisine":[5,5,5,5],
                "wellness":[3,3,4,3],
                "urban":[5,4,5,4],
                "seclusion":[1,2,1,1]
            })
        else:
            self.df = pd.read_csv(self.csv_path)
        
        # build a list of combined lowercase descriptions for matching
        self.df['combined'] = (
            self.df['city'].astype(str) + " " +
            self.df['country'].astype(str) + " " +
            self.df.get('short_description', '').astype(str)
        ).str.lower()

    def search(self, query: str, top_k=1):
        """
        Simple keyword matching search to replace FAISS.
        Returns structured summary in same format as original.
        """
        if not query:
            return "No query provided."

        query_words = query.lower().split()
        matches = []

        for idx, row in self.df.iterrows():
            text = row['combined']
            if any(word in text for word in query_words):
                matches.append(idx)

        if not matches:
            # fallback: just return random top_k rows
            matches = random.sample(range(len(self.df)), min(top_k, len(self.df)))

        # pick top match
        row = self.df.iloc[matches[0]]

        summary = f"""
                📍 City: {row.get('city','N/A')}, {row.get('country','N/A')} ({row.get('region','N/A')})
                🌍 Overview: {row.get('short_description','N/A')}
                🌡️ Avg Monthly Temps: {row.get('avg_temp_monthly','N/A')}
                💰 Budget: {row.get('budget_level','N/A')}
                🗓️ Ideal Durations: {row.get('ideal_durations','N/A')}

                🏖️ Themes (1–5 scale):
                - Culture: {row.get('culture','N/A')}
                - Adventure: {row.get('adventure','N/A')}
                - Nature: {row.get('nature','N/A')}
                - Beaches: {row.get('beaches','N/A')}
                - Nightlife: {row.get('nightlife','N/A')}
                - Cuisine: {row.get('cuisine','N/A')}
                - Wellness: {row.get('wellness','N/A')}
                - Urban: {row.get('urban','N/A')}
                - Seclusion: {row.get('seclusion','N/A')}
                """
        return summary.strip()
