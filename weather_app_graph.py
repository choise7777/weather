import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# OpenWeather API 설정
API_KEY = "14e3fc348b3e11a20c23806f1c3be844"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(
    page_title="날씨 웹앱 - 그래프 버전",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_weather_data(city_name, country_code=None):
    """현재 날씨 정보를 가져오는 함수"""
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
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"날씨 데이터를 가져오는데 실패했습니다: {e}")
        return None

def get_forecast_data(city_name, country_code=None):
    """5일 날씨 예보를 가져오는 함수"""
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
                label="🌬️ 풍속",
                value=f"{weather_data['wind'].get('speed', 0):.1f} m/s"
            )

def display_forecast_graphs(forecast_data):
    """예보 데이터를 다양한 그래프로 표시"""
    if not forecast_data:
        return
    
    # 데이터 준비
    times = []
    temps = []
    humidity = []
    wind_speeds = []
    weather_desc = []
    
    for item in forecast_data['list'][:16]:  # 2일치 데이터
        times.append(datetime.fromtimestamp(item['dt']))
        temps.append(item['main']['temp'])
        humidity.append(item['main']['humidity'])
        wind_speeds.append(item['wind'].get('speed', 0))
        weather_desc.append(item['weather'][0]['description'])
    
    # 1. Streamlit 라인 차트 (요청하신 방식)
    st.subheader("🌡️ 2일간 기온 변화 (Streamlit 차트)")
    
    chart_data_list = []
    for i in range(len(times)):
        chart_data_list.append({
            '시간': times[i],
            '온도': temps[i]
        })
    
    chart_df = pd.DataFrame(chart_data_list).set_index('시간')
    st.line_chart(chart_df)
    
    # 2. Matplotlib 그래프 (더 상세한 그래프)
    st.subheader("📊 상세 기상 그래프 (Matplotlib)")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 온도 그래프
    ax1.plot(times, temps, 'r-o', linewidth=2, markersize=4)
    ax1.set_title('Temperature Change (2 Days)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Temperature (°C)')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax1.tick_params(axis='x', rotation=45)
    
    # 습도 그래프
    ax2.plot(times, humidity, 'b-s', linewidth=2, markersize=4)
    ax2.set_title('Humidity Change (2 Days)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Humidity (%)')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax2.tick_params(axis='x', rotation=45)
    
    # 풍속 그래프
    ax3.plot(times, wind_speeds, 'g-^', linewidth=2, markersize=4)
    ax3.set_title('Wind Speed Change (2 Days)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Wind Speed (m/s)')
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax3.tick_params(axis='x', rotation=45)
    
    # 종합 그래프 (온도 + 습도)
    ax4_twin = ax4.twinx()
    
    line1 = ax4.plot(times, temps, 'r-o', label='Temperature (°C)', linewidth=2)
    line2 = ax4_twin.plot(times, humidity, 'b-s', label='Humidity (%)', linewidth=2)
    
    ax4.set_title('Temperature & Humidity Combined', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Temperature (°C)', color='red')
    ax4_twin.set_ylabel('Humidity (%)', color='blue')
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    ax4.tick_params(axis='x', rotation=45)
    
    # 범례 추가
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='upper left')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 3. 상세 데이터 표 (접을 수 있는 형태)
    with st.expander("📊 상세 예보 데이터 보기"):
        detail_list = []
        for i in range(len(times)):
            detail_list.append({
                '날짜': times[i].strftime('%m-%d'),
                '시간': times[i].strftime('%H:%M'),
                '온도': f"{temps[i]:.1f}°C",
                '날씨': weather_desc[i],
                '습도': f"{humidity[i]}%",
                '풍속': f"{wind_speeds[i]:.1f} m/s"
            })
        
        detail_df = pd.DataFrame(detail_list)
        st.dataframe(detail_df, use_container_width=True)

def main():
    """메인 함수"""
    st.title("📊 날씨 웹앱 - 그래프 버전")
    st.markdown("OpenWeather API를 사용한 실시간 날씨 정보 (그래프 중심)")
    
    # 사이드바
    st.sidebar.header("🔍 도시 검색")
    
    # 인기 도시 목록
    popular_cities = [
        ("서울", "KR"), ("부산", "KR"), ("도쿄", "JP"), 
        ("뉴욕", "US"), ("런던", "GB"), ("파리", "FR")
    ]
    
    # 도시 선택 방법
    search_method = st.sidebar.radio(
        "검색 방법을 선택하세요:",
        ("인기 도시에서 선택", "직접 입력")
    )
    
    if search_method == "인기 도시에서 선택":
        city_options = [f"{city} ({code})" for city, code in popular_cities]
        selected_city = st.sidebar.selectbox("도시를 선택하세요:", city_options)
        
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
                # 현재 날씨 정보
                weather_data = get_weather_data(city_name, country_code)
                
                if weather_data:
                    # 도시 정보 표시
                    st.success(f"📍 {weather_data['name']}, {weather_data['sys']['country']}")
                    
                    # 현재 날씨 표시
                    st.subheader("🌡️ 현재 날씨")
                    display_current_weather(weather_data)
                    
                    st.divider()
                    
                    # 예보 그래프
                    forecast_data = get_forecast_data(city_name, country_code)
                    if forecast_data:
                        display_forecast_graphs(forecast_data)
        else:
            st.sidebar.warning("도시명을 입력해주세요!")
    
    # 초기 화면 정보
    else:
        st.info("👆 사이드바에서 도시를 선택하고 '날씨 조회' 버튼을 클릭해주세요!")
        
        # 그래프 기능 안내
        with st.expander("📊 그래프 기능 안내"):
            st.markdown("""
            ### 🌟 새로운 그래프 기능
            
            **1. 🌡️ Streamlit 라인 차트**
            - 요청하신 방식으로 구현된 온도 변화 그래프
            - 시간을 인덱스로, 온도를 값으로 하는 DataFrame 활용
            
            **2. 📊 Matplotlib 상세 그래프**
            - **온도 변화**: 2일간 온도 추이 (빨간색 선)
            - **습도 변화**: 2일간 습도 변화 (파란색 선)  
            - **풍속 변화**: 2일간 풍속 변화 (녹색 선)
            - **종합 그래프**: 온도와 습도를 함께 표시
            
            **3. 📋 상세 데이터 표**
            - 접을 수 있는 형태로 제공
            - 시간별 상세 정보 확인 가능
            
            ### 🔍 변경 사항
            - **기존**: 표 형태 데이터 (st.dataframe)
            - **변경**: 그래프 중심 시각화 (st.line_chart + matplotlib)
            - **추가**: 다양한 기상 요소 그래프
            """)

if __name__ == "__main__":
    main()