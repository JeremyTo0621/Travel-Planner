import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class TravelRAG:
    def __init__(self, csv_path="Worldwide Travel Cities Dataset (Ratings and Climate).csv"):
        """
        Constructor for TravelRAG.

        Args:
            csv_path (str, optional): Path to the Worldwide Travel Cities Dataset (Ratings and Climate).csv file. Defaults to "Worldwide Travel Cities Dataset (Ratings and Climate).csv".

        The constructor loads the Worldwide Travel Cities Dataset (Ratings and Climate).csv file into a pandas data frame, and initializes the
        SentenceTransformer model and the Faiss index. The load() method is called at the end of the constructor to load the data into the model and
        index.

        If the csv_path is not provided, a fallback list of documents is used instead.
        """
        self.csv_path = csv_path
        self.df = None
        self.docs = []
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.load()

    def load(self):
        """
        Load the Worldwide Travel Cities Dataset (Ratings and Climate).csv file into a pandas data frame, and initialize the SentenceTransformer model and
        the Faiss index. If the csv_path is not provided or does not exist, a fallback list of documents is used instead.

        The method reads the csv file into a pandas data frame, constructs a list of short descriptions for each city, and uses the SentenceTransformer model
        to encode the descriptions into embeddings. The embeddings are then added to the Faiss index.

        If the csv_path does not exist, the method uses a fallback list of documents instead. The fallback list contains four cities: Tokyo, Kyoto, Paris, and
        Bangkok, with short descriptions for each city. The fallback list is used to initialize the SentenceTransformer model and the Faiss index.

        Args:
            None

        Returns:
            None
        """
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

        The method takes a query string (e.g. "Tokyo Japan") and returns a dict with the following keys:
        - city: the closest matching city
        - country: the country the city is in
        - short_description: a short description of the city
        - climate: a short description of the climate in the city
        - rating: the average rating of the city from the dataset
        - lat: the latitude of the city
        - lon: the longitude of the city

        If the query does not match any city, the method returns a message indicating that no info was found.
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
