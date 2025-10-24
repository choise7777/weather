import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import os
from pathlib import Path

# API ??보안 로딩
try:
    # Streamlit Secrets?�서 API ??로딩 (?�선?�위 1)
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (KeyError, FileNotFoundError):
    try:
        # .env ?�일?�서 ?�경변??로딩 ?�도 (?�선?�위 2)
        from dotenv import load_dotenv
        load_dotenv()
        API_KEY = os.getenv('OPENWEATHER_API_KEY')
        
        # .env ?�일???�으�?config.py?�서 로딩
        if not API_KEY:
            from config import OPENWEATHER_API_KEY
            API_KEY = OPENWEATHER_API_KEY
    except (ImportError, ModuleNotFoundError):
        try:
            # config.py?�서 직접 로딩 (?�선?�위 3)
            from config import OPENWEATHER_API_KEY
            API_KEY = OPENWEATHER_API_KEY
        except (ImportError, ModuleNotFoundError):
            # 마�?�??�단?�로 ?�드코딩?????�용 (개발??
            API_KEY = "14e3fc348b3e11a20c23806f1c3be844"
            st.warning("?�️ API ?��? 보안 ?�일?�서 로딩?��? ?�았?�니?? secrets.toml ?�는 config.py ?�일???�인?�세??")

def get_detailed_address(latitude, longitude):
    """Nominatim API�??�용??좌표로�????�세 주소 ?�보 ?�득"""
    try:
        # Nominatim API (OpenStreetMap??무료 지?�코???�비??
        nominatim_url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'accept-language': 'ko,en',  # ?�국???�선, ?�어 fallback
            'zoom': 18  # ?�세??주소 ?�보 ?�청
        }
        
        headers = {
            'User-Agent': 'WeatherApp/1.0 (contact@example.com)'  # Nominatim ?�책???�수
        }
        
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # 주소 ?�보 ?�싱
            address = data.get('address', {})
            display_name = data.get('display_name', '')
            
            # ?�국 주소 체계??맞게 ?�보 추출
            location_info = {
                'country': address.get('country', ''),
                'state': address.get('state', ''),  # ????
                'city': address.get('city', '') or address.get('county', ''),  # ??�?
                'district': address.get('district', '') or address.get('borough', ''),  # �?
                'neighbourhood': address.get('neighbourhood', '') or address.get('suburb', ''),  # ??�?
                'road': address.get('road', ''),  # ?�로�?
                'house_number': address.get('house_number', ''),
                'full_address': display_name
            }
            
            # ?�국??주소 ?�맷??
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
        print(f"Nominatim API ?�류: {e}")
        return None
    
    return None

def get_ootd_recommendation(feels_like, weather_main):
    """
    체감 ?�도?� ?�씨 ?�태???�라 ?�차림을 추천?�는 ?�수 (?�이??처리)
    'level'??추�??�여 기온 ?�계�?비교?????�게 ??
    """
    
    if feels_like > 27:
        rec = {
            "level": 8,  # ?�다
            "summary": "?�� 매우 ?��?",
            "items": "민소�? 반팔, 반바지, 린넨, ?�피??,
            "image_path": "images/ootd_hot.png"
        }
    elif 23 <= feels_like <= 27:
        rec = {
            "level": 7,
            "summary": "?�� ?��?",
            "items": "반팔, ?��? ?�츠, 반바지, 면바지",
            "image_path": "images/ootd_warm.png"
        }
    elif 20 <= feels_like <= 22:
        rec = {
            "level": 6,
            "summary": "?�� 쾌적??,
            "items": "?��? 가?�건, 긴팔 ?�츠, 면바지, �?��지",
            "image_path": "images/ootd_mild.png"
        }
    elif 17 <= feels_like <= 19:
        rec = {
            "level": 5,
            "summary": "?�� ?�선??,
            "items": "맨투�? ?�드?? ?��? ?�트, �?��지",
            "image_path": "images/ootd_cool.png"
        }
    elif 12 <= feels_like <= 16:
        rec = {
            "level": 4,
            "summary": "?�� ?�?�??,
            "items": "?�켓, 가?�건, ?�트, ?��??? 기모 바�?",
            "image_path": "images/ootd_chilly.png"
        }
    elif 9 <= feels_like <= 11:
        rec = {
            "level": 3,
            "summary": "?�� 추�?",
            "items": "?�렌�?코트, ?�상, ?�트, ?�트??,
            "image_path": "images/ootd_cold.png"
        }
    elif 5 <= feels_like <= 8:
        rec = {
            "level": 2,
            "summary": "?�️ 매우 추�?",
            "items": "??코트, 가�??�켓, 목도�? 기모",
            "image_path": "images/ootd_very_cold.png"
        }
    else:  # 5??미만
        rec = {
            "level": 1,
            "summary": "?��?�� ?�파",
            "items": "?�딩, ?�꺼??코트, ?�복, 목도�? ?�갑",
            "image_path": "images/ootd_freezing.png"
        }

    # ?�씨�??�세?�리 추천
    accessory_rec = ""
    if weather_main == "Rain":
        accessory_rec = "???�산??�?챙기?�요! 방수 ?�발??좋습?�다."
    elif weather_main == "Snow":
        accessory_rec = "?�️ 미끄??방�? ?�발�??�갑??준비하?�요."
    elif weather_main == "Thunderstorm":
        accessory_rec = "???�산�?방수 ?�투�?챙기?�요."
    elif weather_main == "Drizzle":
        accessory_rec = "?���?가벼운 ?�산?�나 ?�드�?준비하?�요."
    elif weather_main == "Mist" or weather_main == "Fog":
        accessory_rec = "?���??�야 ?�보�??�해 밝�? ???�을 권합?�다."
    elif weather_main == "Clear" and feels_like > 25:
        accessory_rec = "?���??��??�스?� ?�외??차단?��? 준비하?�요."
    elif weather_main == "Clouds" and feels_like < 15:
        accessory_rec = "?�️ 체온 ?��?�??�해 목도리�? 챙기?�요."
    
    return rec, accessory_rec

def set_background(weather_main):
    """?�씨 ?�태???�라 ?�적 배경?�면 ?�정"""
    # ?�씨 ?�태???�라 ?�른 ?��?지 URL??매핑
    if weather_main == "Clear":
        bg_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # 맑�? ?�늘
    elif weather_main == "Rain":
        bg_url = "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2127&q=80"  # �??�는 창문
    elif weather_main == "Snow":
        bg_url = "https://images.unsplash.com/photo-1548777123-93d6ac74e765?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # ???�리???�경
    elif weather_main == "Clouds":
        bg_url = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2051&q=80"  # ?�린 ?�늘
    elif weather_main == "Thunderstorm":
        bg_url = "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2071&q=80"  # 번개/천둥
    elif weather_main == "Drizzle":
        bg_url = "https://images.unsplash.com/photo-1541919329513-35f7af297129?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # ?�슬�?
    elif weather_main == "Mist" or weather_main == "Fog":
        bg_url = "https://images.unsplash.com/photo-1487621167305-5d248087c724?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2132&q=80"  # ?�개 ?� ?�경
    else:
        bg_url = "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  # 기본 ?�늘 ?��?지

    # CSS�?HTML�?주입
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
        
        /* ?�체 ??컨테?�너??강한 반투�?배경 */
        .stApp > div:first-child {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
            min-height: 100vh;
        }}
        
        /* 메인 컨테?�너 배경 강화 */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.98) !important;
            padding: 2rem 1rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            backdrop-filter: blur(15px);
        }}
        
        /* 메트�?카드 ?��???개선 */
        div[data-testid="metric-container"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid rgba(200, 200, 200, 0.5);
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        /* 메트�??�스??강화 */
        div[data-testid="metric-container"] * {{
            color: #333333 !important;
            font-weight: 600 !important;
        }}
        
        /* ?�장 가?�한 ?�션 ?��???*/
        div[data-testid="stExpander"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 12px;
            border: 1px solid rgba(200, 200, 200, 0.5);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        /* ???��???개선 */
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
        
        /* 버튼 ?��???개선 */
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
        
        /* ?�력 ?�드 ?��???개선 */
        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #333333 !important;
            border: 2px solid rgba(200, 200, 200, 0.7) !important;
        }}
        
        /* ?�자 ?�력 ?�드 ?��???개선 */
        .stNumberInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #333333 !important;
            border: 2px solid rgba(200, 200, 200, 0.7) !important;
        }}
        
        /* ?�이?�프?�임 ?��???개선 */
        .stDataFrame {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        /* 차트 배경 개선 */
        .stPlotlyChart {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px;
            padding: 10px;
        }}
        
        /* ?�반 ?�스??가?�성 ?�상 */
        .stMarkdown, .stText, p, div {{
            color: #333333 !important;
        }}
        
        /* ?�목 ?��???강화 */
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50 !important;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# OpenWeather API ?�정
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# ?�이지 ?�정 - ??버전 ?�자?�으�?롤백
st.set_page_config(
    page_title="?���??�시�??�씨",
    page_icon="?���?,
    layout="centered",  # wide?�서 centered�?변�?
    initial_sidebar_state="auto"
)

# CSS�?불필?�한 ?�소 ?�기�?
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
    """?�재 ?�씨 ?�보�?가?�오???�수"""
    if country_code:
        query = f"{city_name},{country_code}"
    else:
        query = city_name
    
    params = {
        'q': query,
        'appid': API_KEY,
        'units': 'metric',  # ??�� ?�도
        'lang': 'kr'  # ?�국??
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"?�씨 ?�이?��? 가?�오?�데 ?�패?�습?�다: {e}")
        return None

def get_forecast_data(city_name, country_code=None):
    """5???�씨 ?�보�?가?�오???�수"""
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
        st.error(f"?�보 ?�이?��? 가?�오?�데 ?�패?�습?�다: {e}")
        return None

def get_weather_by_coordinates(lat, lon):
    """?�도/경도�??�재 ?�씨 가?�오�?""
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
        st.error(f"?�치 기반 ?�씨 ?�이?��? 가?�오?�데 ?�패?�습?�다: {e}")
        return None

def get_forecast_by_coordinates(lat, lon):
    """?�도/경도�??�보 ?�이??가?�오�?""
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
        st.error(f"?�치 기반 ?�보 ?�이?��? 가?�오?�데 ?�패?�습?�다: {e}")
        return None

def process_weekly_forecast(forecast_data):
    """주간 ?�보 ?�이??처리"""
    if not forecast_data or 'list' not in forecast_data:
        return []
    
    weekly_data = []
    daily_data = {}
    
    # 5???�보�??�별�?그룹??
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
    
    # ?�별 ?�이?��? ?�리?�여 주간 ?�이???�성
    for date_key, data in list(daily_data.items())[:7]:  # 최�? 7??
        weekly_data.append({
            '?�짜': data['date'].strftime('%m/%d (%a)'),
            '?�씨': data['weather'],
            '최고?�도': f"{max(data['temps']):.0f}°C",
            '최�??�도': f"{min(data['temps']):.0f}°C",
            '?�균?�도': f"{sum(data['humidity'])//len(data['humidity'])}%",
            '?�균?�속': f"{sum(data['wind_speeds'])/len(data['wind_speeds']):.1f} m/s",
            '강수?�률': f"{data['pop']*100:.0f}%"
        })
    
    return weekly_data

def display_current_weather(weather_data):
    """?�재 ?�씨 ?�보 ?�시"""
    # ?�씨 ?�보�?3�?컬럼?�로 ?�시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = weather_data['main']['temp']
        st.metric(
            label="?���??�도", 
            value=f"{temp:.1f}°C",
            delta=f"체감 {weather_data['main']['feels_like']:.1f}°C"
        )
    
    with col2:
        humidity = weather_data['main']['humidity']
        st.metric(
            label="?�� ?�도", 
            value=f"{humidity}%"
        )
    
    with col3:
        wind_speed = weather_data['wind']['speed']
        st.metric(
            label="?�� ?�속", 
            value=f"{wind_speed:.1f} m/s"
        )
    
    # ?�씨 ?�태
    weather_desc = weather_data['weather'][0]['description']
    weather_icon = weather_data['weather'][0]['icon']
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
         border-radius: 10px; color: white; margin: 20px 0;">
        <h3>?�️ {weather_desc.title()}</h3>
        <p style="font-size: 18px; margin: 0;">?�재 ?�씨 ?�태</p>
    </div>
    """, unsafe_allow_html=True)

def display_city_weather(search_btn, city_input):
    """?�시 검??결과 ?�시"""
    if search_btn and city_input:
        with st.spinner("?�씨 ?�보 로딩�?.."):
            weather_data = get_weather_data(city_input)
            
            if weather_data:
                # ?�씨???�른 ?�적 배경?�면 ?�정
                set_background(weather_data['weather'][0]['main'])
                
                # 기본 ?�보
                st.success(f"?�� {weather_data['name']}, {weather_data['sys']['country']}")
                
                # ?�재 ?�씨 ?�시
                st.subheader("?���??�재 ?�씨")
                display_current_weather(weather_data)
                
                # ?�세 ?�보
                with st.expander("?�� ?�세 ?�보 보기"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write(f"**체감?�도:** {weather_data['main']['feels_like']:.1f}°C")
                        st.write(f"**최고?�도:** {weather_data['main']['temp_max']:.1f}°C")
                        st.write(f"**최�??�도:** {weather_data['main']['temp_min']:.1f}°C")
                        st.write(f"**기압:** {weather_data['main']['pressure']} hPa")
                    
                    with detail_col2:
                        st.write(f"**구름??** {weather_data['clouds']['all']}%")
                        st.write(f"**가?�거�?** {weather_data.get('visibility', 0)/1000:.1f} km")
                        
                        # ?�출/?�몰
                        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
                        sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
                        st.write(f"**?�출:** {sunrise.strftime('%H:%M')}")
                        st.write(f"**?�몰:** {sunset.strftime('%H:%M')}")
                
                # ?�보 그래??(간단?�게)
                forecast_data = get_forecast_data(city_input)
                if forecast_data:
                    display_forecast(forecast_data)
            
            else:
                st.error("???�씨 ?�보�?가?�올 ???�습?�다. ?�시명을 ?�인?�주?�요.")
    
    elif not search_btn:
        st.info("?�� ?�에???�시명을 ?�력?�거???�기 ?�시 버튼???�릭?�세??")

def display_location_weather():
    """?�재 ?�치 기반 ?�씨 ?�시"""
    st.markdown("### ?�� ?�재 ?�치 기반 ?�씨")
    
    # 좌표 ?�력
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        latitude = st.number_input("?�도 (Latitude)", value=37.6199671, format="%.6f")
    
    with col2:
        longitude = st.number_input("경도 (Longitude)", value=126.726365, format="%.6f")
    
    with col3:
        location_search = st.button("?�� ?�재 ?�치 ?�씨", type="primary")
    
    # ?�치 기반 ?�씨 결과 ?�시
    if location_search:
        with st.spinner("?�재 ?�치???�씨 ?�보�?가?�오??�?.."):
            weather_data = get_weather_by_coordinates(latitude, longitude)
            
            if weather_data:
                # ?�씨???�른 ?�적 배경?�면 ?�정
                set_background(weather_data['weather'][0]['main'])
                
                # ?�세 주소 ?�보 ?�득
                detailed_address = get_detailed_address(latitude, longitude)
                
                # ?�치 ?�보 ?�시
                if detailed_address and detailed_address['formatted_address']:
                    location_display = f"?�� **?�세 ?�치:** {detailed_address['formatted_address']}"
                    weather_location = f"**?�씨 기�?:** {weather_data['name']}, {weather_data['sys']['country']}"
                    st.success(location_display)
                    st.info(f"?���?{weather_location} | ?�� ?�도: {latitude:.4f}, 경도: {longitude:.4f}")
                    
                    # ?�세 주소 ?�보�??�장 가?�한 ?�션?�로 ?�시
                    with st.expander("?���??�세 ?�치 ?�보 보기"):
                        addr_col1, addr_col2 = st.columns(2)
                        
                        with addr_col1:
                            if detailed_address['country']:
                                st.write(f"**?�� �??:** {detailed_address['country']}")
                            if detailed_address['state']:
                                st.write(f"**?���?????** {detailed_address['state']}")
                            if detailed_address['city']:
                                st.write(f"**?���???�?** {detailed_address['city']}")
                        
                        with addr_col2:
                            if detailed_address['district']:
                                st.write(f"**?���?�?** {detailed_address['district']}")
                            if detailed_address['neighbourhood']:
                                st.write(f"**?�� ??�?** {detailed_address['neighbourhood']}")
                            if detailed_address['road']:
                                st.write(f"**?���??�로:** {detailed_address['road']}")
                
                else:
                    # Nominatim API ?�패 ??기본 ?�보 ?�시
                    st.success(f"?�� {weather_data['name']}, {weather_data['sys']['country']}")
                    st.info(f"?�� ?�도: {latitude:.4f}, 경도: {longitude:.4f}")
                    st.warning("?�️ ?�세 주소 ?�보�?가?�올 ???�어 ?�씨 기�? ?�치�??�시?�니??")
                
                st.subheader("?���??�재 ?�씨")
                display_current_weather(weather_data)
                
                # ?�세 ?�보
                with st.expander("?�� ?�세 ?�보 보기"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write(f"**체감?�도:** {weather_data['main']['feels_like']:.1f}°C")
                        st.write(f"**최고?�도:** {weather_data['main']['temp_max']:.1f}°C")
                        st.write(f"**최�??�도:** {weather_data['main']['temp_min']:.1f}°C")
                        st.write(f"**기압:** {weather_data['main']['pressure']} hPa")
                    
                    with detail_col2:
                        st.write(f"**구름??** {weather_data['clouds']['all']}%")
                        st.write(f"**가?�거�?** {weather_data.get('visibility', 0)/1000:.1f} km")
                        
                        # ?�출/?�몰
                        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
                        sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
                        st.write(f"**?�출:** {sunrise.strftime('%H:%M')}")
                        st.write(f"**?�몰:** {sunset.strftime('%H:%M')}")
                
                # 주간 ?�보
                st.divider()
                forecast_data = get_forecast_by_coordinates(latitude, longitude)
                if forecast_data:
                    weekly_data = process_weekly_forecast(forecast_data)
                    
                    if weekly_data:
                        st.subheader("?�� 주간 ?�씨 ?�보 (7??")
                        
                        # 주간 ?�보 ?�이?�프?�임
                        weekly_df = pd.DataFrame(weekly_data)
                        st.dataframe(weekly_df, use_container_width=True)
                        
                        # 주간 ?�도 변??차트
                        st.subheader("?�� 주간 ?�도 변??)
                        
                        # ?�도 ?�이??추출
                        chart_data = []
                        for item in weekly_data:
                            max_temp = float(item['최고?�도'].replace('°C', ''))
                            min_temp = float(item['최�??�도'].replace('°C', ''))
                            chart_data.append({
                                '?�짜': item['?�짜'],
                                '최고?�도': max_temp,
                                '최�??�도': min_temp
                            })
                        
                        chart_df = pd.DataFrame(chart_data).set_index('?�짜')
                        st.line_chart(chart_df)
                    
                    st.divider()  # 구분??추�?
                    
                    # OOTD ?�?�라??
                    display_hourly_ootd_timeline(forecast_data)
                    
                    st.divider()  # 구분??추�?
                    
                    # 2?�간 ?�세 그래??(기존 기능 ?��?)
                    display_forecast(forecast_data)
            
            else:
                st.error("???�재 ?�치???�씨 ?�보�?가?�올 ???�습?�다.")
    
    else:
        st.markdown("""
        ### ?�� ?�용�?
        **?�재 ?�치 기반 ?�씨 조회:**
        1. **?�도/경도 ?�력** ??'?�� ?�재 ?�치 ?�씨' ?�릭
        2. ?�는 **주요 ?�시 좌표 버튼** ?�릭
        3. **주간 ?�보** �?**?�도 변??차트** ?�인
        
        ### ?���?주간 ?�보 기능
        - **7???�씨 ?�보**: ?�별 최고/최�? ?�도
        - **?�세 ?�보**: ?�씨, ?�도, ?�속, 강수?�률
        - **?�도 차트**: 주간 ?�도 변???�각??
        - **2???�세**: 48?�간 ?�도/?�도/?�속 그래??
        
        ### ?�� 좌표 ?�시
        - **김???�우??*: 37.6199671, 126.726365
        - **?�울**: 37.5665, 126.9780
        - **부??*: 35.1796, 129.0756  
        - **?�주**: 33.4996, 126.5312
        """)

def display_current_weather(weather_data):
    """?�재 ?�씨 ?�보�??�시?�는 ?�수"""
    if weather_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="?���??�도",
                value=f"{weather_data['main']['temp']:.1f}°C",
                delta=f"체감?�도: {weather_data['main']['feels_like']:.1f}°C"
            )
        
        with col2:
            st.metric(
                label="?�� ?�도",
                value=f"{weather_data['main']['humidity']}%"
            )
        
        with col3:
            st.metric(
                label="?���?가?�거�?,
                value=f"{weather_data.get('visibility', 0)/1000:.1f}km"
            )
        
        # 추�? ?�보
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric(
                label="?���??�속",
                value=f"{weather_data['wind'].get('speed', 0)} m/s"
            )
        
        with col5:
            st.metric(
                label="?���?기압",
                value=f"{weather_data['main']['pressure']} hPa"
            )
        
        with col6:
            st.metric(
                label="?���??�씨",
                value=weather_data['weather'][0]['description']
            )

def display_forecast(forecast_data):
    """5???�씨 ?�보�?그래?�로 ?�시?�는 ?�수"""
    if forecast_data:
        # --- 그래?�로 변�?---
        # '?�간'???�덱?�로, '?�도'�?값으�??�는 ??DataFrame ?�성
        chart_data_list = []
        for item in forecast_data['list'][:16]:  # 2?�치(16*3=48?�간) ?�도�?
            chart_data_list.append({
                '?�간': datetime.fromtimestamp(item['dt']),
                '?�도': item['main']['temp']
            })

        chart_df = pd.DataFrame(chart_data_list).set_index('?�간')

        st.subheader("?���?2?�간 기온 변??)
        st.line_chart(chart_df)
        
        # 추�?: ?�도?� ?�속 그래??
        st.subheader("�?2?�간 ?�도 �??���??�속 변??)
        
        # ?�도?� ?�속 ?�이??준�?
        multi_data_list = []
        for item in forecast_data['list'][:16]:
            multi_data_list.append({
                '?�간': datetime.fromtimestamp(item['dt']),
                '?�도(%)': item['main']['humidity'],
                '?�속(m/s)': item['wind'].get('speed', 0)
            })
        
        multi_df = pd.DataFrame(multi_data_list).set_index('?�간')
        st.line_chart(multi_df)
        
        # ?�세 ?�이????(?�을 ???�는 ?�태�?
        with st.expander("?�� ?�세 ?�보 ?�이??보기"):
            detail_list = []
            for item in forecast_data['list'][:16]:
                date_time = datetime.fromtimestamp(item['dt'])
                detail_list.append({
                    '?�짜': date_time.strftime('%m-%d'),
                    '?�간': date_time.strftime('%H:%M'),
                    '?�도': f"{item['main']['temp']:.1f}°C",
                    '?�씨': item['weather'][0]['description'],
                    '?�도': f"{item['main']['humidity']}%",
                    '?�속': f"{item['wind'].get('speed', 0):.1f} m/s"
                })
            
            detail_df = pd.DataFrame(detail_list)
            st.dataframe(detail_df, use_container_width=True)



def display_hourly_ootd_timeline(forecast_data):
    """
    ?�간?��?OOTD ?�?�라?�을 가로로 ?�시?�는 ?�수 (개선 버전)
    """
    st.subheader("?�� ?�간?��?'?�늘 �??��??' ?�?�라??)

    # 1. '?�늘+?�일'???�보 ?�이???�터�?(??많�? ?�간?�)
    now = datetime.now()
    forecasts = []
    
    if 'list' not in forecast_data:
        st.warning("?�간?��??�보 ?�이?��? 불러?????�습?�다.")
        return

    for item in forecast_data['list'][:12]:  # 36?�간 (12�??�간?�)
        item_time = datetime.fromtimestamp(item['dt'])
        # ?�재 ?�간 ?�후???�보�??�택
        if item_time >= now:
            forecasts.append(item)
    
    if not forecasts:
        st.info("?�간?��??�보 ?�보가 ?�습?�다.")
        return

    # 2. 가�??�?�라???�성 (6개로 줄여???�이 ?�보)
    cols = st.columns(min(len(forecasts), 6))  # 최�? 6�?컬럼?�로 줄임
    
    prev_rec = None  # ?�전 ?�간?� 추천???�?�할 변??

    for i, item in enumerate(forecasts[:6]):  # 최�? 6�??�간?��??�시
        with cols[i]:
            # 고정 ?�이 카드 컨테?�너
            st.markdown("""
            <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; 
                        height: 400px; background-color: rgba(255, 255, 255, 0.95); 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0;">
            """, unsafe_allow_html=True)
            
            item_time = datetime.fromtimestamp(item['dt'])
            
            # ?�씨 ?�이??추출
            temp = item['main']['temp']
            feels_like = item['main']['feels_like']
            humidity = item['main']['humidity']
            wind_speed = item['wind'].get('speed', 0)
            weather_main = item['weather'][0]['main']
            weather_desc = item['weather'][0]['description']
            
            # ?�재 ?�간?�??OOTD 추천 받기
            current_rec, accessory_rec = get_ootd_recommendation(feels_like, weather_main)

            # (1) ?�간 ?�시 - 고정 ?�이
            if item_time.date() == now.date():
                time_str = f"?�늘 {item_time.strftime('%H??)}"
            else:
                time_str = f"?�일 {item_time.strftime('%H??)}"
            
            st.markdown(f"""
            <div style="text-align: center; font-weight: bold; font-size: 14px; 
                       margin-bottom: 12px; padding: 8px; height: 35px;
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       border-radius: 8px; color: white; display: flex; align-items: center; justify-content: center;">
                {time_str}
            </div>
            """, unsafe_allow_html=True)
            
            # (2) ?�씨 ?�보 - 고정 ?�이
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px; height: 50px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-weight: bold; font-size: 16px;">?���?{temp:.1f}°C</div>
                <div style="font-size: 12px; color: #666;">체감 {feels_like:.1f}°C</div>
                <div style="font-size: 11px; color: #888;">?�� {humidity}% | ?�� {wind_speed:.1f}m/s</div>
            </div>
            """, unsafe_allow_html=True)
            
            # (3) 변??감�? �?조언 - 고정 ?�이
            advice_html = ""
            if prev_rec and current_rec['level'] < prev_rec['level']:
                colder_item = current_rec['items'].split(',')[0].strip()
                advice_html = f"""
                <div style="background-color: rgba(255, 193, 7, 0.2); padding: 6px; border-radius: 6px; 
                           text-align: center; font-size: 11px; font-weight: bold; height: 35px; 
                           display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                    ??{colder_item} 챙기?�요!
                </div>
                """
            elif prev_rec and current_rec['level'] > prev_rec['level']:
                advice_html = f"""
                <div style="background-color: rgba(144, 202, 249, 0.3); padding: 6px; border-radius: 6px; 
                           text-align: center; font-size: 11px; font-weight: bold; height: 35px; 
                           display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                    ?��??�워?�요. ?�투�?벗으?�요
                </div>
                """
            else:
                advice_html = '<div style="height: 43px; margin-bottom: 8px;"></div>'
            
            st.markdown(advice_html, unsafe_allow_html=True)

            # (4) 추천 ?�차�??�태 - 고정 ?�이
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; height: 35px;
                       background: rgba(103, 126, 234, 0.1); 
                       border-radius: 6px; margin-bottom: 10px; 
                       display: flex; align-items: center; justify-content: center;">
                <strong style="font-size: 12px;">{current_rec['summary']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # (5) 추천 ?�류 - 고정 ?�이
            st.markdown(f"""
            <div style="margin-bottom: 8px; height: 80px; overflow: hidden;">
                <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">?�� 추천 ?�류</div>
                <div style="font-size: 10px; color: #666; line-height: 1.3;">{current_rec['items']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # (6) ?�세?�리 조언 - 고정 ?�이
            accessory_text = accessory_rec if accessory_rec else "?�별??준비물 ?�음"
            st.markdown(f"""
            <div style="height: 60px; overflow: hidden;">
                <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">?�� ?�수 ?�이??/div>
                <div style="font-size: 10px; color: #666; line-height: 1.3;">{accessory_text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 컨테?�너 ?�기
            st.markdown("</div>", unsafe_allow_html=True)

            # ?�음 루프�??�해 ?�재 추천??prev_rec???�??
            prev_rec = current_rec

def main():
    """메인 ?�수"""
    # ?�목
    st.title("?���??�시�??�씨")
    
    # ?�재 ?�치 기반 ?�씨�??�시
    display_location_weather()

if __name__ == "__main__":
    main()
