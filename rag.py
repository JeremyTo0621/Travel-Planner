import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class TravelRAG:
    def __init__(self, csv_path="Worldwide Travel Cities Dataset (Ratings and Climate).csv"):
        self.csv_path = csv_path
        self.df = None
        self.docs = []
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.load()

    def load(self):
        if not os.path.exists(self.csv_path):
            # fallback docs if csv missing
            self.docs = [
                "Tokyo, Japan - major cultural sites, great food, efficient transport.",
                "Kyoto, Japan - temples, traditional culture, best during cherry blossom and autumn.",
                "Paris, France - museums, cafes, art, lively nightlife.",
                "Bangkok, Thailand - street food, temples, vibrant nightlife."
            ]
            self.df = pd.DataFrame({"city": ["Tokyo","Kyoto","Paris","Bangkok"], "doc": self.docs})
        else:
            self.df = pd.read_csv(self.csv_path)
            self.docs = []
            for _, r in self.df.iterrows():
                parts = [str(r.get("city", "")), str(r.get("country", "")), str(r.get("short_description", ""))]
                self.docs.append(" - ".join([p for p in parts if p]))

        # build embeddings + FAISS index
        embs = self.model.encode(self.docs, convert_to_numpy=True)
        dim = embs.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embs.astype("float32"))

    def search(self, query: str, top_k=1):
        """
        Search FAISS for the closest matching city and return structured info.
        """
        if not query:
            return "No query provided."

        q_emb = self.model.encode([query], convert_to_numpy=True).astype("float32")
        dists, ids = self.index.search(q_emb, top_k)

        if ids[0][0] >= len(self.docs):
            return f"No info found for {query}."

        # get row from dataframe
        row = self.df.iloc[ids[0][0]]

        # build structured summary
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
