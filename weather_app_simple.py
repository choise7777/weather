import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import os
from pathlib import Path

# API ??ë³´ì•ˆ ë¡œë”©
try:
    # Streamlit Secrets?ì„œ API ??ë¡œë”© (?°ì„ ?œìœ„ 1)
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (KeyError, FileNotFoundError):
    try:
        # .env ?Œì¼?ì„œ ?˜ê²½ë³€??ë¡œë”© ?œë„ (?°ì„ ?œìœ„ 2)
        from dotenv import load_dotenv
        load_dotenv()
        API_KEY = os.getenv('OPENWEATHER_API_KEY')
        
        # .env ?Œì¼???†ìœ¼ë©?config.py?ì„œ ë¡œë”©
        if not API_KEY:
            from config import OPENWEATHER_API_KEY
            API_KEY = OPENWEATHER_API_KEY
    except (ImportError, ModuleNotFoundError):
        try:
            # config.py?ì„œ ì§ì ‘ ë¡œë”© (?°ì„ ?œìœ„ 3)
            from config import OPENWEATHER_API_KEY
            API_KEY = OPENWEATHER_API_KEY
        except (ImportError, ModuleNotFoundError):
            # ë§ˆì?ë§??˜ë‹¨?¼ë¡œ ?˜ë“œì½”ë”©?????¬ìš© (ê°œë°œ??
            API_KEY = "14e3fc348b3e11a20c23806f1c3be844"
            st.warning("? ï¸ API ?¤ê? ë³´ì•ˆ ?Œì¼?ì„œ ë¡œë”©?˜ì? ?Šì•˜?µë‹ˆ?? secrets.toml ?ëŠ” config.py ?Œì¼???•ì¸?˜ì„¸??")

def get_detailed_address(latitude, longitude):
    """Nominatim APIë¥??¬ìš©??ì¢Œí‘œë¡œë????ì„¸ ì£¼ì†Œ ?•ë³´ ?ë“"""
    try:
        # Nominatim API (OpenStreetMap??ë¬´ë£Œ ì§€?¤ì½”???œë¹„??
        nominatim_url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'accept-language': 'ko,en',  # ?œêµ­???°ì„ , ?ì–´ fallback
            'zoom': 18  # ?ì„¸??ì£¼ì†Œ ?•ë³´ ?”ì²­
        }
        
        headers = {
            'User-Agent': 'WeatherApp/1.0 (contact@example.com)'  # Nominatim ?•ì±…???„ìˆ˜
        }
        
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # ì£¼ì†Œ ?•ë³´ ?Œì‹±
            address = data.get('address', {})
            display_name = data.get('display_name', '')
            
            # ?œêµ­ ì£¼ì†Œ ì²´ê³„??ë§ê²Œ ?•ë³´ ì¶”ì¶œ
            location_info = {
                'country': address.get('country', ''),
                'state': address.get('state', ''),  # ????
                'city': address.get('city', '') or address.get('county', ''),  # ??êµ?
                'district': address.get('district', '') or address.get('borough', ''),  # êµ?
                'neighbourhood': address.get('neighbourhood', '') or address.get('suburb', ''),  # ??ë©?
                'road': address.get('road', ''),  # ?„ë¡œëª?
                'house_number': address.get('house_number', ''),
                'full_address': display_name
            }
            
            # ?œêµ­??ì£¼ì†Œ ?¬ë§·??
            formatted_parts = []
            
            if location_info['country']:
                formatted_parts.append(location_info['country'])
            if location_info['state']:
                formatted_parts.append(location_info['state'])
            if location_info['city']:
                formatted_parts.append(location_info['city'])
            if location_info['district']:
                formatted_parts.append(location_info['district'])
            if location_info['neighbourhood']:
                formatted_parts.append(location_info['neighbourhood'])
                
            location_info['formatted_address'] = ' '.join(formatted_parts)
            
            return location_info
            
    except Exception as e:
        print(f"Nominatim API ?¤ë¥˜: {e}")
        return None
    
    return None

def get_ootd_recommendation(feels_like, weather_main):
    """
    ì²´ê° ?¨ë„?€ ? ì”¨ ?íƒœ???°ë¼ ?·ì°¨ë¦¼ì„ ì¶”ì²œ?˜ëŠ” ?¨ìˆ˜ (?°ì´??ì²˜ë¦¬)
    'level'??ì¶”ê??˜ì—¬ ê¸°ì˜¨ ?¨ê³„ë¥?ë¹„êµ?????ˆê²Œ ??
    """
    
    if feels_like > 27:
        rec = {
            "level": 8,  # ?¥ë‹¤
            "summary": "?¥µ ë§¤ìš° ?”ì?",
            "items": "ë¯¼ì†Œë§? ë°˜íŒ”, ë°˜ë°”ì§€, ë¦°ë„¨, ?í”¼??,
            "image_path": "images/ootd_hot.png"
        }
    elif 23 <= feels_like <= 27:
        rec = {
            "level": 7,
            "summary": "?˜ ?”ì?",
            "items": "ë°˜íŒ”, ?‡ì? ?”ì¸ , ë°˜ë°”ì§€, ë©´ë°”ì§€",
            "image_path": "images/ootd_warm.png"
        }
    elif 20 <= feels_like <= 22:
        rec = {
            "level": 6,
            "summary": "?™‚ ì¾Œì ??,
            "items": "?‡ì? ê°€?”ê±´, ê¸´íŒ” ?”ì¸ , ë©´ë°”ì§€, ì²?°”ì§€",
            "image_path": "images/ootd_mild.png"
        }
    elif 17 <= feels_like <= 19:
        rec = {
            "level": 5,
            "summary": "?‘ ? ì„ ??,
            "items": "ë§¨íˆ¬ë§? ?„ë“œ?? ?‡ì? ?ˆíŠ¸, ì²?°”ì§€",
            "image_path": "images/ootd_cool.png"
        }
    elif 12 <= feels_like <= 16:
        rec = {
            "level": 4,
            "summary": "?§¥ ?€?€??,
            "items": "?ì¼“, ê°€?”ê±´, ?ˆíŠ¸, ?¤í??? ê¸°ëª¨ ë°”ì?",
            "image_path": "images/ootd_chilly.png"
        }
    elif 9 <= feels_like <= 11:
        rec = {
            "level": 3,
            "summary": "?¥¶ ì¶”ì?",
            "items": "?¸ë Œì¹?ì½”íŠ¸, ?¼ìƒ, ?ˆíŠ¸, ?ˆíŠ¸??,
            "image_path": "images/ootd_cold.png"
        }
    elif 5 <= feels_like <= 8:
        rec = {
            "level": 2,
            "summary": "?„ï¸ ë§¤ìš° ì¶”ì?",
            "items": "??ì½”íŠ¸, ê°€ì£??ì¼“, ëª©ë„ë¦? ê¸°ëª¨",
            "image_path": "images/ootd_very_cold.png"
        }
    else:  # 5??ë¯¸ë§Œ
        rec = {
            "level": 1,
            "summary": "?¥¶?¥¶ ?œíŒŒ",
            "items": "?¨ë”©, ?êº¼??ì½”íŠ¸, ?´ë³µ, ëª©ë„ë¦? ?¥ê°‘",
            "image_path": "images/ootd_freezing.png"
        }

    # ? ì”¨ë³??¡ì„¸?œë¦¬ ì¶”ì²œ
    accessory_rec = ""
    if weather_main == "Rain":
        accessory_rec = "???°ì‚°??ê¼?ì±™ê¸°?¸ìš”! ë°©ìˆ˜ ? ë°œ??ì¢‹ìŠµ?ˆë‹¤."
    elif weather_main == "Snow":
        accessory_rec = "?„ï¸ ë¯¸ë„??ë°©ì? ? ë°œê³??¥ê°‘??ì¤€ë¹„í•˜?¸ìš”."
    elif weather_main == "Thunderstorm":
        accessory_rec = "???°ì‚°ê³?ë°©ìˆ˜ ?¸íˆ¬ë¥?ì±™ê¸°?¸ìš”."
    elif weather_main == "Drizzle":
        accessory_rec = "?Œ¦ï¸?ê°€ë²¼ìš´ ?°ì‚°?´ë‚˜ ?„ë“œë¥?ì¤€ë¹„í•˜?¸ìš”."
    elif weather_main == "Mist" or weather_main == "Fog":
        accessory_rec = "?Œ«ï¸??œì•¼ ?•ë³´ë¥??„í•´ ë°ì? ???·ì„ ê¶Œí•©?ˆë‹¤."
    elif weather_main == "Clear" and feels_like > 25:
        accessory_rec = "?•¶ï¸?? ê??¼ìŠ¤?€ ?ì™¸??ì°¨ë‹¨?œë? ì¤€ë¹„í•˜?¸ìš”."
    elif weather_main == "Clouds" and feels_like < 15:
        accessory_rec = "?ï¸ ì²´ì˜¨ ? ì?ë¥??„í•´ ëª©ë„ë¦¬ë? ì±™ê¸°?¸ìš”."
    
    return rec, accessory_rec

def set_background(weather_main):
    """? ì”¨ ?íƒœ???°ë¼ ?™ì  ë°°ê²½?”ë©´ ?¤ì •"""
    # ? ì”¨ ?íƒœ???°ë¼ ?¤ë¥¸ ?´ë?ì§€ URL??ë§¤í•‘
    if weather_main == "Clear":
        bg_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # ë§‘ì? ?˜ëŠ˜
    elif weather_main == "Rain":
        bg_url = "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2127&q=80"  # ë¹??¤ëŠ” ì°½ë¬¸
    elif weather_main == "Snow":
        bg_url = "https://images.unsplash.com/photo-1548777123-93d6ac74e765?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # ???´ë¦¬???ê²½
    elif weather_main == "Clouds":
        bg_url = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2051&q=80"  # ?ë¦° ?˜ëŠ˜
    elif weather_main == "Thunderstorm":
        bg_url = "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2071&q=80"  # ë²ˆê°œ/ì²œë‘¥
    elif weather_main == "Drizzle":
        bg_url = "https://images.unsplash.com/photo-1541919329513-35f7af297129?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # ?´ìŠ¬ë¹?
    elif weather_main == "Mist" or weather_main == "Fog":
        bg_url = "https://images.unsplash.com/photo-1487621167305-5d248087c724?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2132&q=80"  # ?ˆê°œ ?€ ?ê²½
    else:
        bg_url = "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # ê¸°ë³¸ ?˜ëŠ˜ ?´ë?ì§€

    # CSSë¥?HTMLë¡?ì£¼ì…
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        
        /* ?„ì²´ ??ì»¨í…Œ?´ë„ˆ??ê°•í•œ ë°˜íˆ¬ëª?ë°°ê²½ */
        .stApp > div:first-child {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
            min-height: 100vh;
        }}
        
        /* ë©”ì¸ ì»¨í…Œ?´ë„ˆ ë°°ê²½ ê°•í™” */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.98) !important;
            padding: 2rem 1rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            backdrop-filter: blur(15px);
        }}
        
        /* ë©”íŠ¸ë¦?ì¹´ë“œ ?¤í???ê°œì„  */
        div[data-testid="metric-container"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid rgba(200, 200, 200, 0.5);
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        /* ë©”íŠ¸ë¦??ìŠ¤??ê°•í™” */
        div[data-testid="metric-container"] * {{
            color: #333333 !important;
            font-weight: 600 !important;
        }}
        
        /* ?•ì¥ ê°€?¥í•œ ?¹ì…˜ ?¤í???*/
        div[data-testid="stExpander"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 12px;
            border: 1px solid rgba(200, 200, 200, 0.5);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        /* ???¤í???ê°œì„  */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 5px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            margin: 2px;
        }}
        
        /* ë²„íŠ¼ ?¤í???ê°œì„  */
        .stButton > button {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #333333 !important;
            border: 2px solid rgba(103, 126, 234, 0.8) !important;
            font-weight: 600 !important;
        }}
        
        .stButton > button:hover {{
            background-color: rgba(103, 126, 234, 0.9) !important;
            color: white !important;
        }}
        
        /* ?…ë ¥ ?„ë“œ ?¤í???ê°œì„  */
        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #333333 !important;
            border: 2px solid rgba(200, 200, 200, 0.7) !important;
        }}
        
        /* ?«ì ?…ë ¥ ?„ë“œ ?¤í???ê°œì„  */
        .stNumberInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #333333 !important;
            border: 2px solid rgba(200, 200, 200, 0.7) !important;
        }}
        
        /* ?°ì´?°í”„?ˆì„ ?¤í???ê°œì„  */
        .stDataFrame {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        /* ì°¨íŠ¸ ë°°ê²½ ê°œì„  */
        .stPlotlyChart {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px;
            padding: 10px;
        }}
        
        /* ?¼ë°˜ ?ìŠ¤??ê°€?…ì„± ?¥ìƒ */
        .stMarkdown, .stText, p, div {{
            color: #333333 !important;
        }}
        
        /* ?œëª© ?¤í???ê°•í™” */
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50 !important;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# OpenWeather API ?¤ì •
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# ?˜ì´ì§€ ?¤ì • - ??ë²„ì „ ?”ì?¸ìœ¼ë¡?ë¡¤ë°±
st.set_page_config(
    page_title="?Œ¤ï¸??¤ì‹œê°?? ì”¨",
    page_icon="?Œ¤ï¸?,
    layout="centered",  # wide?ì„œ centeredë¡?ë³€ê²?
    initial_sidebar_state="auto"
)

# CSSë¡?ë¶ˆí•„?”í•œ ?”ì†Œ ?¨ê¸°ê¸?
st.markdown("""
<style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stDecoration {display:none;}
    header {visibility: hidden;}
    .css-1rs6os {display:none;}
    .css-17eq0hr {display:none;}
</style>
""", unsafe_allow_html=True)

def get_weather_data(city_name, country_code=None):
    """?„ì¬ ? ì”¨ ?•ë³´ë¥?ê°€?¸ì˜¤???¨ìˆ˜"""
    if country_code:
        query = f"{city_name},{country_code}"
    else:
        query = city_name
    
    params = {
        'q': query,
        'appid': API_KEY,
        'units': 'metric',  # ??”¨ ?¨ë„
        'lang': 'kr'  # ?œêµ­??
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"? ì”¨ ?°ì´?°ë? ê°€?¸ì˜¤?”ë° ?¤íŒ¨?ˆìŠµ?ˆë‹¤: {e}")
        return None

def get_forecast_data(city_name, country_code=None):
    """5??? ì”¨ ?ˆë³´ë¥?ê°€?¸ì˜¤???¨ìˆ˜"""
    if country_code:
        query = f"{city_name},{country_code}"
    else:
        query = city_name
    
    params = {
        'q': query,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'kr'
    }
    
    try:
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"?ˆë³´ ?°ì´?°ë? ê°€?¸ì˜¤?”ë° ?¤íŒ¨?ˆìŠµ?ˆë‹¤: {e}")
        return None

def get_weather_by_coordinates(lat, lon):
    """?„ë„/ê²½ë„ë¡??„ì¬ ? ì”¨ ê°€?¸ì˜¤ê¸?""
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'kr'
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"?„ì¹˜ ê¸°ë°˜ ? ì”¨ ?°ì´?°ë? ê°€?¸ì˜¤?”ë° ?¤íŒ¨?ˆìŠµ?ˆë‹¤: {e}")
        return None

def get_forecast_by_coordinates(lat, lon):
    """?„ë„/ê²½ë„ë¡??ˆë³´ ?°ì´??ê°€?¸ì˜¤ê¸?""
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'kr'
    }
    
    try:
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"?„ì¹˜ ê¸°ë°˜ ?ˆë³´ ?°ì´?°ë? ê°€?¸ì˜¤?”ë° ?¤íŒ¨?ˆìŠµ?ˆë‹¤: {e}")
        return None

def process_weekly_forecast(forecast_data):
    """ì£¼ê°„ ?ˆë³´ ?°ì´??ì²˜ë¦¬"""
    if not forecast_data or 'list' not in forecast_data:
        return []
    
    weekly_data = []
    daily_data = {}
    
    # 5???ˆë³´ë¥??¼ë³„ë¡?ê·¸ë£¹??
    for item in forecast_data['list']:
        date = datetime.fromtimestamp(item['dt'])
        date_key = date.strftime('%Y-%m-%d')
        
        if date_key not in daily_data:
            daily_data[date_key] = {
                'temps': [],
                'humidity': [],
                'weather': item['weather'][0]['description'],
                'pop': item.get('pop', 0),
                'date': date,
                'wind_speeds': []
            }
        
        daily_data[date_key]['temps'].append(item['main']['temp'])
        daily_data[date_key]['humidity'].append(item['main']['humidity'])
        daily_data[date_key]['wind_speeds'].append(item['wind'].get('speed', 0))
    
    # ?¼ë³„ ?°ì´?°ë? ?•ë¦¬?˜ì—¬ ì£¼ê°„ ?°ì´???ì„±
    for date_key, data in list(daily_data.items())[:7]:  # ìµœë? 7??
        weekly_data.append({
            '? ì§œ': data['date'].strftime('%m/%d (%a)'),
            '? ì”¨': data['weather'],
            'ìµœê³ ?¨ë„': f"{max(data['temps']):.0f}Â°C",
            'ìµœì??¨ë„': f"{min(data['temps']):.0f}Â°C",
            '?‰ê· ?µë„': f"{sum(data['humidity'])//len(data['humidity'])}%",
            '?‰ê· ?ì†': f"{sum(data['wind_speeds'])/len(data['wind_speeds']):.1f} m/s",
            'ê°•ìˆ˜?•ë¥ ': f"{data['pop']*100:.0f}%"
        })
    
    return weekly_data

def display_current_weather(weather_data):
    """?„ì¬ ? ì”¨ ?•ë³´ ?œì‹œ"""
    # ? ì”¨ ?•ë³´ë¥?3ê°?ì»¬ëŸ¼?¼ë¡œ ?œì‹œ
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = weather_data['main']['temp']
        st.metric(
            label="?Œ¡ï¸??¨ë„", 
            value=f"{temp:.1f}Â°C",
            delta=f"ì²´ê° {weather_data['main']['feels_like']:.1f}Â°C"
        )
    
    with col2:
        humidity = weather_data['main']['humidity']
        st.metric(
            label="?’§ ?µë„", 
            value=f"{humidity}%"
        )
    
    with col3:
        wind_speed = weather_data['wind']['speed']
        st.metric(
            label="?’¨ ?ì†", 
            value=f"{wind_speed:.1f} m/s"
        )
    
    # ? ì”¨ ?íƒœ
    weather_desc = weather_data['weather'][0]['description']
    weather_icon = weather_data['weather'][0]['icon']
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
         border-radius: 10px; color: white; margin: 20px 0;">
        <h3>?ï¸ {weather_desc.title()}</h3>
        <p style="font-size: 18px; margin: 0;">?„ì¬ ? ì”¨ ?íƒœ</p>
    </div>
    """, unsafe_allow_html=True)

def display_city_weather(search_btn, city_input):
    """?„ì‹œ ê²€??ê²°ê³¼ ?œì‹œ"""
    if search_btn and city_input:
        with st.spinner("? ì”¨ ?•ë³´ ë¡œë”©ì¤?.."):
            weather_data = get_weather_data(city_input)
            
            if weather_data:
                # ? ì”¨???°ë¥¸ ?™ì  ë°°ê²½?”ë©´ ?¤ì •
                set_background(weather_data['weather'][0]['main'])
                
                # ê¸°ë³¸ ?•ë³´
                st.success(f"?“ {weather_data['name']}, {weather_data['sys']['country']}")
                
                # ?„ì¬ ? ì”¨ ?œì‹œ
                st.subheader("?Œ¡ï¸??„ì¬ ? ì”¨")
                display_current_weather(weather_data)
                
                # ?ì„¸ ?•ë³´
                with st.expander("?“Š ?ì„¸ ?•ë³´ ë³´ê¸°"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write(f"**ì²´ê°?¨ë„:** {weather_data['main']['feels_like']:.1f}Â°C")
                        st.write(f"**ìµœê³ ?¨ë„:** {weather_data['main']['temp_max']:.1f}Â°C")
                        st.write(f"**ìµœì??¨ë„:** {weather_data['main']['temp_min']:.1f}Â°C")
                        st.write(f"**ê¸°ì••:** {weather_data['main']['pressure']} hPa")
                    
                    with detail_col2:
                        st.write(f"**êµ¬ë¦„??** {weather_data['clouds']['all']}%")
                        st.write(f"**ê°€?œê±°ë¦?** {weather_data.get('visibility', 0)/1000:.1f} km")
                        
                        # ?¼ì¶œ/?¼ëª°
                        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
                        sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
                        st.write(f"**?¼ì¶œ:** {sunrise.strftime('%H:%M')}")
                        st.write(f"**?¼ëª°:** {sunset.strftime('%H:%M')}")
                
                # ?ˆë³´ ê·¸ë˜??(ê°„ë‹¨?˜ê²Œ)
                forecast_data = get_forecast_data(city_input)
                if forecast_data:
                    display_forecast(forecast_data)
            
            else:
                st.error("??? ì”¨ ?•ë³´ë¥?ê°€?¸ì˜¬ ???†ìŠµ?ˆë‹¤. ?„ì‹œëª…ì„ ?•ì¸?´ì£¼?¸ìš”.")
    
    elif not search_btn:
        st.info("?‘† ?„ì—???„ì‹œëª…ì„ ?…ë ¥?˜ê±°???¸ê¸° ?„ì‹œ ë²„íŠ¼???´ë¦­?˜ì„¸??")

def display_location_weather():
    """?„ì¬ ?„ì¹˜ ê¸°ë°˜ ? ì”¨ ?œì‹œ"""
    st.markdown("### ?“ ?„ì¬ ?„ì¹˜ ê¸°ë°˜ ? ì”¨")
    
    # ì¢Œí‘œ ?…ë ¥
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        latitude = st.number_input("?„ë„ (Latitude)", value=37.6199671, format="%.6f")
    
    with col2:
        longitude = st.number_input("ê²½ë„ (Longitude)", value=126.726365, format="%.6f")
    
    with col3:
        location_search = st.button("?¯ ?„ì¬ ?„ì¹˜ ? ì”¨", type="primary")
    
    # ?„ì¹˜ ê¸°ë°˜ ? ì”¨ ê²°ê³¼ ?œì‹œ
    if location_search:
        with st.spinner("?„ì¬ ?„ì¹˜??? ì”¨ ?•ë³´ë¥?ê°€?¸ì˜¤??ì¤?.."):
            weather_data = get_weather_by_coordinates(latitude, longitude)
            
            if weather_data:
                # ? ì”¨???°ë¥¸ ?™ì  ë°°ê²½?”ë©´ ?¤ì •
                set_background(weather_data['weather'][0]['main'])
                
                # ?ì„¸ ì£¼ì†Œ ?•ë³´ ?ë“
                detailed_address = get_detailed_address(latitude, longitude)
                
                # ?„ì¹˜ ?•ë³´ ?œì‹œ
                if detailed_address and detailed_address['formatted_address']:
                    location_display = f"?“ **?ì„¸ ?„ì¹˜:** {detailed_address['formatted_address']}"
                    weather_location = f"**? ì”¨ ê¸°ì?:** {weather_data['name']}, {weather_data['sys']['country']}"
                    st.success(location_display)
                    st.info(f"?Œ¤ï¸?{weather_location} | ?“ ?„ë„: {latitude:.4f}, ê²½ë„: {longitude:.4f}")
                    
                    # ?ì„¸ ì£¼ì†Œ ?•ë³´ë¥??•ì¥ ê°€?¥í•œ ?¹ì…˜?¼ë¡œ ?œì‹œ
                    with st.expander("?—ºï¸??ì„¸ ?„ì¹˜ ?•ë³´ ë³´ê¸°"):
                        addr_col1, addr_col2 = st.columns(2)
                        
                        with addr_col1:
                            if detailed_address['country']:
                                st.write(f"**?Œ êµ??:** {detailed_address['country']}")
                            if detailed_address['state']:
                                st.write(f"**?›ï¸?????** {detailed_address['state']}")
                            if detailed_address['city']:
                                st.write(f"**?™ï¸???êµ?** {detailed_address['city']}")
                        
                        with addr_col2:
                            if detailed_address['district']:
                                st.write(f"**?˜ï¸?êµ?** {detailed_address['district']}")
                            if detailed_address['neighbourhood']:
                                st.write(f"**?  ??ë©?** {detailed_address['neighbourhood']}")
                            if detailed_address['road']:
                                st.write(f"**?›£ï¸??„ë¡œ:** {detailed_address['road']}")
                
                else:
                    # Nominatim API ?¤íŒ¨ ??ê¸°ë³¸ ?•ë³´ ?œì‹œ
                    st.success(f"?“ {weather_data['name']}, {weather_data['sys']['country']}")
                    st.info(f"?“ ?„ë„: {latitude:.4f}, ê²½ë„: {longitude:.4f}")
                    st.warning("? ï¸ ?ì„¸ ì£¼ì†Œ ?•ë³´ë¥?ê°€?¸ì˜¬ ???†ì–´ ? ì”¨ ê¸°ì? ?„ì¹˜ë¥??œì‹œ?©ë‹ˆ??")
                
                st.subheader("?Œ¡ï¸??„ì¬ ? ì”¨")
                display_current_weather(weather_data)
                
                # ?ì„¸ ?•ë³´
                with st.expander("?“Š ?ì„¸ ?•ë³´ ë³´ê¸°"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write(f"**ì²´ê°?¨ë„:** {weather_data['main']['feels_like']:.1f}Â°C")
                        st.write(f"**ìµœê³ ?¨ë„:** {weather_data['main']['temp_max']:.1f}Â°C")
                        st.write(f"**ìµœì??¨ë„:** {weather_data['main']['temp_min']:.1f}Â°C")
                        st.write(f"**ê¸°ì••:** {weather_data['main']['pressure']} hPa")
                    
                    with detail_col2:
                        st.write(f"**êµ¬ë¦„??** {weather_data['clouds']['all']}%")
                        st.write(f"**ê°€?œê±°ë¦?** {weather_data.get('visibility', 0)/1000:.1f} km")
                        
                        # ?¼ì¶œ/?¼ëª°
                        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
                        sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
                        st.write(f"**?¼ì¶œ:** {sunrise.strftime('%H:%M')}")
                        st.write(f"**?¼ëª°:** {sunset.strftime('%H:%M')}")
                
                # ì£¼ê°„ ?ˆë³´
                st.divider()
                forecast_data = get_forecast_by_coordinates(latitude, longitude)
                if forecast_data:
                    weekly_data = process_weekly_forecast(forecast_data)
                    
                    if weekly_data:
                        st.subheader("?“… ì£¼ê°„ ? ì”¨ ?ˆë³´ (7??")
                        
                        # ì£¼ê°„ ?ˆë³´ ?°ì´?°í”„?ˆì„
                        weekly_df = pd.DataFrame(weekly_data)
                        st.dataframe(weekly_df, use_container_width=True)
                        
                        # ì£¼ê°„ ?¨ë„ ë³€??ì°¨íŠ¸
                        st.subheader("?“Š ì£¼ê°„ ?¨ë„ ë³€??)
                        
                        # ?¨ë„ ?°ì´??ì¶”ì¶œ
                        chart_data = []
                        for item in weekly_data:
                            max_temp = float(item['ìµœê³ ?¨ë„'].replace('Â°C', ''))
                            min_temp = float(item['ìµœì??¨ë„'].replace('Â°C', ''))
                            chart_data.append({
                                '? ì§œ': item['? ì§œ'],
                                'ìµœê³ ?¨ë„': max_temp,
                                'ìµœì??¨ë„': min_temp
                            })
                        
                        chart_df = pd.DataFrame(chart_data).set_index('? ì§œ')
                        st.line_chart(chart_df)
                    
                    st.divider()  # êµ¬ë¶„??ì¶”ê?
                    
                    # OOTD ?€?„ë¼??
                    display_hourly_ootd_timeline(forecast_data)
                    
                    st.divider()  # êµ¬ë¶„??ì¶”ê?
                    
                    # 2?¼ê°„ ?ì„¸ ê·¸ë˜??(ê¸°ì¡´ ê¸°ëŠ¥ ? ì?)
                    display_forecast(forecast_data)
            
            else:
                st.error("???„ì¬ ?„ì¹˜??? ì”¨ ?•ë³´ë¥?ê°€?¸ì˜¬ ???†ìŠµ?ˆë‹¤.")
    
    else:
        st.markdown("""
        ### ?’¡ ?¬ìš©ë²?
        **?„ì¬ ?„ì¹˜ ê¸°ë°˜ ? ì”¨ ì¡°íšŒ:**
        1. **?„ë„/ê²½ë„ ?…ë ¥** ??'?¯ ?„ì¬ ?„ì¹˜ ? ì”¨' ?´ë¦­
        2. ?ëŠ” **ì£¼ìš” ?„ì‹œ ì¢Œí‘œ ë²„íŠ¼** ?´ë¦­
        3. **ì£¼ê°„ ?ˆë³´** ë°?**?¨ë„ ë³€??ì°¨íŠ¸** ?•ì¸
        
        ### ?—“ï¸?ì£¼ê°„ ?ˆë³´ ê¸°ëŠ¥
        - **7??? ì”¨ ?ˆë³´**: ?¼ë³„ ìµœê³ /ìµœì? ?¨ë„
        - **?ì„¸ ?•ë³´**: ? ì”¨, ?µë„, ?ì†, ê°•ìˆ˜?•ë¥ 
        - **?¨ë„ ì°¨íŠ¸**: ì£¼ê°„ ?¨ë„ ë³€???œê°??
        - **2???ì„¸**: 48?œê°„ ?¨ë„/?µë„/?ì† ê·¸ë˜??
        
        ### ?“ ì¢Œí‘œ ?ˆì‹œ
        - **ê¹€???¬ìš°??*: 37.6199671, 126.726365
        - **?œìš¸**: 37.5665, 126.9780
        - **ë¶€??*: 35.1796, 129.0756  
        - **?œì£¼**: 33.4996, 126.5312
        """)

def display_current_weather(weather_data):
    """?„ì¬ ? ì”¨ ?•ë³´ë¥??œì‹œ?˜ëŠ” ?¨ìˆ˜"""
    if weather_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="?Œ¡ï¸??¨ë„",
                value=f"{weather_data['main']['temp']:.1f}Â°C",
                delta=f"ì²´ê°?¨ë„: {weather_data['main']['feels_like']:.1f}Â°C"
            )
        
        with col2:
            st.metric(
                label="?’§ ?µë„",
                value=f"{weather_data['main']['humidity']}%"
            )
        
        with col3:
            st.metric(
                label="?‘ï¸?ê°€?œê±°ë¦?,
                value=f"{weather_data.get('visibility', 0)/1000:.1f}km"
            )
        
        # ì¶”ê? ?•ë³´
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric(
                label="?Œ¬ï¸??ì†",
                value=f"{weather_data['wind'].get('speed', 0)} m/s"
            )
        
        with col5:
            st.metric(
                label="?Œ¡ï¸?ê¸°ì••",
                value=f"{weather_data['main']['pressure']} hPa"
            )
        
        with col6:
            st.metric(
                label="?Œ¤ï¸?? ì”¨",
                value=weather_data['weather'][0]['description']
            )

def display_forecast(forecast_data):
    """5??? ì”¨ ?ˆë³´ë¥?ê·¸ë˜?„ë¡œ ?œì‹œ?˜ëŠ” ?¨ìˆ˜"""
    if forecast_data:
        # --- ê·¸ë˜?„ë¡œ ë³€ê²?---
        # '?œê°„'???¸ë±?¤ë¡œ, '?¨ë„'ë¥?ê°’ìœ¼ë¡??˜ëŠ” ??DataFrame ?ì„±
        chart_data_list = []
        for item in forecast_data['list'][:16]:  # 2?¼ì¹˜(16*3=48?œê°„) ?•ë„ë§?
            chart_data_list.append({
                '?œê°„': datetime.fromtimestamp(item['dt']),
                '?¨ë„': item['main']['temp']
            })

        chart_df = pd.DataFrame(chart_data_list).set_index('?œê°„')

        st.subheader("?Œ¡ï¸?2?¼ê°„ ê¸°ì˜¨ ë³€??)
        st.line_chart(chart_df)
        
        # ì¶”ê?: ?µë„?€ ?ì† ê·¸ë˜??
        st.subheader("ï¿?2?¼ê°„ ?µë„ ë°??Œ¬ï¸??ì† ë³€??)
        
        # ?µë„?€ ?ì† ?°ì´??ì¤€ë¹?
        multi_data_list = []
        for item in forecast_data['list'][:16]:
            multi_data_list.append({
                '?œê°„': datetime.fromtimestamp(item['dt']),
                '?µë„(%)': item['main']['humidity'],
                '?ì†(m/s)': item['wind'].get('speed', 0)
            })
        
        multi_df = pd.DataFrame(multi_data_list).set_index('?œê°„')
        st.line_chart(multi_df)
        
        # ?ì„¸ ?°ì´????(?‘ì„ ???ˆëŠ” ?•íƒœë¡?
        with st.expander("?“Š ?ì„¸ ?ˆë³´ ?°ì´??ë³´ê¸°"):
            detail_list = []
            for item in forecast_data['list'][:16]:
                date_time = datetime.fromtimestamp(item['dt'])
                detail_list.append({
                    '? ì§œ': date_time.strftime('%m-%d'),
                    '?œê°„': date_time.strftime('%H:%M'),
                    '?¨ë„': f"{item['main']['temp']:.1f}Â°C",
                    '? ì”¨': item['weather'][0]['description'],
                    '?µë„': f"{item['main']['humidity']}%",
                    '?ì†': f"{item['wind'].get('speed', 0):.1f} m/s"
                })
            
            detail_df = pd.DataFrame(detail_list)
            st.dataframe(detail_df, use_container_width=True)



def display_hourly_ootd_timeline(forecast_data):
    """
    ?œê°„?€ë³?OOTD ?€?„ë¼?¸ì„ ê°€ë¡œë¡œ ?œì‹œ?˜ëŠ” ?¨ìˆ˜ (ê°œì„  ë²„ì „)
    """
    st.subheader("?‘• ?œê°„?€ë³?'?¤ëŠ˜ ë­??…ì??' ?€?„ë¼??)

    # 1. '?¤ëŠ˜+?´ì¼'???ˆë³´ ?°ì´???„í„°ë§?(??ë§ì? ?œê°„?€)
    now = datetime.now()
    forecasts = []
    
    if 'list' not in forecast_data:
        st.warning("?œê°„?€ë³??ˆë³´ ?°ì´?°ë? ë¶ˆëŸ¬?????†ìŠµ?ˆë‹¤.")
        return

    for item in forecast_data['list'][:12]:  # 36?œê°„ (12ê°??œê°„?€)
        item_time = datetime.fromtimestamp(item['dt'])
        # ?„ì¬ ?œê°„ ?´í›„???ˆë³´ë§?? íƒ
        if item_time >= now:
            forecasts.append(item)
    
    if not forecasts:
        st.info("?œê°„?€ë³??ˆë³´ ?•ë³´ê°€ ?†ìŠµ?ˆë‹¤.")
        return

    # 2. ê°€ë¡??€?„ë¼???ì„± (6ê°œë¡œ ì¤„ì—¬???“ì´ ?•ë³´)
    cols = st.columns(min(len(forecasts), 6))  # ìµœë? 6ê°?ì»¬ëŸ¼?¼ë¡œ ì¤„ì„
    
    prev_rec = None  # ?´ì „ ?œê°„?€ ì¶”ì²œ???€?¥í•  ë³€??

    for i, item in enumerate(forecasts[:6]):  # ìµœë? 6ê°??œê°„?€ë§??œì‹œ
        with cols[i]:
            # ê³ ì • ?’ì´ ì¹´ë“œ ì»¨í…Œ?´ë„ˆ
            st.markdown("""
            <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; 
                        height: 400px; background-color: rgba(255, 255, 255, 0.95); 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            """, unsafe_allow_html=True)
            
            item_time = datetime.fromtimestamp(item['dt'])
            
            # ? ì”¨ ?°ì´??ì¶”ì¶œ
            temp = item['main']['temp']
            feels_like = item['main']['feels_like']
            humidity = item['main']['humidity']
            wind_speed = item['wind'].get('speed', 0)
            weather_main = item['weather'][0]['main']
            weather_desc = item['weather'][0]['description']
            
            # ?„ì¬ ?œê°„?€??OOTD ì¶”ì²œ ë°›ê¸°
            current_rec, accessory_rec = get_ootd_recommendation(feels_like, weather_main)

            # (1) ?œê°„ ?œì‹œ - ê³ ì • ?’ì´
            if item_time.date() == now.date():
                time_str = f"?¤ëŠ˜ {item_time.strftime('%H??)}"
            else:
                time_str = f"?´ì¼ {item_time.strftime('%H??)}"
            
            st.markdown(f"""
            <div style="text-align: center; font-weight: bold; font-size: 14px; 
                       margin-bottom: 12px; padding: 8px; height: 35px;
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       border-radius: 8px; color: white; display: flex; align-items: center; justify-content: center;">
                {time_str}
            </div>
            """, unsafe_allow_html=True)
            
            # (2) ? ì”¨ ?•ë³´ - ê³ ì • ?’ì´
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px; height: 50px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-weight: bold; font-size: 16px;">?Œ¡ï¸?{temp:.1f}Â°C</div>
                <div style="font-size: 12px; color: #666;">ì²´ê° {feels_like:.1f}Â°C</div>
                <div style="font-size: 11px; color: #888;">?’§ {humidity}% | ?’¨ {wind_speed:.1f}m/s</div>
            </div>
            """, unsafe_allow_html=True)
            
            # (3) ë³€??ê°ì? ë°?ì¡°ì–¸ - ê³ ì • ?’ì´
            advice_html = ""
            if prev_rec and current_rec['level'] < prev_rec['level']:
                colder_item = current_rec['items'].split(',')[0].strip()
                advice_html = f"""
                <div style="background-color: rgba(255, 193, 7, 0.2); padding: 6px; border-radius: 6px; 
                           text-align: center; font-size: 11px; font-weight: bold; height: 35px; 
                           display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                    ??{colder_item} ì±™ê¸°?¸ìš”!
                </div>
                """
            elif prev_rec and current_rec['level'] > prev_rec['level']:
                advice_html = f"""
                <div style="background-color: rgba(144, 202, 249, 0.3); padding: 6px; border-radius: 6px; 
                           text-align: center; font-size: 11px; font-weight: bold; height: 35px; 
                           display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                    ?€ï¸??”ì›Œ?¸ìš”. ?¸íˆ¬ë¥?ë²—ìœ¼?¸ìš”
                </div>
                """
            else:
                advice_html = '<div style="height: 43px; margin-bottom: 8px;"></div>'
            
            st.markdown(advice_html, unsafe_allow_html=True)

            # (4) ì¶”ì²œ ?·ì°¨ë¦??íƒœ - ê³ ì • ?’ì´
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; height: 35px;
                       background: rgba(103, 126, 234, 0.1); 
                       border-radius: 6px; margin-bottom: 10px; 
                       display: flex; align-items: center; justify-content: center;">
                <strong style="font-size: 12px;">{current_rec['summary']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # (5) ì¶”ì²œ ?˜ë¥˜ - ê³ ì • ?’ì´
            st.markdown(f"""
            <div style="margin-bottom: 8px; height: 80px; overflow: hidden;">
                <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">?‘• ì¶”ì²œ ?˜ë¥˜</div>
                <div style="font-size: 10px; color: #666; line-height: 1.3;">{current_rec['items']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # (6) ?¡ì„¸?œë¦¬ ì¡°ì–¸ - ê³ ì • ?’ì´
            accessory_text = accessory_rec if accessory_rec else "?¹ë³„??ì¤€ë¹„ë¬¼ ?†ìŒ"
            st.markdown(f"""
            <div style="height: 60px; overflow: hidden;">
                <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">?¯ ?„ìˆ˜ ?„ì´??/div>
                <div style="font-size: 10px; color: #666; line-height: 1.3;">{accessory_text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # ì»¨í…Œ?´ë„ˆ ?«ê¸°
            st.markdown("</div>", unsafe_allow_html=True)

            # ?¤ìŒ ë£¨í”„ë¥??„í•´ ?„ì¬ ì¶”ì²œ??prev_rec???€??
            prev_rec = current_rec

def main():
    """ë©”ì¸ ?¨ìˆ˜"""
    # ?œëª©
    st.title("?Œ¤ï¸??¤ì‹œê°?? ì”¨")
    
    # ?„ì¬ ?„ì¹˜ ê¸°ë°˜ ? ì”¨ë§??œì‹œ
    display_location_weather()

if __name__ == "__main__":
    main()
