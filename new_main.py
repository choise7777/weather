def main():
    """메인 함수"""
    # 제목
    st.title("🌤️ 실시간 날씨")
    
    # 현재 위치 기반 날씨만 표시
    display_location_weather()

if __name__ == "__main__":
    main()