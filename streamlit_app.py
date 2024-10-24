import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

# 운영체제별 폰트 경로 설정
def find_nanum_font():
    system = platform.system()
    if system == "Windows":
        return r"C:\Users\SKTelecom\AppData\Local\Microsoft\Windows\Fonts\NanumGothic_0.ttf"
    elif system == "Linux":
        return "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    elif system == "Darwin":
        return "/Library/Fonts/NanumGothic.ttf"
    return None

# 폰트 설정 함수
def set_font():
    font_path = find_nanum_font()
    if font_path and os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        st.warning("NanumGothic 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 폰트 설정 적용
set_font()

# CSS 스타일 설정 (NanumGothic 폰트 적용)
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'NanumGothic';
        src: url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');
    }
    html, body, [class*="css"] {
        font-family: 'NanumGothic', sans-serif;
    }
    .stDownloadButton > button {
        color: blue !important;
    }
    .large-font {
        font-size: 24px !important;
    }
    .medium-font {
        font-size: 20px !important;
    }
    .bold-larger {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    .bold-large {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 일주일 최고 온도 색상 강조 함수
def highlight_max_temp(val):
    color = 'red' if val >= 31 else 'black'
    return f'color: {color}'

# 앱 타이틀
st.markdown('<h1 class="large-font">🌡️ 통합국 온도 모니터링 대시보드</h1>', unsafe_allow_html=True)

# CSV 파일 업로드
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요:", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기 및 날짜 변환
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 결측값과 온도가 0인 행 제외
    data = data.dropna(subset=['온도'])
    data = data[data['온도'] > 0]

    # 통합국명 목록 정렬 및 선택
    unique_locations = sorted(data['통합국명'].unique())
    st.markdown('<p class="bold-larger">📍 통합국명을 선택하세요:</p>', unsafe_allow_html=True)
    selected_location = st.selectbox("", ["전체"] + unique_locations)

    # 선택된 통합국명 데이터 필터링
    if selected_location == "전체":
        filtered_data = data
    else:
        filtered_data = data[data['통합국명'] == selected_location]

    # 데이터 다운로드 버튼
    st.download_button(
        label="CSV 다운로드",
        data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{selected_location}_온도데이터.csv",
        mime='text/csv'
    )

    # 최신 온도 데이터 추출
    latest_data = filtered_data.sort_values(by='날짜', ascending=False).groupby('모듈번호').first().reset_index()

    # 최근 1주일 평균 온도 계산
    one_week_ago = datetime.now() - timedelta(days=7)
    week_data = filtered_data[filtered_data['날짜'] >= one_week_ago]
    daily_avg_temp_data = week_data.groupby(week_data['날짜'].dt.date)['온도'].mean().reset_index()
    daily_avg_temp_data.columns = ['날짜', '평균 온도']

    # 일주일 최고/최저 온도 계산
    max_temp_row = week_data.loc[week_data['온도'].idxmax()]
    min_temp_row = week_data.loc[week_data['온도'].idxmin()]

    # 최고 온도 모듈 찾기
    max_module = latest_data.loc[latest_data['온도'].idxmax()]

    # 통계 정보 출력
    st.markdown('<p class="medium-font">📈 <b>각 모듈번호의 현재 온도:</b></p>', unsafe_allow_html=True)
    st.dataframe(latest_data[['모듈번호', '온도']])

    st.markdown(f'<p class="medium-font">🔥 <b>가장 높은 온도를 가진 모듈번호:</b> {max_module["모듈번호"]} (온도: {max_module["온도"]}°C)</p>', unsafe_allow_html=True)

    # 최근 1주일 평균 온도 출력
    st.markdown('<p class="medium-font">🌡️ <b>최근 1주일 평균 온도:</b></p>', unsafe_allow_html=True)
    st.dataframe(daily_avg_temp_data)

    # 일주일 최고/최저 온도 표시
    st.markdown('<p class="medium-font">🔺 <b>일주일 최고/최저 온도:</b></p>', unsafe_allow_html=True)
    styled_week_data = pd.DataFrame({
        '날짜': [max_temp_row['날짜'].date(), min_temp_row['날짜'].date()],
        '온도': [max_temp_row['온도'], min_temp_row['온도']],
        '유형': ['최고 온도', '최저 온도']
    }).style.applymap(highlight_max_temp, subset=['온도'])
    st.dataframe(styled_week_data)

    # 그래프 선택
    st.markdown('<p class="bold-large">📊 보고 싶은 그래프를 선택하세요:</p>', unsafe_allow_html=True)
    graph_type = st.selectbox(
        "",
        ["전체 보기", "최근 24시간 평균 온도", "2주 평균 온도", "일단위 최대 온도"]
    )

    # 그래프 그리기 함수
    def plot_graph(graph_type):
        if graph_type in ["전체 보기", "최근 24시간 평균 온도"]:
            last_24_hours = datetime.now() - timedelta(hours=24)
            recent_data = filtered_data[filtered_data['날짜'] >= last_24_hours]
            hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-', linewidth=2)
            ax.set_title('최근 24시간 시간대별 평균 온도', fontsize=18)
            ax.set_xlabel('시간대 (시)', fontsize=16)
            ax.set_ylabel('평균 온도 (°C)', fontsize=16)
            plt.grid(True)
            st.pyplot(fig)

        if graph_type in ["전체 보기", "2주 평균 온도"]:
            two_weeks_ago = datetime.now() - timedelta(days=14)
            two_weeks_data = filtered_data[filtered_data['날짜'] >= two_weeks_ago]
            two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
            ax.set_title('2주 평균 온도', fontsize=18)
            ax.set_xlabel('날짜 (월-일)', fontsize=16)
            ax.set_ylabel('평균 온도 (°C)', fontsize=16)
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(fig)

        if graph_type in ["전체 보기", "일단위 최대 온도"]:
            daily_max = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(daily_max.index, daily_max.values, marker='o', linestyle='-', linewidth=2)
            ax.set_title('일단위 최대 온도', fontsize=18)
            ax.set_xlabel('날짜 (월-일)', fontsize=16)
            ax.set_ylabel('최대 온도 (°C)', fontsize=16)
            plt.xticks