import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# OpenWeather API 설정
API_KEY = "14e3fc348b3e11a20c23806f1c3be844"  # 여기에 유효한 API 키를 입력하세요
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# 테스트용 더미 데이터
DUMMY_WEATHER_DATA = {
    'name': '서울',
    'sys': {'country': 'KR', 'sunrise': 1729737600, 'sunset': 1729777200},
    'main': {
        'temp': 18.5,
        'feels_like': 17.2,
        'temp_min': 15.0,
        'temp_max': 22.0,
        'pressure': 1013,
        'humidity': 65
    },
    'weather': [{'description': '맑음', 'main': 'Clear'}],
    'wind': {'speed': 3.2},
    'clouds': {'all': 20},
    'visibility': 10000
}

# 페이지 설정
st.set_page_config(
    page_title="날씨 웹앱",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_api_key():
    """API 키 유효성 검사"""
    if API_KEY == "YOUR_API_KEY_HERE" or len(API_KEY) != 32:
        return False
    
    try:
        params = {'q': 'Seoul', 'appid': API_KEY}
        response = requests.get(BASE_URL, params=params, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_weather_data(city_name, country_code=None):
    """현재 날씨 정보를 가져오는 함수"""
    if not check_api_key():
        st.warning("⚠️ API 키가 설정되지 않았거나 유효하지 않습니다. 테스트 데이터를 표시합니다.")
        return DUMMY_WEATHER_DATA
    
    if country_code:
        query = f"{city_name},{country_code}"
    else:
        query = city_name
    
    params = {
        'q': query,
        'appid': API_KEY,
        'units': 'metric',  # 섭씨 온도
        'lang': 'kr'  # 한국어
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"날씨 데이터를 가져오는데 실패했습니다: {e}")
        st.info("테스트 데이터를 표시합니다.")
        return DUMMY_WEATHER_DATA

def get_forecast_data(city_name, country_code=None):
    """5일 날씨 예보를 가져오는 함수"""
    if not check_api_key():
        # 더미 예보 데이터 생성
        dummy_forecast = {
            'list': []
        }
        base_time = datetime.now().timestamp()
        for i in range(8):  # 8개의 예보 데이터
            dummy_forecast['list'].append({
                'dt': int(base_time + i * 10800),  # 3시간 간격
                'main': {
                    'temp': 18 + (i % 3) * 2,
                    'humidity': 60 + (i % 4) * 5
                },
                'weather': [{'description': ['맑음', '구름많음', '흐림'][i % 3]}],
                'wind': {'speed': 2 + (i % 2)}
            })
        return dummy_forecast
    
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
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"예보 데이터를 가져오는데 실패했습니다: {e}")
        return None

def display_current_weather(weather_data):
    """현재 날씨 정보를 표시하는 함수"""
    if weather_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🌡️ 온도",
                value=f"{weather_data['main']['temp']:.1f}°C",
                delta=f"체감온도: {weather_data['main']['feels_like']:.1f}°C"
            )
        
        with col2:
            st.metric(
                label="💧 습도",
                value=f"{weather_data['main']['humidity']}%"
            )
        
        with col3:
            st.metric(
                label="👁️ 가시거리",
                value=f"{weather_data.get('visibility', 0)/1000:.1f}km"
            )
        
        # 추가 정보
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric(
                label="🌬️ 풍속",
                value=f"{weather_data['wind'].get('speed', 0)} m/s"
            )
        
        with col5:
            st.metric(
                label="🌡️ 기압",
                value=f"{weather_data['main']['pressure']} hPa"
            )
        
        with col6:
            st.metric(
                label="🌤️ 날씨",
                value=weather_data['weather'][0]['description']
            )

def display_forecast(forecast_data):
    """5일 날씨 예보를 표시하는 함수"""
    if forecast_data:
        st.subheader("📅 5일 날씨 예보")
        
        # 데이터 처리
        forecast_list = []
        for item in forecast_data['list']:
            date_time = datetime.fromtimestamp(item['dt'])
            forecast_list.append({
                '날짜': date_time.strftime('%m-%d'),
                '시간': date_time.strftime('%H:%M'),
                '온도': f"{item['main']['temp']:.1f}°C",
                '날씨': item['weather'][0]['description'],
                '습도': f"{item['main']['humidity']}%",
                '풍속': f"{item['wind'].get('speed', 0):.1f} m/s"
            })
        
        # DataFrame으로 변환하여 표시
        df = pd.DataFrame(forecast_list[:20])  # 처음 20개 항목만 표시
        st.dataframe(df, use_container_width=True)

def api_key_setup():
    """API 키 설정 가이드"""
    st.error("🔑 API 키 설정이 필요합니다!")
    
    with st.expander("📋 API 키 설정 방법", expanded=True):
        st.markdown("""
        ### 🔗 OpenWeather API 키 발급받기
        
        1. **OpenWeatherMap 웹사이트 방문**: https://openweathermap.org/
        2. **Sign Up** 또는 **Sign In** 클릭
        3. **API Keys** 메뉴로 이동
        4. **Create Key** 버튼 클릭하여 새 API 키 생성
        5. **이메일 인증** 완료 (매우 중요!)
        
        ### ⚠️ 주의사항
        - 새로 생성한 API 키는 **활성화까지 최대 2시간** 소요
        - 무료 계정은 **분당 60회, 월 1,000,000회** 요청 제한
        - API 키는 32자리 영숫자 조합
        
        ### 💻 API 키 설정 방법
        1. `weather_app.py` 파일을 열기
        2. 상단의 `API_KEY = "YOUR_API_KEY_HERE"` 부분 찾기
        3. `YOUR_API_KEY_HERE`를 발급받은 API 키로 교체
        4. 파일 저장 후 웹앱 새로고침
        
        ### 📝 예시
        ```python
        API_KEY = "abcd1234efgh5678ijkl9012mnop3456"  # 실제 발급받은 키로 교체
        ```
        """)

def main():
    """메인 함수"""
    st.title("🌤️ 날씨 웹앱")
    st.markdown("OpenWeather API를 사용한 실시간 날씨 정보")
    
    # API 키 확인
    if not check_api_key():
        api_key_setup()
        st.divider()
        st.info("🧪 **테스트 모드**: API 키가 설정되지 않아 샘플 데이터를 표시합니다.")
    
    # 사이드바
    st.sidebar.header("🔍 도시 검색")
    
    # 인기 도시 목록
    popular_cities = [
        ("서울", "KR"),
        ("부산", "KR"),
        ("대구", "KR"),
        ("인천", "KR"),
        ("광주", "KR"),
        ("대전", "KR"),
        ("울산", "KR"),
        ("도쿄", "JP"),
        ("오사카", "JP"),
        ("뉴욕", "US"),
        ("런던", "GB"),
        ("파리", "FR"),
        ("베이징", "CN"),
        ("상하이", "CN")
    ]
    
    # 도시 선택 방법
    search_method = st.sidebar.radio(
        "검색 방법을 선택하세요:",
        ("인기 도시에서 선택", "직접 입력")
    )
    
    if search_method == "인기 도시에서 선택":
        city_options = [f"{city} ({code})" for city, code in popular_cities]
        selected_city = st.sidebar.selectbox("도시를 선택하세요:", city_options)
        
        # 선택된 도시 파싱
        city_name = selected_city.split(" (")[0]
        country_code = selected_city.split("(")[1].split(")")[0]
    else:
        city_name = st.sidebar.text_input("도시명을 입력하세요:", placeholder="예: Seoul")
        country_code = st.sidebar.text_input("국가 코드 (선택사항):", placeholder="예: KR")
        
        if not country_code:
            country_code = None
    
    # 검색 버튼
    if st.sidebar.button("🔍 날씨 조회", type="primary"):
        if city_name:
            with st.spinner("날씨 정보를 가져오는 중..."):
                # 현재 날씨 정보 가져오기
                weather_data = get_weather_data(city_name, country_code)
                
                if weather_data:
                    # 도시 정보 표시
                    st.success(f"📍 {weather_data['name']}, {weather_data['sys']['country']}")
                    
                    # 현재 날씨 표시
                    st.subheader("🌡️ 현재 날씨")
                    display_current_weather(weather_data)
                    
                    # 상세 정보
                    with st.expander("📊 상세 날씨 정보"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**기본 정보**")
                            st.write(f"• 최고 온도: {weather_data['main']['temp_max']:.1f}°C")
                            st.write(f"• 최저 온도: {weather_data['main']['temp_min']:.1f}°C")
                            st.write(f"• 구름량: {weather_data['clouds']['all']}%")
                        
                        with col2:
                            st.write("**시간 정보**")
                            sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
                            sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
                            st.write(f"• 일출: {sunrise.strftime('%H:%M')}")
                            st.write(f"• 일몰: {sunset.strftime('%H:%M')}")
                            st.write(f"• 조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 5일 예보
                    forecast_data = get_forecast_data(city_name, country_code)
                    if forecast_data:
                        display_forecast(forecast_data)
        else:
            st.sidebar.warning("도시명을 입력해주세요!")
    
    # 초기 화면 정보
    if 'weather_searched' not in st.session_state:
        st.info("👆 사이드바에서 도시를 선택하고 '날씨 조회' 버튼을 클릭해주세요!")
        
        # 사용법 안내
        with st.expander("📖 사용법 안내"):
            st.markdown("""
            ### 🌤️ 날씨 웹앱 사용법
            
            1. **API 키 설정 (중요!)**
               - OpenWeatherMap에서 무료 API 키 발급
               - `weather_app.py` 파일의 API_KEY 변수에 입력
            
            2. **사이드바에서 검색 방법 선택**
               - 인기 도시에서 선택: 미리 설정된 인기 도시 목록에서 선택
               - 직접 입력: 원하는 도시명을 직접 입력
            
            3. **도시 정보 입력**
               - 도시명: 검색하고 싶은 도시의 이름 (한글 또는 영어)
               - 국가 코드: 더 정확한 검색을 위한 국가 코드 (선택사항)
            
            4. **날씨 조회**
               - '🔍 날씨 조회' 버튼을 클릭하여 실시간 날씨 정보 확인
            
            ### 🔍 주요 기능
            - **실시간 날씨**: 현재 온도, 습도, 풍속, 기압 등
            - **5일 예보**: 향후 5일간의 날씨 예보
            - **상세 정보**: 일출/일몰 시간, 체감온도 등
            """)

if __name__ == "__main__":
    main()