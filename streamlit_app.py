import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

# 운영체제에 맞게 폰트 경로를 찾는 함수
def find_nanum_font():
    system = platform.system()

    if system == "Windows":
        font_path = r"C:\Users\SKTelecom\AppData\Local\Microsoft\Windows\Fonts\NanumGothic_0.ttf"
    elif system == "Linux":
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    elif system == "Darwin":
        font_path = "/Library/Fonts/NanumGothic.ttf"
    else:
        font_path = None

    if font_path and os.path.exists(font_path):
        return font_path
    else:
        st.error(f"폰트 파일을 찾을 수 없습니다: {font_path}")
        return None

# 폰트 설정 함수
def set_font():
    font_path = find_nanum_font()
    if font_path:
        try:
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            plt.rcParams['axes.unicode_minus'] = False
            st.success(f"폰트 설정 성공: {font_prop.get_name()}")
        except Exception as e:
            st.error(f"폰트 설정 실패: {e}")
            plt.rcParams['font.family'] = 'sans-serif'
    else:
        st.warning("NanumGothic 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'sans-serif'

# 폰트 설정 적용
set_font()

# CSS 스타일 적용 (글자 크기와 버튼 색상 설정)
def set_css():
    st.markdown(
        """
        <style>
        .stDownloadButton > button {
            color: blue !important;
        }
        .large-font {
            font-size: 24px !important;
        }
        .medium-font {
            font-size: 20px !important;
        }
        .small-font {
            font-size: 18px !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

# 일주일 최고 온도 스타일링 함수 (31도 이상 빨간색)
def highlight_max_temp(val):
    color = 'red' if val >= 31 else 'black'
    return f'color: {color}'

# 그래프를 그리는 함수들 정의
def plot_hourly_avg(data):
    last_24_hours = datetime.now() - timedelta(hours=24)
    recent_data = data[data['날짜'] >= last_24_hours]
    hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-', linewidth=2)
    ax.set_title('최근 24시간 시간대별 평균 온도', fontsize=20)
    ax.set_xlabel('시간대 (시)', fontsize=18)
    ax.set_ylabel('평균 온도 (°C)', fontsize=18)
    plt.grid(True)
    st.pyplot(fig)

def plot_two_weeks_avg(data):
    two_weeks_ago = datetime.now() - timedelta(days=14)
    two_weeks_data = data[data['날짜'] >= two_weeks_ago]
    two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
    ax.set_title('2주 평균 온도', fontsize=20)
    ax.set_xlabel('날짜 (월-일)', fontsize=18)
    ax.set_ylabel('평균 온도 (°C)', fontsize=18)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

def plot_daily_max(data):
    daily_max = data.groupby(data['날짜'].dt.date)['온도'].max()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_max.index, daily_max.values, marker='o', linestyle='-', linewidth=2)
    ax.set_title('하루 중 최대 온도', fontsize=20)
    ax.set_xlabel('날짜 (월-일)', fontsize=18)
    ax.set_ylabel('최대 온도 (°C)', fontsize=18)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

# 선택한 데이터를 CSV로 저장하고 다운로드 링크 제공
def download_csv(data, filename):
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# Streamlit 앱 타이틀
st.markdown('<h1 class="large-font">🌡️ 통합국 온도 모니터링 대시보드</h1>', unsafe_allow_html=True)

# CSS 설정 적용
set_css()

# CSV 파일 업로드
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요:", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기 및 날짜 변환
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 결측값을 제외하고 데이터 필터링
    data = data.dropna(subset=['온도'])

    # 통합국명 목록 정렬 및 선택
    unique_locations = sorted(data['통합국명'].unique())
    selected_location = st.selectbox("📍 통합국명을 선택하세요:", ["전체"] + unique_locations)

    # 선택된 통합국명 데이터 필터링
    if selected_location == "전체":
        filtered_data = data
    else:
        filtered_data = data[data['통합국명'] == selected_location]

    # 선택된 통합국명 데이터 다운로드 버튼
    download_csv(filtered_data, f"{selected_location}_온도데이터.csv")

    # 최신 온도 데이터 추출
    latest_data = filtered_data.sort_values(by='날짜', ascending=False).groupby('모듈번호').first().reset_index()

    # 일주일 최고/최저 온도 계산
    one_week_ago = datetime.now() - timedelta(days=7)
    week_data = filtered_data[filtered_data['날짜'] >= one_week_ago]
    max_temp = week_data['온도'].max()
    min_temp = week_data['온도'].min()

    # 일평균 온도 계산
    today_data = filtered_data[filtered_data['날짜'].dt.date == datetime.now().date()]
    daily_avg_temp = today_data['온도'].mean()

    # 최고 온도 모듈 찾기
    max_module = latest_data.loc[latest_data['온도'].idxmax()]

    # 통계 정보 출력
    st.markdown('<p class="medium-font">📈 <b>각 모듈번호의 현재 온도:</b></p>', unsafe_allow_html=True)
    st.dataframe(latest_data[['모듈번호', '온도']])

    st.markdown(f'<p class="medium-font">🔥 <b>가장 높은 온도를 가진 모듈번호:</b> {max_module["모듈번호"]} (온도: {max_module["온도"]}°C)</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="medium-font">🌡️ <b>일평균 온도:</b> {daily_avg_temp:.2f}°C</p>', unsafe_allow_html=True)
    
    # 일주일 최고/최저 온도 표시 (31도 이상 빨간색)
    st.markdown('<p class="medium-font">🔺 <b>일주일 최고/최저 온도:</b></p>', unsafe_allow_html=True)
    styled_week_data = pd.DataFrame({
        '최고 온도': [max_temp],
        '최저 온도': [min_temp]
    }).style.applymap(highlight_max_temp, subset=['최고 온도'])
    st.dataframe(styled_week_data)

    # 그래프 종류 선택
    graph_type = st.selectbox(
        "📊 보고 싶은 그래프를 선택하세요:",
        ["전체 보기", "최근 24시간 평균 온도", "2주 평균 온도", "하루 중 최대 온도"]
    )

    # 그래프 그리기
    if graph_type == "전체 보기":
        st.write("📊 **전체 그래프 보기**")
        plot_hourly_avg(filtered_data)
        plot_two_weeks_avg(filtered_data)
        plot_daily_max(filtered_data)
    elif graph_type == "최근 24시간 평균 온도":
        plot_hourly_avg(filtered_data)
    elif graph_type == "2주 평균 온도":
        plot_two_weeks_avg(filtered_data)
    elif graph_type == "하루 중 최대 온도":
        plot_daily_max(filtered_data)
