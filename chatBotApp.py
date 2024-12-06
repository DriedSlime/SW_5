import streamlit as st
from streamlit_option_menu import option_menu
from urllib.parse import quote
import requests
from datetime import datetime, timedelta

# Kakao 지도 API를 사용하여 HTML iframe 생성
KAKAO_API_KEY = "your_kakao_api_key"

# OpenWeather API Key
OPENWEATHER_API_KEY = "your_openweather_api_key"


# HTML을 렌더링하기 위한 기본 템플릿
def generate_map_iframe_html(query, width, height):
    encoded_query = quote(query)
    return f"""
    <iframe
        width="{width}"
        height="{height}"
        src="https://map.kakao.com/link/search/{encoded_query}"
        frameborder="0"
        allowfullscreen>
    </iframe>
    """

# 날씨 예보를 가져오는 함수
def get_weather_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        forecast_data = []

        current_time = datetime.now()

        # 시간 구하기
        for delta in [0, 12]:  # 0은 현재시간, 3은 +3시간, 6은 +6시간
            forecast_time = current_time + timedelta(hours=delta)
            forecast_data.append({
                "time": forecast_time.strftime("%H시 %M분"),  
                "temp": data['list'][delta]['main']['temp'],
                "description": data['list'][delta]['weather'][0]['description'],
                "weekday": forecast_time.strftime("%A"),  
                "temp_min": data['list'][delta]['main']['temp_min'],  
                "temp_max": data['list'][delta]['main']['temp_max'],  
            })

        # 각 요일별로 최저 및 최고 기온을 구하기
        daily_min_max = {}
        for forecast in data['list']:
            date = datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d')
            temp_min = forecast['main']['temp_min']
            temp_max = forecast['main']['temp_max']
            if date not in daily_min_max:
                daily_min_max[date] = {'temp_min': temp_min, 'temp_max': temp_max}
            else:
                daily_min_max[date]['temp_min'] = min(daily_min_max[date]['temp_min'], temp_min)
                daily_min_max[date]['temp_max'] = max(daily_min_max[date]['temp_max'], temp_max)

        return forecast_data, daily_min_max
    else:
        return None, None
# Streamlit 앱 구현
def main():
    # 화면 너비 설정
    st.set_page_config(layout="wide")
    st.markdown(
    """
    <style>
        /* Sidebar width adjustment */
        [data-testid="stSidebar"] {
            min-width: 200px;
            max-width: 300px;  /* Adjust the maximum width */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

    # 앱 제목 및 설명
    st.title("🗺️ 여행 가이드 챗봇")
    st.write("검색하고자 하는 장소를 입력하세요. 현재는 **춘천 지역**만 지원합니다.")

    # 기본 지도 HTML
    map_html = None

    # 레이아웃 설정: 지도, 날씨 예보, 추천 일정
    col1, col2 = st.columns([5, 3])

    # 사이드바
    with st.sidebar:
        st.header("🔍 빠른 탐색")
        menu = option_menu(
            menu_title="Menu",  # Title for the menu
            options=["춘천 식당", "춘천 숙소", "춘천 관광지"],  # Menu options
            icons=["apple", "building", "backpack"],  # Icons for the options
            default_index=0,  # Default selected option
            styles={  # Custom styles for the menu
                "container": {"padding": "5!important", "background-color": "#121212"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#AAAAFF",
                },
                "nav-link-selected": {
                    "background-color": "#A9A9A9",
                    },
            },
        )

        # Date input for selecting forecast date
        my_date = st.date_input("원하는 날짜를 선택하세요", datetime.now())

    # Map query based on user choice
    query = menu
    map_html = generate_map_iframe_html(query, "100%", "600px")

    # Layout: Columns for map and weather
    col1, col2 = st.columns([4, 3])

    # 추천 일정 출력 (col2)
    with col2:
        user_input = st.text_input("검색할 장소를 입력하세요:", placeholder="예: 춘천 카페")
        #if user_input:
            # if "춘천" in user_input:
            #     query = user_input
            #     map_html = generate_map_iframe_html(query, "100%", "600px")
            # else:
            #     st.warning("현재는 춘천 지역만 지원합니다. 검색어에 '춘천'을 포함해주세요.")
        st.write("chatBot이 일정을 출력해줄겁니다")
    # 지도 및 날씨 정보 출력 (col1)
    with col1:
        if map_html:
            st.components.v1.html(map_html, height=550, width=900)
        else:
            st.info("지도가 여기에 표시됩니다.")

        # 날씨 정보 출력
        forecast_data, daily_min_max = get_weather_forecast("Chuncheon")
        if forecast_data:
            st.subheader("☀️ 춘천 날씨 예보")
            for i, forecast in enumerate(forecast_data):
                # 두 컬럼으로 나누기
                left_col, right_col = st.columns([1, 1])  # 두 컬럼으로 나눔
                with left_col: # 현재 시간을 기준으로 시간, 온도, 날씨 출력(left_col)
                    st.write(f"🕓시간: {forecast['time']}")
                    st.write(f"🌡️온도: {forecast['temp']}°C")
                    st.write(f"☁️날씨: {forecast['description']}")
                with right_col: # 요일과 그 날 최저, 최고 기온 출력(right_col)
                    weekday_display = (my_date + timedelta(days=i)).strftime("%A")
                    st.write(f"📅요일: {weekday_display}")
                    date_key = (my_date + timedelta(days=i)).strftime('%Y-%m-%d')
                    if date_key in daily_min_max:
                        st.write(f"🌡️최저 기온: {daily_min_max[date_key]['temp_min']}°C")
                        st.write(f"🌡️최고 기온: {daily_min_max[date_key]['temp_max']}°C")
                st.write("------")
        else:
            st.error("날씨 정보를 가져올 수 없습니다.")

# 메인 실행
if __name__ == "__main__":
    main()
