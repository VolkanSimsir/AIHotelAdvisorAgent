from my_crew import AIHotelAdvisor

def run():
    print("AI Hotel Advisor başlatılıyor...")
    
    inputs = {
        "hotel_location": "İstanbul",
        "hotel_daily_price": "500",
        "trip_duration": "5 gün",
        "personal_information": "2 yetişkin, 1 çocuk",
        "user_interest": "Tarihi yerler, aile dostu"
    }
    
    print(f"Arama kriterleri:")
    for key, value in inputs.items():
        print(f"  {key}: {value}")
    
    try:
        print("\nOtel arama süreci başlıyor...")
        advisor = AIHotelAdvisor()
        print("Crew oluşturuldu, arama başlatılıyor...")
        
        result = advisor.crew().kickoff(inputs=inputs)
        
        print("\n" + "="*50)
        print("SONUÇLAR:")
        print("="*50)
        print(result)
        print("="*50)
        
        return result
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = run()
    if result:
        print("Arama başarıyla tamamlandı!")
    else:
        print("Arama başarısız!")