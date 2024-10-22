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

# 선택한 데이터를 CSV로 저장하고 다운로드 링크 제공
def download_csv(data, filename):
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# 그래프를 이미지로 저장하고 경로 반환
def save_plot(fig, filename):
    if not os.path.exists("images"):
        os.makedirs("images")
    filepath = os.path.join("images", filename)
    fig.savefig(filepath, bbox_inches='tight')
    return filepath

# Streamlit 앱 타이틀
st.title("온도 모니터링 대시보드")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요:", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기 및 날짜 변환
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 결측값을 제외하고 데이터 필터링
    data = data.dropna(subset=['온도'])

    # 통합국명 목록 정렬 및 선택
    unique_locations = sorted(data['통합국명'].unique())
    selected_location = st.selectbox("통합국명을 선택하세요:", unique_locations)

    # 선택된 통합국명 데이터 필터링
    filtered_data = data[data['통합국명'] == selected_location]

    # 선택된 통합국명 데이터 다운로드 버튼
    download_csv(filtered_data, f"{selected_location}_온도데이터.csv")

    # 그래프 종류 선택
    graph_type = st.selectbox(
        "보고 싶은 그래프를 선택하세요:",
        ["최근 24시간 평균 온도", "2주 평균 온도", "하루 중 최대 온도"]
    )

    # 그래프 그리기
    if graph_type == "최근 24시간 평균 온도":
        last_24_hours = datetime.now() - timedelta(hours=24)
        recent_data = filtered_data[filtered_data['날짜'] >= last_24_hours]
        hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-', linewidth=2)
        ax.set_title('최근 24시간 시간대별 평균 온도', fontsize=15)
        ax.set_xlabel('시간대 (시)', fontsize=12)
        ax.set_ylabel('평균 온도 (°C)', fontsize=12)
        plt.grid(True)
        st.pyplot(fig)

    elif graph_type == "2주 평균 온도":
        two_weeks_ago = datetime.now() - timedelta(days=14)
        two_weeks_data = filtered_data[filtered_data['날짜'] >= two_weeks_ago]
        two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
        ax.set_title('2주 평균 온도', fontsize=15)
        ax.set_xlabel('날짜 (월-일)', fontsize=12)
        ax.set_ylabel('평균 온도 (°C)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)

    elif graph_type == "하루 중 최대 온도":
        daily_max = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(daily_max.index, daily_max.values, marker='o', linestyle='-', linewidth=2)
        ax.set_title('하루 중 최대 온도', fontsize=15)
        ax.set_xlabel('날짜 (월-일)', fontsize=12)
        ax.set_ylabel('최대 온도 (°C)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)
