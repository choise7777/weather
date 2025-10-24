import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time

# 페이지 설정 - 경고 최소화
st.set_page_config(
    page_title="🌤️ 날씨 앱",
    page_icon="🌤️",
    layout="centered",  # wide에서 centered로 변경하여 안정성 향상
    initial_sidebar_state="auto"
)

# CSS로 불필요한 요소 숨기기 + 위치 기능 추가
st.markdown("""
<style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stDecoration {display:none;}
    header {visibility: hidden;}
    .css-1rs6os {display:none;}
    .css-17eq0hr {display:none;}
</style>

<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // Streamlit으로 위도/경도 전달
            window.parent.postMessage({
                type: 'location',
                latitude: lat,
                longitude: lon
            }, '*');
        }, function(error) {
            console.log("위치 정보를 가져올 수 없습니다: " + error.message);
        });
    } else {
        console.log("이 브라우저는 위치 서비스를 지원하지 않습니다.");
    }
}
</script>
""", unsafe_allow_html=True)

# API 설정
API_KEY = "14e3fc348b3e11a20c23806f1c3be844"

def get_weather_data(city_name):
    """제공된 코드 구조로 날씨 데이터 가져오기"""
    city = city_name
    apikey = API_KEY
    lang = "kr"
    
    api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        result = requests.get(api, timeout=10)
        if result.status_code == 200:
            data = json.loads(result.text)
            return data
        else:
            return None
    except:
        return None

def get_weather_by_coordinates(lat, lon):
    """위도/경도로 현재 날씨 가져오기"""
    apikey = API_KEY
    lang = "kr"
    
    api = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        result = requests.get(api, timeout=10)
        if result.status_code == 200:
            data = json.loads(result.text)
            return data
        else:
            return None
    except:
        return None

def get_forecast_data(city_name):
    """예보 데이터 가져오기"""
    city = city_name
    apikey = API_KEY
    lang = "kr"
    
    api = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        result = requests.get(api, timeout=10)
        if result.status_code == 200:
            data = json.loads(result.text)
            return data
        else:
            return None
    except:
        return None

def get_forecast_by_coordinates(lat, lon):
    """위도/경도로 예보 데이터 가져오기"""
    apikey = API_KEY
    lang = "kr"
    
    api = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&lang={lang}&units=metric"
    
    try:
        result = requests.get(api, timeout=10)
        if result.status_code == 200:
            data = json.loads(result.text)
            return data
        else:
            return None
    except:
        return None

def get_weekly_weather(lat, lon):
    """7일 날씨 예보 (OneCall API 사용)"""
    apikey = API_KEY
    
    # OneCall API - 7일 예보 제공
    api = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={apikey}&lang=kr&units=metric&exclude=minutely,alerts"
    
    try:
        result = requests.get(api, timeout=10)
        if result.status_code == 200:
            data = json.loads(result.text)
            return data
        else:
            # OneCall API가 실패하면 5일 예보로 대체
            return get_forecast_by_coordinates(lat, lon)
    except:
        return get_forecast_by_coordinates(lat, lon)

def process_weekly_forecast(forecast_data, is_onecall=False):
    """주간 예보 데이터 처리"""
    weekly_data = []
    
    if is_onecall and 'daily' in forecast_data:
        # OneCall API 데이터 처리
        for day in forecast_data['daily'][:7]:
            date = datetime.fromtimestamp(day['dt'])
            weekly_data.append({
                '날짜': date.strftime('%m/%d (%a)'),
                '날씨': day['weather'][0]['description'],
                '최고온도': f"{day['temp']['max']:.0f}°C",
                '최저온도': f"{day['temp']['min']:.0f}°C",
                '습도': f"{day['humidity']}%",
                '강수확률': f"{day.get('pop', 0)*100:.0f}%"
            })
    else:
        # 5일 예보 데이터를 일별로 그룹화
        if 'list' in forecast_data:
            daily_data = {}
            
            for item in forecast_data['list']:
                date = datetime.fromtimestamp(item['dt'])
                date_key = date.strftime('%Y-%m-%d')
                
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        'temps': [],
                        'humidity': [],
                        'weather': item['weather'][0]['description'],
                        'pop': item.get('pop', 0),
                        'date': date
                    }
                
                daily_data[date_key]['temps'].append(item['main']['temp'])
                daily_data[date_key]['humidity'].append(item['main']['humidity'])
            
            # 일별 데이터를 정리
            for date_key, data in list(daily_data.items())[:7]:
                weekly_data.append({
                    '날짜': data['date'].strftime('%m/%d (%a)'),
                    '날씨': data['weather'],
                    '최고온도': f"{max(data['temps']):.0f}°C",
                    '최저온도': f"{min(data['temps']):.0f}°C",
                    '습도': f"{sum(data['humidity'])//len(data['humidity'])}%",
                    '강수확률': f"{data['pop']*100:.0f}%"
                })
    
    return weekly_data

def display_weather_info(weather_data):
    """날씨 정보 표시 함수"""
    # 기본 정보
    st.success(f"📍 {weather_data['name']}, {weather_data['sys']['country']}")
    
    # 온도 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🌡️ 현재 온도", f"{weather_data['main']['temp']:.1f}°C")
    
    with col2:
        st.metric("💧 습도", f"{weather_data['main']['humidity']}%")
    
    with col3:
        st.metric("🌬️ 바람", f"{weather_data['wind']['speed']:.1f} m/s")
    
    # 날씨 상태
    st.subheader(f"🌤️ {weather_data['weather'][0]['description']}")
    
    # 상세 정보
    with st.expander("📊 상세 정보 보기"):
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.write(f"**체감온도:** {weather_data['main']['feels_like']:.1f}°C")
            st.write(f"**최고온도:** {weather_data['main']['temp_max']:.1f}°C")
            st.write(f"**최저온도:** {weather_data['main']['temp_min']:.1f}°C")
            st.write(f"**기압:** {weather_data['main']['pressure']} hPa")
        
        with detail_col2:
            st.write(f"**구름량:** {weather_data['clouds']['all']}%")
            st.write(f"**가시거리:** {weather_data.get('visibility', 0)/1000:.1f} km")
            
            # 일출/일몰
            sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
            sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
            st.write(f"**일출:** {sunrise.strftime('%H:%M')}")
            st.write(f"**일몰:** {sunset.strftime('%H:%M')}")

def display_weekly_forecast(weekly_data):
    """주간 예보 표시 함수"""
    st.subheader("📅 7일 날씨 예보")
    
    # OneCall API 데이터인지 확인
    is_onecall = 'daily' in weekly_data if isinstance(weekly_data, dict) else False
    
    if is_onecall:
        forecast_items = process_weekly_forecast(weekly_data, True)
    else:
        forecast_items = process_weekly_forecast(weekly_data, False)
    
    if forecast_items:
        df = pd.DataFrame(forecast_items)
        st.dataframe(df, use_container_width=True, height=300)
        
        # 주간 날씨 차트
        if len(forecast_items) > 0:
            st.subheader("📈 주간 온도 변화")
            
            # 온도 데이터 추출 (숫자만)
            max_temps = [float(item['최고온도'].replace('°C', '')) for item in forecast_items]
            min_temps = [float(item['최저온도'].replace('°C', '')) for item in forecast_items]
            dates = [item['날짜'] for item in forecast_items]
            
            # 차트 데이터 준비
            chart_data = pd.DataFrame({
                '날짜': dates,
                '최고온도': max_temps,
                '최저온도': min_temps
            })
            
            st.line_chart(chart_data.set_index('날짜'))
    else:
        st.warning("주간 예보 데이터를 처리할 수 없습니다.")

def main():
    # 제목
    st.title("🌤️ 실시간 날씨")
    
    # 상단 기능 탭
    tab1, tab2 = st.tabs(["🔍 도시 검색", "📍 현재 위치"])
    
    with tab1:
        # 도시 입력
        col1, col2 = st.columns([3, 1])
        
        with col1:
            city_input = st.text_input("도시명", placeholder="도시명을 입력하세요 (예: Seoul, Tokyo, London)", label_visibility="collapsed")
        
        with col2:
            search_btn = st.button("🔍 검색", type="primary")
        
        # 인기 도시 버튼들
        st.markdown("**인기 도시:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🇰🇷 서울", key="seoul"):
                city_input = "Seoul"
                search_btn = True
        with col2:
            if st.button("🇯🇵 도쿄", key="tokyo"):
                city_input = "Tokyo"
                search_btn = True
        with col3:
            if st.button("🇬🇧 런던", key="london"):
                city_input = "London"
                search_btn = True
        with col4:
            if st.button("🇺🇸 뉴욕", key="newyork"):
                city_input = "New York"
                search_btn = True
        with col5:
            if st.button("🇫🇷 파리", key="paris"):
                city_input = "Paris"
                search_btn = True
    
    with tab2:
        st.markdown("### 📍 현재 위치 기반 날씨")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("브라우저에서 위치 권한을 허용하고 좌표를 입력하세요.")
        
        with col2:
            location_btn = st.button("📍 내 위치 날씨", type="primary")
        
        # 수동 좌표 입력 (테스트용)
        st.markdown("**또는 직접 좌표 입력:**")
        coord_col1, coord_col2, coord_col3 = st.columns([1, 1, 1])
        
        with coord_col1:
            manual_lat = st.number_input("위도", value=37.5665, format="%.4f")
        
        with coord_col2:
            manual_lon = st.number_input("경도", value=126.9780, format="%.4f")
        
        with coord_col3:
            manual_search = st.button("🎯 좌표로 검색")
        
        # 현재 위치 날씨 표시
        if location_btn or manual_search:
            lat, lon = manual_lat, manual_lon
            
            with st.spinner("현재 위치의 날씨 정보 로딩중..."):
                weather_data = get_weather_by_coordinates(lat, lon)
                
                if weather_data:
                    display_weather_info(weather_data)
                    
                    # 주간 날씨 예보
                    st.divider()
                    weekly_data = get_weekly_weather(lat, lon)
                    if weekly_data:
                        display_weekly_forecast(weekly_data)
                else:
                    st.error("❌ 현재 위치의 날씨 정보를 가져올 수 없습니다.")
        
        return  # tab2에서는 여기서 함수 종료
    
    # tab1의 날씨 정보 표시
    if search_btn and city_input:
        with st.spinner("날씨 정보 로딩중..."):
            weather_data = get_weather_data(city_input)
            
            if weather_data:
                display_weather_info(weather_data)
                
                # 5일 예보 정보
                forecast_data = get_forecast_data(city_input)
                if forecast_data:
                    st.divider()
                    st.subheader("📅 5일 예보")
                    
                    forecast_items = []
                    for item in forecast_data['list'][:15]:  # 15개 항목만
                        dt = datetime.fromtimestamp(item['dt'])
                        forecast_items.append({
                            '날짜/시간': dt.strftime('%m/%d %H:%M'),
                            '온도': f"{item['main']['temp']:.0f}°C",
                            '날씨': item['weather'][0]['description'],
                            '습도': f"{item['main']['humidity']}%"
                        })
                    
                    df = pd.DataFrame(forecast_items)
                    st.dataframe(df, use_container_width=True, height=300)
            
            else:
                st.error("❌ 날씨 정보를 가져올 수 없습니다. 도시명을 확인해주세요.")
    
    # 초기 화면 (탭1에서만 표시)
    if not search_btn:
        st.info("👆 위에서 도시명을 입력하거나 인기 도시 버튼을 클릭하세요!")
        
        # 사용법
        st.markdown("""
        ### 📖 사용법
        **🔍 도시 검색 탭:**
        1. 상단 입력창에 **도시명** 입력 (영어)
        2. **🔍 검색** 버튼 클릭
        3. 또는 **인기 도시 버튼** 클릭
        4. **5일 예보** 확인 가능
        
        **📍 현재 위치 탭:**
        1. 브라우저 위치 권한 허용
        2. **📍 내 위치 날씨** 버튼 클릭
        3. 또는 **직접 좌표 입력** 후 검색
        4. **7일 주간 예보** 및 **온도 차트** 확인
        
        **지원 지역:** 전 세계 모든 지역 🌍
        """)

if __name__ == "__main__":
    main()