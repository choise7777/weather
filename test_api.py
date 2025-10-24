import requests
import json

# 제공된 코드 구조 그대로
city = "Seoul"
apikey = "14e3fc348b3e11a20c23806f1c3be844"  # API 키 입력
lang = "kr"

api = f"""http://api.openweathermap.org/data/2.5/\
weather?q={city}&appid={apikey}&lang={lang}&units=metric"""

result = requests.get(api)

data = json.loads(result.text)

print("=== 서울 날씨 정보 ===")
print(f"도시: {data['name']}")
print(f"온도: {data['main']['temp']}°C")
print(f"체감온도: {data['main']['feels_like']}°C")
print(f"날씨: {data['weather'][0]['description']}")
print(f"습도: {data['main']['humidity']}%")
print(f"풍속: {data['wind']['speed']} m/s")

print("\n=== 전체 데이터 ===")
print(data)