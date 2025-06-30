import streamlit as st
import json
import re
from typing import Dict, List, Any


st.set_page_config(
    page_title="AI Hotel Advisor",
    page_icon="🏨",
    layout="wide"
)

def parse_hotel_result(result):
    """Parse the hotel advisor result and extract hotel information"""
    hotels = []
    
    try:
        if hasattr(result, 'pydantic'):
            pydantic_result = result.pydantic
            if hasattr(pydantic_result, 'recommended_hotels'):
                for hotel in pydantic_result.recommended_hotels:
                    if hasattr(hotel, 'dict'):
                        hotels.append(hotel.dict())
                    elif hasattr(hotel, 'model_dump'):
                        hotels.append(hotel.model_dump())
                    else:
                        hotel_dict = {}
                        for field in hotel.__fields__:
                            hotel_dict[field] = getattr(hotel, field, None)
                        hotels.append(hotel_dict)
                return hotels
        
        elif hasattr(result, 'raw'):
            return parse_hotel_result(result.raw)
        
        elif isinstance(result, str):
            if 'recommended_hotels=' in result:
                start_idx = result.find('recommended_hotels=')
                if start_idx != -1:
                    hotels_str = result[start_idx + len('recommended_hotels='):]
                    
                    bracket_count = 0
                    end_idx = 0
                    for i, char in enumerate(hotels_str):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx > 0:
                        hotels_str = hotels_str[:end_idx]
                        
                        hotel_pattern = r"HotelInfo\(([^)]+(?:\)[^)]*)*)\)"
                        matches = re.findall(hotel_pattern, hotels_str)
                        
                        for match in matches:
                            hotel_data = parse_hotel_info_string(match)
                            if hotel_data:
                                hotels.append(hotel_data)
        
        elif isinstance(result, dict):
            if "recommended_hotels" in result:
                hotels_data = result["recommended_hotels"]
                if isinstance(hotels_data, list):
                    for hotel in hotels_data:
                        if hasattr(hotel, 'dict'):
                            hotels.append(hotel.dict())
                        elif hasattr(hotel, 'model_dump'):
                            hotels.append(hotel.model_dump())
                        elif isinstance(hotel, dict):
                            hotels.append(hotel)
                        else:
                            hotel_dict = {}
                            for attr in dir(hotel):
                                if not attr.startswith('_') and not callable(getattr(hotel, attr)):
                                    hotel_dict[attr] = getattr(hotel, attr)
                            hotels.append(hotel_dict)
                else:
                    hotels = [hotels_data]
            else:
                hotels = [result]
        
        elif isinstance(result, list):
            hotels = result
        
        return hotels
    
    except Exception as e:
        st.error(f"Sonuç parse edilirken hata: {e}")
        st.code(f"Hata detayı: {str(e)}")
        return []

def parse_hotel_info_string(hotel_str):
    """Parse a single HotelInfo string into a dictionary"""
    hotel_data = {}
    
    try:
        parts = []
        current_part = ""
        bracket_count = 0
        quote_count = 0
        
        for char in hotel_str:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == "'":
                quote_count = (quote_count + 1) % 2
            elif char == ',' and bracket_count == 0 and quote_count == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.startswith('[') and value.endswith(']'):
                    list_content = value[1:-1]
                    if list_content:
                        items = []
                        current_item = ""
                        in_quotes = False
                        
                        for char in list_content:
                            if char == "'" and (not current_item or current_item[-1] != '\\'):
                                in_quotes = not in_quotes
                            elif char == ',' and not in_quotes:
                                if current_item.strip():
                                    items.append(current_item.strip().strip("'"))
                                current_item = ""
                            else:
                                current_item += char
                        
                        if current_item.strip():
                            items.append(current_item.strip().strip("'"))
                        
                        value = items
                    else:
                        value = []
                elif value.replace('.', '').isdigit():
                    value = float(value) if '.' in value else int(value)
                
                hotel_data[key] = value
        
        return hotel_data
    
    except Exception as e:
        st.error(f"Hotel string parse hatası: {e}")
        return {}

def display_hotel_card(hotel, index):
    """Display a single hotel as a card"""
    
    hotel_name = hotel.get('hotel_name', f'Otel {index}')
    location = hotel.get('hotel_location', 'Konum belirtilmemiş')
    price = hotel.get('hotel_daily_price', 'Fiyat belirtilmemiş')
    certificates = hotel.get('hotel_certificates', [])
    accessibility = hotel.get('accessibility_features', [])
    benefits = hotel.get('benefits', [])
    review_score = hotel.get('review_score', 'N/A')
    
    # Create a card-like container
    with st.container():
        st.markdown("---")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(f"🏨 {hotel_name}")
            st.write(f"📍 **Konum:** {location}")
        
        with col2:
            if isinstance(price, (int, float)):
                st.metric("💰 Günlük Fiyat", f"${price}")
            else:
                st.metric("💰 Günlük Fiyat", str(price))
        
        with col3:
            if review_score != 'N/A':
                st.metric("⭐ Puan", f"{review_score}/10")
            else:
                st.metric("⭐ Puan", "Değerlendirme yok")
        
        # Details row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if benefits:
                st.write("**🎯 Otel İmkanları:**")
                for benefit in benefits[:5]:  
                    st.write(f"✅ {benefit}")
                if len(benefits) > 5:
                    st.write(f"... ve {len(benefits) - 5} imkan daha")
        
        with col2:
            if accessibility:
                st.write("**♿ Erişilebilirlik:**")
                for feature in accessibility[:4]: 
                    st.write(f"✅ {feature}")
                if len(accessibility) > 4:
                    st.write(f"... ve {len(accessibility) - 4} özellik daha")
        
        with col3:
            if certificates:
                st.write("**📜 Sertifikalar:**")
                for cert in certificates[:3]: 
                    st.write(f"🏆 {cert}")
                if len(certificates) > 3:
                    st.write(f"... ve {len(certificates) - 3} sertifika daha")

def main():
    st.title("🏨 AI Hotel Advisor")
    st.write("Yapay zeka destekli otel önerisi alın")
    
    st.sidebar.header("Arama Kriterleri")
    
    location = st.sidebar.text_input("Şehir", value="İstanbul")
    budget = st.sidebar.number_input("Günlük Bütçe (TL)", min_value=50, max_value=5000, value=500)
    duration = st.sidebar.text_input("Kalış Süresi", value="5 gün")
    guests = st.sidebar.text_input("Misafir Bilgisi", value="2 yetişkin, 1 çocuk")
    interests = st.sidebar.text_area("İlgi Alanları", value="Tarihi yerler, aile dostu")
    search_button = st.sidebar.button("Otel Ara", type="primary")
    
    # Main content
    if search_button:
        if location and budget and duration and guests:
            with st.spinner("Oteller araştırılıyor..."):
                inputs = {
                    "hotel_location": location,
                    "hotel_daily_price": str(budget),
                    "trip_duration": duration,
                    "personal_information": guests,
                    "user_interest": interests
                }
                
                try:
                    result = run_hotel_advisor(inputs)
                    
                    if result:
                        hotels = parse_hotel_result(result)
                        
                        if hotels:
                            st.success(f"🎉 {len(hotels)} otel bulundu!")
                            
                            st.info(f"📍 **{location}** şehrinde **₺{budget}** bütçe ile **{duration}** için **{guests}** misafir sayısına uygun oteller")

                            st.header("🏨 Önerilen Oteller")
                            
                            try:
                                hotels_sorted = sorted(hotels, key=lambda x: float(x.get('hotel_daily_price', 999999)))
                            except:
                                hotels_sorted = hotels
                            
                            for i, hotel in enumerate(hotels_sorted, 1):
                                display_hotel_card(hotel, i)
                        
                        else:
                            st.warning("⚠️ Otel bilgileri parse edilemedi.")
                            
                            st.write("**Debug Bilgisi:**")
                            st.write(f"Result türü: {type(result)}")
                            
                            if hasattr(result, '__dict__'):
                                st.write("Result attributes:")
                                for attr in dir(result):
                                    if not attr.startswith('_'):
                                        try:
                                            value = getattr(result, attr)
                                            if not callable(value):
                                                st.write(f"- {attr}: {type(value)}")
                                        except:
                                            pass
                            
                            st.write("**Ham Sonuç:**")
                            with st.expander("Detayları Göster"):
                                st.code(str(result))
                    
                    else:
                        st.error("❌ Otel araması başarısız oldu.")
                
                except Exception as e:
                    st.error(f"❌ Hata oluştu: {str(e)}")
                    with st.expander("Hata Detayları"):
                        st.code(str(e))
        else:
            st.warning("⚠️ Lütfen tüm alanları doldurun.")
    
    else:
        st.info("👈 Sol menüden arama kriterlerinizi girin ve 'Otel Ara' butonuna tıklayın.")
        

def run_hotel_advisor(inputs):
    """Run hotel advisor with inputs"""
    try:
        from agent.my_crew import AIHotelAdvisor
        advisor = AIHotelAdvisor()
        st.write(f"📍 Aranan şehir: {inputs['hotel_location']}")
        st.write(f"💰 Bütçe: {inputs['hotel_daily_price']} TL")
        
        result = advisor.crew().kickoff(inputs=inputs)
        
        st.write("✅ Arama tamamlandı!")
        return result
        
    except ImportError as e:
        st.error(f"Import hatası: {e}")
        return None
    except Exception as e:
        st.error(f"Crew hatası: {e}")
        st.write("Hata detayları:")
        st.code(str(e))
        return None

if __name__ == "__main__":
    main()