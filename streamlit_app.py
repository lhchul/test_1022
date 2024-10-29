import streamlit as st
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

# 운영체제별 폰트 경로 설정 함수
def find_nanum_font():
    system = platform.system()
    font_paths = {
        "Windows": r"C:\Windows\Fonts\NanumGothic.ttf",
        "Linux": "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "Darwin": "/Library/Fonts/NanumGothic.ttf"
    }
    font_path = font_paths.get(system)

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
            plt.rc('font', family=font_prop.get_name())
            plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
        except Exception as e:
            st.error(f"폰트 설정 실패: {e}")
            plt.rc('font', family='sans-serif')
    else:
        st.warning("NanumGothic 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        plt.rc('font', family='sans-serif')

# 폰트 설정 적용
set_font()

# Streamlit에서 CSV 파일 업로드
st.title("CSV 파일 업로드 및 데이터 시각화")
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 결측값 및 온도 0 제거
    data = data.dropna(subset=['온도'])
    data = data[data['온도'] > 0]

    # 데이터의 마지막 날짜를 기준으로 1주일 데이터 필터링
    last_date = data['날짜'].max()
    one_week_data = data[data['날짜'] >= last_date - timedelta(days=7)]

    # 1주일 평균 온도 계산
    daily_avg_temp_data = one_week_data.groupby(one_week_data['날짜'].dt.date)['온도'].mean().reset_index()
    daily_avg_temp_data.columns = ['날짜', '평균 온도']

    # 1주일 평균 온도 그래프 시각화
    st.write("### 최근 1주일 평균 온도")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_avg_temp_data['날짜'], daily_avg_temp_data['평균 온도'], marker='o', linestyle='-')
    ax.set_title('최근 1주일 평균 온도', fontsize=18)
    ax.set_ylabel('평균 온도 (°C)', fontsize=16)
    plt.xticks(rotation=45)  # 날짜 라벨 회전
    plt.grid(True)
    st.pyplot(fig)

    # 최근 24시간 데이터 필터링 및 시간대별 평균 계산
    recent_data = data[data['날짜'] >= last_date - timedelta(hours=24)]
    hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

    # 최근 24시간 시간대별 평균 온도 그래프
    st.write("### 최근 24시간 시간대별 평균 온도")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-')
    ax.set_title('최근 24시간 시간대별 평균 온도', fontsize=18)
    ax.set_xlabel('시간대 (시)', fontsize=16)
    ax.set_ylabel('평균 온도 (°C)', fontsize=16)
    plt.grid(True)
    st.pyplot(fig)
