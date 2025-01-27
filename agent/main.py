from my_crew import AIHotelAdvisor


def run():
    
    inputs = {
        "hotel_location": "İstanbul",
        "hotel_daily_price": "500",
        "trip_duration": "5 days",
        "personal_information": "2 adults, 1 child",
        "user_interest": "Historical sites, family-friendly"

    }
    
    result = AIHotelAdvisor().crew().kickoff(inputs=inputs)
    print(result)
    
if __name__ == "__main__":
    run()