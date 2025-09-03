# travel_ui.py
import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")  # default local


st.set_page_config(page_title="Travel Chatbot", layout="wide")
st.title("✈️ Travel Chatbot")

st.markdown(
    "Describe your trip in plain English (e.g. "
    "_'I want a 5 day trip in Japan in June to explore culture.'_ )"
)

with st.form("trip_form", clear_on_submit=False):
    user_message = st.text_area(
        "Your request",
        value="I want a 5 day trip in Japan in June to explore culture",
        height=120,
    )
    submitted = st.form_submit_button("Plan my trip")

if submitted and user_message.strip():
    with st.spinner("Planning your trip..."):
        data = {}
        try:
            resp = requests.post(f"{API_URL}/chat", json={"message": user_message}, timeout=90)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
            data = {}

    # ✅ Check for Gemini quota error
    if data.get("error") and "quota" in data["error"].lower():
        st.warning("⚠️ Gemini API quota exceeded. Please try again later.")
    elif not data:
        st.error("⚠️ No response from the chatbot.")
    else:
        tab1, tab2, tab3 = st.tabs(["📋 Itinerary", "🌤️ Weather & Locations", "🔎 Prompt Analysis"])

        with tab1:
            st.subheader("Itinerary")
            itinerary = data.get("itinerary") or "_No itinerary generated._"
            st.markdown(itinerary)

        with tab2:
            st.subheader("Weather & Location Overview")

            weather = data.get("weather", {}) or {}
            st.markdown("**Weather summary:** " + weather.get("summary", "N/A"))

            meta_cols = st.columns(3)
            with meta_cols[0]:
                st.caption("Source")
                st.write(weather.get("source", "N/A"))
            with meta_cols[1]:
                if "details" in weather and isinstance(weather["details"], dict):
                    main = weather["details"].get("main") if isinstance(weather["details"].get("main"), dict) else None
                    temp = main.get("temp") if main else None
                    if temp is not None:
                        st.caption("Current Temp (°C)")
                        st.write(temp)
            with meta_cols[2]:
                coord = weather.get("details", {}).get("coord", {})
                if coord:
                    st.caption("Coordinates")
                    st.write(f"{coord.get('lat')}, {coord.get('lon')}")

            st.markdown("---")
            st.subheader("Location Overview")
            st.markdown(data.get("rag_summary", "_No location data._"))

        with tab3:
            st.subheader("Prompt Analysis (How your request was understood)")
            parsed = data.get("parsed_prompt") or data.get("details") or {}
            st.json(parsed)

            st.subheader("Full RAG Context (raw)")
            st.text_area("Raw RAG Info", data.get("rag_info_raw", ""), height=250)
