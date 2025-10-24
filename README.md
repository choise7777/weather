# 🌤️ 날씨 웹앱

OpenWeather API를 사용한 실시간 날씨 정보 제공 웹애플리케이션

## 📋 주요 기능

### 🔍 도시 검색 기능
- **실시간 날씨 정보**: 현재 온도, 습도, 풍속, 기압 등
- **5일 날씨 예보**: 향후 5일간의 상세 날씨 예보 (3시간 간격)
- **인기 도시 바로가기**: 서울, 도쿄, 런던, 뉴욕, 파리 원클릭 검색
- **전 세계 도시 지원**: 영어 도시명으로 전 세계 검색 가능

### 📍 현재 위치 기능 ✨
- **위치 기반 날씨**: GPS 좌표로 현재 위치 날씨 자동 조회
- **수동 좌표 입력**: 위도/경도 직접 입력으로 정확한 위치 검색
- **7일 주간 예보**: 일별 최고/최저 온도 및 날씨 상태
- **온도 변화 차트**: 주간 온도 변화를 시각적으로 표시
- **강수 확률**: 일별 비/눈 올 확률 정보

### 🎨 사용자 경험
- **탭 기반 UI**: 도시 검색과 현재 위치를 분리된 탭으로 제공
- **반응형 디자인**: 모바일/데스크톱 최적화
- **실시간 업데이트**: 최신 날씨 데이터 제공

## 🚀 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행
```bash
streamlit run weather_app.py
```

### 3. 웹 브라우저에서 확인
애플리케이션이 실행되면 자동으로 브라우저가 열리며, `http://localhost:8501`에서 웹앱을 사용할 수 있습니다.

## 🛠️ 기술 스택

- **Python 3.13+**
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Requests**: HTTP 요청 처리
- **Pandas**: 데이터 처리 및 표시
- **OpenWeather API**: 날씨 데이터 제공

## 📖 사용법

### 🔍 도시 검색 탭
1. **도시명 입력**: 상단 입력창에 영어 도시명 입력 (예: Seoul, Tokyo, London)
2. **🔍 검색 버튼**: 클릭하여 날씨 정보 조회
3. **인기 도시 버튼**: 원클릭으로 주요 도시 날씨 확인
4. **5일 예보**: 3시간 간격 상세 예보 데이터 확인

### 📍 현재 위치 탭 ⭐
1. **📍 내 위치 날씨**: 브라우저 위치 권한 허용 후 버튼 클릭
2. **수동 좌표 입력**: 
   - 위도/경도 직접 입력 (예: 서울 37.5665, 126.9780)
   - 🎯 좌표로 검색 버튼 클릭
3. **7일 주간 예보**: 일별 최고/최저 온도 및 강수확률
4. **📈 온도 차트**: 주간 온도 변화 그래프 확인

## 🌍 지원 도시

### 한국 주요 도시
- 서울, 부산, 대구, 인천, 광주, 대전, 울산

### 해외 주요 도시  
- 도쿄, 오사카, 뉴욕, 런던, 파리, 베이징, 상하이

## 🔑 API 키 설정

OpenWeather API 키가 코드에 포함되어 있습니다. 실제 배포 시에는 환경 변수로 관리하는 것을 권장합니다.

```python
# 환경 변수로 관리하는 방법
import os
API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_default_api_key')
```

## 📄 파일 구조

```
weather/
├── weather_app.py      # 메인 애플리케이션 파일
├── requirements.txt    # 필요한 패키지 목록
└── # 🌤️ 실시간 날씨 앱

Streamlit으로 제작된 실시간 날씨 정보 및 OOTD(Outfit of the Day) 추천 웹 애플리케이션입니다.

## 🚀 주요 기능

### 📍 날씨 정보
- **실시간 날씨**: 현재 온도, 습도, 풍속, 기압 등
- **위치 기반 날씨**: GPS 좌표를 통한 정확한 날씨 정보
- **상세 주소**: Nominatim API를 통한 정확한 위치 정보
- **동적 배경**: 날씨 상태에 따른 배경화면 변경

### 📊 예보 및 분석
- **주간 예보**: 7일 날씨 예보
- **시각화**: 온도, 습도, 풍속 변화 그래프
- **2일 상세**: 48시간 상세 예보

### 👕 OOTD 추천 시스템
- **시간대별 타임라인**: 6시간 단위 옷차림 추천
- **8단계 온도 분류**: 체감온도 기반 정교한 추천
- **날씨별 액세서리**: 우산, 선글라스, 목도리 등
- **변화 감지**: 온도 변화에 따른 의류 조언

## 🛠️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/weather-app.git
cd weather-app
```

### 2. 가상환경 생성 (선택사항)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
#### 방법 1: .env 파일 사용 (권장)
```bash
# .env.example을 .env로 복사
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# .env 파일 편집하여 실제 API 키 입력
OPENWEATHER_API_KEY=your_actual_api_key_here
```

#### 방법 2: config.py 파일 수정
`config.py` 파일의 `OPENWEATHER_API_KEY` 값을 실제 API 키로 변경

### 5. 앱 실행
```bash
streamlit run weather_app.py
```

## 🔑 API 키 발급

### OpenWeather API
1. [OpenWeatherMap](https://openweathermap.org/api) 회원가입
2. API Keys 섹션에서 무료 API 키 생성
3. 위의 설정 방법에 따라 키 설정

## 📁 프로젝트 구조

```
weather-app/
├── weather_app.py          # 메인 애플리케이션
├── config.py              # API 설정 (보안 파일)
├── requirements.txt       # 필요한 패키지 목록
├── .env.example          # 환경변수 예시 파일
├── .env                  # 환경변수 파일 (생성 필요)
├── .gitignore           # Git 제외 파일 목록
└── README.md            # 프로젝트 설명서
```

## 🌍 지원 지역

- **한국**: 서울, 김포, 부산, 제주 등
- **해외**: 도쿄, 뉴욕, 런던, 파리 등 전 세계 주요 도시
- **좌표 기반**: 정확한 위도/경도를 통한 모든 지역

## 🔒 보안

- API 키는 `config.py` 또는 `.env` 파일에서 관리
- 보안 파일들은 `.gitignore`에 의해 Git에서 제외됨
- 환경변수를 통한 안전한 키 관리 지원

## 🎨 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **APIs**: 
  - OpenWeather API (날씨 정보)
  - Nominatim API (지오코딩)
- **Data**: Pandas (데이터 처리)
- **HTTP**: Requests (API 통신)

## 📱 사용법

1. **도시 검색 탭**: 도시명 입력 또는 인기 도시 버튼 클릭
2. **내 위치 탭**: 위도/경도 입력 또는 빠른 좌표 버튼 클릭
3. **OOTD 타임라인**: 시간대별 옷차림 추천 확인
4. **상세 정보**: 예보 그래프 및 상세 데이터 열람

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 연락처

프로젝트 링크: [https://github.com/yourusername/weather-app](https://github.com/yourusername/weather-app)

---

**⚠️ 주의사항**
- API 키는 절대 GitHub에 업로드하지 마세요
- `.env` 파일은 로컬에서만 사용하고 공유하지 마세요
- 무료 API 키의 경우 일일 호출 제한이 있을 수 있습니다          # 프로젝트 설명서
```

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.
날씨 웹 앱
