import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Travel Planner", layout="wide")

st.title("AI Travel Agent Planner")
st.markdown("*Using Agentic AI & RAG*")

# Sidebar for inputs
st.sidebar.header("Plan Your Trip")

city = st.sidebar.selectbox(
    "Choose your destination:",
    ["Tokyo", "Kyoto", "Paris", "London", "New York"]
)

theme = st.sidebar.selectbox(
    "What interests you most?",
    ["history", "food", "culture", "nature"]
)

days = st.sidebar.slider("How many days?", 1, 10, 3)

# API endpoint - update this when deployed
API_URL = "http://localhost:8000"

if st.sidebar.button("Plan My Trip! 🚀"):
    with st.spinner("AI agents are working on your perfect itinerary..."):
        try:
            response = requests.post(
                f"{API_URL}/plan",
                json={"city": city, "theme": theme, "days": days}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["📋 Itinerary", "🌤️ Travel Info", "🔍 Research Sources"])
                
                with tab1:
                    st.subheader(f"Your {days}-Day {city} Adventure")
                    st.markdown(result.get("enhanced_plan", ""))
                    
                    # Show basic itinerary
                    if "itinerary" in result:
                        st.subheader("Quick Overview")
                        for day, attractions in result["itinerary"].items():
                            st.write(f"**{day}:** {', '.join(attractions)}")
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🌤️ Weather Info")
                        st.info(result.get("weather", "No weather info available"))
                    
                    with col2:
                        st.subheader("👥 Crowd Information")
                        st.warning(result.get("crowd_info", "No crowd info available"))
                
                with tab3:
                    st.subheader("📚 Research Sources")
                    st.markdown("*The AI used these sources from our knowledge base:*")
                    sources = result.get("research_sources", [])
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"{i}. {source}")
            
            else:
                st.error("Failed to get travel plan. Please try again!")
                
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            st.markdown("Make sure your FastAPI server is running!")

# Information section
st.markdown("---")
st.markdown("### 🤖 How This AI Travel Agent Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🔍 Research Agent**
    - Uses RAG to find relevant travel info
    - Searches knowledge base
    - Provides context-aware recommendations
    """)

with col2:
    st.markdown("""
    **📋 Planning Agent**
    - Creates optimized itineraries
    - Considers weather & crowds
    - Integrates multiple data sources
    """)

with col3:
    st.markdown("""
    **🎯 Smart Features**
    - Gemini AI for natural language
    - Real-time information processing
    - Personalized recommendations
    """)