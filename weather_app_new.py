import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time

# 페이지 설정 - Popper.js 경고 해결을 위한 최적화
st.set_page_config(
    page_title="🌤️ 실시간 날씨 웹앱",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 콘솔 경고 숨기기
st.markdown(
    """
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stDecoration {display:none;}
    </style>
    """, 
    unsafe_allow_html=True
)

# OpenWeather API 설정
API_KEY = "14e3fc348b3e11a20c23806f1c3be844"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ONECALL_URL = "https://api.openweathermap.org/data/2.5/onecall"

# 글로벌 변수
api_status = {"working": None, "last_check": None}

def test_api_connection():
    """API 연결 테스트 - 제공된 코드 구조 사용"""
    global api_status
    
    # 캐시된 결과가 있고 5분 이내라면 재사용
    if (api_status["last_check"] and 
        time.time() - api_status["last_check"] < 300):
        return api_status["working"]
    
    # 제공된 코드와 동일한 방식으로 API 테스트
    city = "Seoul"
    apikey = API_KEY
    lang = "kr"
    
    api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        result = requests.get(api, timeout=10)
        
        if result.status_code == 200:
            # 실제 데이터 파싱 테스트
            data = json.loads(result.text)
            if 'main' in data and 'temp' in data['main']:
                api_status["working"] = True
                api_status["last_check"] = time.time()
                return True
        
        api_status["working"] = False
        api_status["last_check"] = time.time()
        return False
        
    except:
        api_status["working"] = False
        api_status["last_check"] = time.time()
        return False

def get_weather_data(city_name, country_code=None):
    """현재 날씨 정보 가져오기 - 제공된 코드 구조 사용"""
    # 도시 쿼리 구성
    if country_code:
        city = f"{city_name},{country_code}"
    else:
        city = city_name
    
    apikey = API_KEY
    lang = "kr"
    
    # 제공된 코드와 동일한 API URL 구성
    api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        # 제공된 코드와 동일한 방식으로 요청
        result = requests.get(api, timeout=15)
        
        if result.status_code == 200:
            # JSON 파싱 (제공된 코드와 동일)
            data = json.loads(result.text)
            return data
        elif result.status_code == 404:
            st.error(f"도시 '{city}'를 찾을 수 없습니다. 도시명을 확인해주세요.")
            return None
        elif result.status_code == 401:
            st.error("API 키가 유효하지 않습니다.")
            return None
        else:
            st.error(f"API 오류: {result.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.warning(f"네트워크 오류: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"데이터 파싱 오류: {e}")
        return None

def get_forecast_data(city_name, country_code=None):
    """5일 날씨 예보 가져오기 - 제공된 코드 구조 사용"""
    # 도시 쿼리 구성
    if country_code:
        city = f"{city_name},{country_code}"
    else:
        city = city_name
    
    apikey = API_KEY
    lang = "kr"
    
    # 예보 API URL 구성 (제공된 코드 방식)
    api = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        # 제공된 코드와 동일한 방식으로 요청
        result = requests.get(api, timeout=15)
        
        if result.status_code == 200:
            # JSON 파싱 (제공된 코드와 동일)
            data = json.loads(result.text)
            return data
        else:
            return None
            
    except:
        return None

def create_dummy_data(city_name="서울"):
    """테스트용 더미 데이터 생성"""
    return {
        'name': city_name,
        'sys': {
            'country': 'KR',
            'sunrise': int(datetime.now().replace(hour=6, minute=30).timestamp()),
            'sunset': int(datetime.now().replace(hour=18, minute=45).timestamp())
        },
        'main': {
            'temp': 18.5,
            'feels_like': 17.2,
            'temp_min': 15.0,
            'temp_max': 22.0,
            'pressure': 1013,
            'humidity': 65
        },
        'weather': [{'description': '맑음', 'main': 'Clear', 'icon': '01d'}],
        'wind': {'speed': 3.2, 'deg': 180},
        'clouds': {'all': 20},
        'visibility': 10000,
        'coord': {'lat': 37.5665, 'lon': 126.9780}
    }

def create_dummy_forecast():
    """테스트용 예보 데이터 생성"""
    base_time = datetime.now().timestamp()
    forecast_list = []
    
    weather_options = ['맑음', '구름많음', '흐림', '비', '눈']
    temp_base = 18
    
    for i in range(40):  # 5일 * 8회 (3시간 간격)
        forecast_list.append({
            'dt': int(base_time + i * 10800),  # 3시간 간격
            'main': {
                'temp': temp_base + (i % 8 - 4) * 2,  # 온도 변화
                'humidity': 60 + (i % 5) * 5,
                'pressure': 1010 + (i % 3) * 3
            },
            'weather': [{'description': weather_options[i % len(weather_options)]}],
            'wind': {'speed': 2 + (i % 3)},
            'pop': (i % 10) / 10  # 강수 확률
        })
    
    return {'list': forecast_list}

def display_weather_metrics(weather_data):
    """날씨 메트릭 표시"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌡️ 현재 온도",
            value=f"{weather_data['main']['temp']:.1f}°C",
            delta=f"체감 {weather_data['main']['feels_like']:.1f}°C"
        )
    
    with col2:
        st.metric(
            label="💧 습도",
            value=f"{weather_data['main']['humidity']}%"
        )
    
    with col3:
        st.metric(
            label="🌬️ 바람",
            value=f"{weather_data['wind'].get('speed', 0):.1f} m/s"
        )
    
    with col4:
        st.metric(
            label="🌡️ 기압",
            value=f"{weather_data['main']['pressure']} hPa"
        )

def display_additional_info(weather_data):
    """추가 날씨 정보 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 상세 정보")
        st.write(f"**최고 온도:** {weather_data['main']['temp_max']:.1f}°C")
        st.write(f"**최저 온도:** {weather_data['main']['temp_min']:.1f}°C")
        st.write(f"**가시거리:** {weather_data.get('visibility', 0)/1000:.1f} km")
        st.write(f"**구름량:** {weather_data['clouds']['all']}%")
    
    with col2:
        st.subheader("🌅 일출/일몰")
        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
        sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
        st.write(f"**일출:** {sunrise.strftime('%H:%M')}")
        st.write(f"**일몰:** {sunset.strftime('%H:%M')}")
        st.write(f"**조회 시간:** {datetime.now().strftime('%H:%M:%S')}")

def display_forecast_table(forecast_data):
    """예보 테이블 표시"""
    if not forecast_data:
        return
    
    st.subheader("📅 5일 날씨 예보")
    
    forecast_list = []
    for item in forecast_data['list'][:24]:  # 24시간 예보만 표시
        dt = datetime.fromtimestamp(item['dt'])
        forecast_list.append({
            '날짜': dt.strftime('%m/%d'),
            '시간': dt.strftime('%H:%M'),
            '온도': f"{item['main']['temp']:.1f}°C",
            '날씨': item['weather'][0]['description'],
            '습도': f"{item['main']['humidity']}%",
            '바람': f"{item['wind'].get('speed', 0):.1f} m/s",
            '강수확률': f"{item.get('pop', 0)*100:.0f}%"
        })
    
    df = pd.DataFrame(forecast_list)
    st.dataframe(df, use_container_width=True, height=400)

def show_api_status():
    """API 상태 표시"""
    if test_api_connection():
        st.success("🟢 OpenWeather API 연결 정상")
        return True
    else:
        st.error("🔴 OpenWeather API 연결 실패")
        with st.expander("❓ API 문제 해결 방법"):
            st.markdown("""
            ### 🔧 API 키 문제 해결
            
            **1. API 키 확인**
            - OpenWeatherMap 계정 로그인: https://home.openweathermap.org/api_keys
            - API 키 상태 확인 (Active/Inactive)
            
            **2. 새 API 키 발급**
            - "Create Key" 버튼 클릭
            - 키 이름 입력 후 생성
            - 이메일 인증 완료 필요
            
            **3. 활성화 대기**
            - 새 키는 최대 2시간 활성화 시간 필요
            - 무료 계정 제한: 월 1,000,000회 호출
            
            **4. 현재 사용 중인 키**
            ```
            {API_KEY}
            ```
            """)
        return False

def main():
    """메인 애플리케이션"""
    # 헤더
    st.title("🌤️ 실시간 날씨 웹앱")
    st.markdown("**OpenWeather API 기반 날씨 정보 서비스**")
    
    # API 상태 확인
    api_working = show_api_status()
    
    st.divider()
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🔍 날씨 검색")
        
        # 검색 방법 선택
        search_type = st.radio(
            "검색 방법:",
            ["🏙️ 인기 도시", "✍️ 직접 입력"],
            horizontal=True
        )
        
        # 인기 도시 목록
        popular_cities = {
            "🇰🇷 한국": [
                ("서울", "KR"), ("부산", "KR"), ("대구", "KR"), 
                ("인천", "KR"), ("광주", "KR"), ("대전", "KR")
            ],
            "🌏 아시아": [
                ("도쿄", "JP"), ("오사카", "JP"), ("베이징", "CN"), 
                ("상하이", "CN"), ("방콕", "TH"), ("싱가포르", "SG")
            ],
            "🌍 유럽/미주": [
                ("런던", "GB"), ("파리", "FR"), ("뉴욕", "US"), 
                ("로스앤젤레스", "US"), ("시드니", "AU")
            ]
        }
        
        if search_type == "🏙️ 인기 도시":
            # 지역 선택
            region = st.selectbox("지역 선택:", list(popular_cities.keys()))
            
            # 도시 선택
            city_options = [f"{city}" for city, code in popular_cities[region]]
            selected_city_name = st.selectbox("도시 선택:", city_options)
            
            # 선택된 도시의 국가 코드 찾기
            city_name = selected_city_name
            country_code = None
            for city, code in popular_cities[region]:
                if city == selected_city_name:
                    country_code = code
                    break
        else:
            # 직접 입력
            city_name = st.text_input("🏙️ 도시명:", placeholder="예: Seoul, Tokyo, London")
            country_code = st.text_input("🏳️ 국가 코드 (선택):", placeholder="예: KR, JP, US")
            
            if country_code == "":
                country_code = None
        
        # 검색 버튼
        search_button = st.button("🔍 날씨 조회", type="primary", use_container_width=True)
        
        # 새로고침 버튼
        if st.button("🔄 API 상태 새로고침", use_container_width=True):
            api_status["last_check"] = None  # 캐시 초기화
            st.rerun()
    
    # 메인 컨텐츠
    if search_button and city_name:
        with st.spinner("🔄 날씨 정보를 가져오는 중..."):
            # 날씨 데이터 가져오기
            weather_data = None
            forecast_data = None
            
            if api_working:
                weather_data = get_weather_data(city_name, country_code)
                if weather_data:
                    forecast_data = get_forecast_data(city_name, country_code)
            
            # 데이터가 없으면 더미 데이터 사용
            if not weather_data:
                if api_working:
                    st.warning("⚠️ 해당 도시의 날씨 정보를 찾을 수 없습니다. 테스트 데이터를 표시합니다.")
                else:
                    st.info("🧪 **테스트 모드**: API 연결 문제로 샘플 데이터를 표시합니다.")
                
                weather_data = create_dummy_data(city_name)
                forecast_data = create_dummy_forecast()
            
            # 날씨 정보 표시
            if weather_data:
                # 도시 정보
                st.success(f"📍 **{weather_data['name']}, {weather_data['sys']['country']}**")
                
                # 현재 날씨 상태
                st.subheader(f"🌤️ {weather_data['weather'][0]['description']}")
                
                # 메트릭 표시
                display_weather_metrics(weather_data)
                
                st.divider()
                
                # 상세 정보
                display_additional_info(weather_data)
                
                st.divider()
                
                # 예보 정보
                if forecast_data:
                    display_forecast_table(forecast_data)
    
    # 초기 화면
    else:
        st.info("👆 **사이드바에서 도시를 선택하고 '날씨 조회' 버튼을 클릭해주세요!**")
        
        # 앱 소개
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✨ 주요 기능")
            st.markdown("""
            - 🌡️ **실시간 날씨**: 온도, 습도, 바람, 기압
            - 📅 **5일 예보**: 3시간 간격 상세 예보
            - 🌍 **전 세계 지원**: 주요 도시 및 직접 검색
            - 📱 **반응형 디자인**: 모바일/데스크톱 최적화
            """)
        
        with col2:
            st.subheader("🚀 사용법")
            st.markdown("""
            1. **사이드바**에서 검색 방법 선택
            2. **도시 선택** 또는 직접 입력
            3. **'날씨 조회'** 버튼 클릭
            4. **실시간 날씨 정보** 확인
            """)
        
        # API 키 정보 (개발자용)
        with st.expander("🔧 개발자 정보"):
            st.code(f"""
# 현재 사용 중인 API 키
API_KEY = "{API_KEY}"

# API 상태
연결 상태: {"✅ 정상" if api_working else "❌ 오류"}
마지막 확인: {datetime.fromtimestamp(api_status["last_check"]).strftime("%H:%M:%S") if api_status["last_check"] else "미확인"}
            """)

if __name__ == "__main__":
    main()