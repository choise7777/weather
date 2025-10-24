# 파일 정리 스크립트
with open('weather_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# main 함수를 새로운 버전으로 교체
new_main = '''def main():
    """메인 함수"""
    # 제목
    st.title("🌤️ 실시간 날씨")
    
    # 현재 위치 기반 날씨만 표시
    display_location_weather()

if __name__ == "__main__":
    main()'''

# main 함수 부분을 찾아서 교체
import re
pattern = r'def main\(\):(.*?)if __name__ == "__main__":\s*main\(\)'
replacement = new_main

updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 사용하지 않는 함수들 제거
functions_to_remove = [
    r'def display_city_weather\(.*?\n(?:.*?\n)*?(?=def|\Z)',
    r'def get_weather_data\(.*?\n(?:.*?\n)*?(?=def|\Z)',
    r'def get_forecast_data\(.*?\n(?:.*?\n)*?(?=def|\Z)'
]

for pattern in functions_to_remove:
    updated_content = re.sub(pattern, '', updated_content, flags=re.DOTALL)

with open('weather_app_clean.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("파일 정리 완료!")