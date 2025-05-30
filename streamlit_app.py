import streamlit as st
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="AI Hotel Advisor",
    page_icon="🏨",
    layout="wide"
)

# App header
st.title("🏨 AI Hotel Advisor")
st.markdown("Find the perfect hotel for your stay based on your preferences.")

def get_user_preferences():
    """Get user preferences from the sidebar."""
    with st.sidebar:
        st.header("Your Preferences")
        
        # Location input
        hotel_location = st.text_input("Destination", value="İstanbul")
        
        # Price range
        hotel_daily_price = st.slider("Maximum Daily Price (TL)", 
                                 min_value=100, 
                                 max_value=5000, 
                                 value=500,
                                 step=100)
        
        # Trip duration
        trip_duration_days = st.slider("Trip Duration (Days)", 
                                  min_value=1, 
                                  max_value=30, 
                                  value=5)
        trip_duration = f"{trip_duration_days} days"
        
        # Group composition
        col1, col2 = st.columns(2)
        with col1:
            adults = st.number_input("Adults", min_value=1, max_value=10, value=2)
        with col2:
            children = st.number_input("Children", min_value=0, max_value=10, value=1)
        
        personal_information = f"{adults} adults, {children} children"
        
        # User interests
        interest_options = [
            "Historical sites", 
            "Family-friendly", 
            "Beach", 
            "Nightlife", 
            "Shopping", 
            "Cultural experiences",
            "Nature",
            "Business travel"
        ]
        
        user_interests = st.multiselect(
            "Your Interests", 
            options=interest_options,
            default=["Historical sites", "Family-friendly"]
        )
        
        user_interest = ", ".join(user_interests)
        
        # Search button
        search_button = st.button("Find Hotels", type="primary", use_container_width=True)
    
    return {
        'hotel_location': hotel_location,
        'hotel_daily_price': hotel_daily_price,
        'trip_duration': trip_duration,
        'personal_information': personal_information,
        'user_interest': user_interest,
        'search_button': search_button
    }

def search_hotels(prefs):
    """Search for hotels based on user preferences."""
    st.session_state.is_loading = True
    
    inputs = {
        "hotel_location": prefs['hotel_location'],
        "hotel_daily_price": str(prefs['hotel_daily_price']),
        "trip_duration": prefs['trip_duration'],
        "personal_information": prefs['personal_information'],
        "user_interest": prefs['user_interest']
    }
    
    with st.spinner("🔍 Our AI agents are searching for the best hotels for you..."):
        try:
            # Import here to avoid the import error at startup time
            from agent.my_crew import AIHotelAdvisor
            
            # Call the AI Hotel Advisor crew
            result = AIHotelAdvisor().crew().kickoff(inputs=inputs)
            
            # Handle different result formats
            if isinstance(result, str):
                try:
                    # Sometimes CrewAI returns JSON strings
                    result_data = json.loads(result)
                    if "recommended_hotels" in result_data:
                        st.session_state.hotel_results = result_data["recommended_hotels"]
                    else:
                        st.session_state.hotel_results = result_data
                except json.JSONDecodeError:
                    # Handle raw string output
                    st.session_state.hotel_results = result
            else:
                # Handle structured output
                st.session_state.hotel_results = result
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            import traceback
            st.code(traceback.format_exc(), language="python")
            st.session_state.hotel_results = None
    
    st.session_state.is_loading = False

def display_hotels():
    """Display the hotel results in a user-friendly format."""
    if not st.session_state.hotel_results:
        return
        
    st.header("🌟 Recommended Hotels")
    
    results = st.session_state.hotel_results
    
    # Function to safely get a value from dictionary with default
    def get_value(data, key, default="N/A"):
        value = data.get(key, default)
        return value if value not in [None, "", "N/A"] else default
    
    # Handle different result formats
    if isinstance(results, str):
        try:
            parsed_results = json.loads(results)
            if isinstance(parsed_results, list):
                results = parsed_results
            elif "recommended_hotels" in parsed_results:
                results = parsed_results["recommended_hotels"]
            else:
                st.warning("No hotel data found in the response.")
                st.write(results)
                return
        except json.JSONDecodeError:
            st.warning("Unable to parse the response. Showing raw output:")
            st.write(results)
            return
    
    
    if isinstance(results, list) and results:
        for i, hotel in enumerate(results):
            with st.container():
                st.markdown(f"### {i+1}. {get_value(hotel, 'hotel_name', 'Hotel')}")
                
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    
                    st.markdown(f"**Location:** {get_value(hotel, 'hotel_location')}")
                    st.markdown(f"**Price:** {get_value(hotel, 'hotel_daily_price')} TL/night")
                    st.markdown(f"**Rating:** {get_value(hotel, 'review_score')}/10")
                    
                    
                    if 'description' in hotel:
                        st.markdown("---")
                        st.markdown(get_value(hotel, 'description'))
                
                with col2:
                    
                    if 'image_url' in hotel:
                        st.image(hotel['image_url'], use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=Hotel+Image", 
                               use_column_width=True)
                
                n
                st.markdown("---")
                st.markdown("#### 🏨 Amenities")
                
                
                amenities = hotel.get('benefits', [])
                if amenities and isinstance(amenities, list):
                    cols = st.columns(4)  # 4 columns for amenities
                    for idx, amenity in enumerate(amenities):
                        cols[idx % 4].markdown(f"✓ {amenity}")
                
                # Certificates and accessibility features
                certs = hotel.get('hotel_certificates', [])
                if certs and isinstance(certs, list):
                    st.markdown("#### 🏆 Certifications")
                    st.markdown(", ".join([f"`{cert}`" for cert in certs]))
                
                access = hotel.get('accessibility_features', [])
                if access and isinstance(access, list):
                    st.markdown("#### ♿ Accessibility Features")
                    st.markdown(", ".join([f"`{feature}`" for feature in access]))
                
                # Add space between hotels
                st.markdown("")
                st.markdown("---")
                st.markdown("")
    
    elif not results:
        st.warning("No hotels found matching your criteria. Please try adjusting your search.")
    else:
        st.warning("Unexpected response format. Please try again.")
        st.json(results)

# Main application flow
def main():
   
    if 'hotel_results' not in st.session_state:
        st.session_state.hotel_results = None
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False
    
    # Get user preferences from the sidebar
    prefs = get_user_preferences()
    
    # Trigger search on button click
    if prefs['search_button']:
        search_hotels(prefs)
    
    # Display loading indicator
    if st.session_state.is_loading:
        st.info("Searching for hotels... This may take a few minutes.")
    
    # Display results or initial instructions
    if st.session_state.hotel_results:
        display_hotels()
    elif not st.session_state.is_loading:
        st.info("👈 Set your preferences in the sidebar and click 'Find Hotels' to get personalized hotel recommendations.")

if __name__ == "__main__":
    main()
