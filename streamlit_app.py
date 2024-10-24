import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os, platform

# 운영체제별 폰트 설정
def set_font():
    system = platform.system()
    font_path = (
        r"C:\Users\SKTelecom\AppData\Local\Microsoft\Windows\Fonts\NanumGothic_0.ttf"
        if system == "Windows" else
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
        if system == "Linux" else
        "/Library/Fonts/NanumGothic.ttf"
        if system == "Darwin" else None
    )
    if font_path and os.path.exists(font_path):
        fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

set_font()

# 앱 타이틀 및 파일 업로드
st.title("🌡️ 통합국 온도 모니터링 대시보드")
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요:", type="csv")

if uploaded_file:
    # 데이터 로딩 및 전처리
    data = pd.read_csv(uploaded_file, parse_dates=['날짜'])
    data = data.dropna(subset=['온도']).query('온도 > 0')

    # 통합국명 선택
    locations = sorted(data['통합국명'].unique())
    selected = st.selectbox("📍 통합국명 선택:", ["전체"] + locations)
    filtered = data if selected == "전체" else data[data['통합국명'] == selected]

    # 최신 데이터 및 통계 정보
    latest = filtered.sort_values('날짜', ascending=False).groupby('모듈번호').first().reset_index()
    max_temp_row = filtered.loc[filtered['온도'].idxmax()]
    min_temp_row = filtered.loc[filtered['온도'].idxmin()]

    # 통계 출력
    st.dataframe(latest[['모듈번호', '온도']])
    st.write(f"🔥 **가장 높은 온도:** {max_temp_row['온도']}°C (모듈번호: {max_temp_row['모듈번호']})")
    st.write(f"🔻 **일주일 최저 온도:** {min_temp_row['온도']}°C")

    # 그래프 선택 및 그리기
    graph_type = st.selectbox("📊 그래프 선택:", ["최근 24시간 평균", "2주 평균 온도", "일별 최대 온도"])

    def plot_graph(data, title, xlabel, ylabel):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data.index, data.values, marker='o', linestyle='-', linewidth=2)
        ax.set_title(title, fontsize=18)
        ax.set_xlabel(xlabel, fontsize=16)
        ax.set_ylabel(ylabel, fontsize=16)
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)

    # 그래프 데이터 생성
    now = datetime.now()
    if graph_type == "최근 24시간 평균":
        hourly = filtered[filtered['날짜'] >= now - timedelta(hours=24)]
        avg_hourly = hourly.groupby(hourly['날짜'].dt.hour)['온도'].mean()
        plot_graph(avg_hourly, "최근 24시간 시간대별 평균 온도", "시간대 (시)", "평균 온도 (°C)")

    elif graph_type == "2주 평균 온도":
        two_weeks = filtered[filtered['날짜'] >= now - timedelta(days=14)]
        avg_daily = two_weeks.groupby(two_weeks['날짜'].dt.strftime('%m-%d'))['온도'].mean()
        plot_graph(avg_daily, "2주 평균 온도", "날짜 (월-일)", "평균 온도 (°C)")

    elif graph_type == "일별 최대 온도":
        daily_max = filtered.groupby(filtered['날짜'].dt.date)['온도'].max()
        plot_graph(daily_max, "일별 최대 온도", "날짜", "최대 온도 (°C)")
