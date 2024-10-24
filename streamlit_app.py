import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import platform, os

# 폰트 설정 함수
def set_font():
    system = platform.system()
    font_path = {
        "Windows": r"C:\Users\SKTelecom\AppData\Local\Microsoft\Windows\Fonts\NanumGothic_0.ttf",
        "Linux": "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "Darwin": "/Library/Fonts/NanumGothic.ttf"
    }.get(system)
    if font_path and os.path.exists(font_path):
        plt.rcParams['font.family'] = plt.matplotlib.font_manager.FontProperties(fname=font_path).get_name()
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

set_font()  # 폰트 설정

# CSV 업로드 및 데이터 처리
st.title("🌡️ 온도 모니터링 대시보드")
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요:", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file, parse_dates=['날짜']).dropna(subset=['온도']).query('온도 > 0')
    selected = st.selectbox("📍 통합국명 선택:", ["전체"] + sorted(data['통합국명'].unique()))
    filtered = data if selected == "전체" else data[data['통합국명'] == selected]
    
    st.download_button("CSV 다운로드", filtered.to_csv(index=False).encode('utf-8-sig'), f"{selected}_데이터.csv")

    latest = filtered.sort_values('날짜', ascending=False).groupby('모듈번호').first().reset_index()
    max_temp_row, min_temp_row = filtered.loc[filtered['온도'].idxmax()], filtered.loc[filtered['온도'].idxmin()]

    st.dataframe(latest[['모듈번호', '온도']])
    st.write(f"🔥 최고 온도 모듈: {max_temp_row['모듈번호']} ({max_temp_row['온도']}°C)")
    st.write(f"🔻 일주일 최저 온도: {min_temp_row['온도']}°C")

    # 그래프 그리기 함수
    def plot_graph(title, xlabel, ylabel, data):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data.index, data.values, marker='o', linestyle='-', linewidth=2)
        ax.set_title(title, fontsize=18)
        ax.set_xlabel(xlabel, fontsize=16)
        ax.set_ylabel(ylabel, fontsize=16)
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)

    # 그래프 선택 및 표시
    graph_type = st.selectbox("📊 그래프 선택:", ["최근 24시간", "2주 평균", "일별 최대"])
    now = datetime.now()

    if graph_type == "최근 24시간":
        hourly_avg = filtered[filtered['날짜'] >= now - timedelta(hours=24)].groupby(filtered['날짜'].dt.hour)['온도'].mean()
        plot_graph("최근 24시간 평균 온도", "시간대", "평균 온도 (°C)", hourly_avg)

    elif graph_type == "2주 평균":
        two_weeks_avg = filtered[filtered['날짜'] >= now - timedelta(days=14)].groupby(filtered['날짜'].dt.strftime('%m-%d'))['온도'].mean()
        plot_graph("2주 평균 온도", "날짜 (월-일)", "평균 온도 (°C)", two_weeks_avg)

    elif graph_type == "일별 최대":
        daily_max = filtered.groupby(filtered['날짜'].dt.date)['온도'].max()
        plot_graph("일별 최대 온도", "날짜", "최대 온도 (°C)", daily_max)
