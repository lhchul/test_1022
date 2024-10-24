import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

# 폰트 설정 함수
def set_font():
    system = platform.system()
    font_paths = {
        "Windows": r"C:\Windows\Fonts\NanumGothic.ttf",
        "Linux": "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "Darwin": "/Library/Fonts/NanumGothic.ttf"
    }
    font_path = font_paths.get(system)
    if font_path and os.path.exists(font_path):
        fm._rebuild()
        plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())
    else:
        plt.rc('font', family='sans-serif')
    plt.rc('axes', unicode_minus=False)

# 폰트 설정 적용
set_font()

# CSS 적용
st.markdown("""
    <style>
    .stDownloadButton > button { color: blue !important; }
    .large-font { font-size: 24px !important; }
    .medium-font { font-size: 20px !important; }
    .bold-larger { font-size: 22px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="large-font">🌡️ 통합국 온도 모니터링 대시보드</h1>', unsafe_allow_html=True)

# CSV 파일 업로드
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요:", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file).dropna(subset=['온도'])
    data = data[data['온도'] > 0]
    data['날짜'] = pd.to_datetime(data['날짜'])

    locations = ["전체"] + sorted(data['통합국명'].unique())
    selected_location = st.selectbox("📍 통합국명을 선택하세요:", locations)

    filtered_data = data if selected_location == "전체" else data[data['통합국명'] == selected_location]

    st.download_button(
        "CSV 다운로드", 
        filtered_data.to_csv(index=False).encode('utf-8-sig'), 
        f"{selected_location}_온도데이터.csv", 
        "text/csv"
    )

    latest_data = filtered_data.groupby('모듈번호').last().reset_index()

    week_data = filtered_data[filtered_data['날짜'] >= datetime.now() - timedelta(days=7)]
    daily_avg = week_data.groupby(week_data['날짜'].dt.date)['온도'].mean().reset_index()

    st.markdown('<p class="medium-font">📈 현재 온도:</p>', unsafe_allow_html=True)
    st.dataframe(latest_data[['모듈번호', '온도']])

    max_module = latest_data.loc[latest_data['온도'].idxmax()]
    st.markdown(f"<b>최고 온도 모듈:</b> {max_module['모듈번호']} ({max_module['온도']}°C)")

    st.markdown("🌡️ <b>최근 1주일 평균 온도:</b>", unsafe_allow_html=True)
    st.dataframe(daily_avg)

    graph_type = st.selectbox("📊 그래프 선택:", ["최근 24시간", "2주 평균", "일단위 최대"])

    def plot_graph():
        if graph_type == "최근 24시간":
            hourly_avg = filtered_data[filtered_data['날짜'] >= datetime.now() - timedelta(hours=24)] \
                         .groupby(filtered_data['날짜'].dt.hour)['온도'].mean()
            title, xlabel = "최근 24시간 평균 온도", "시간 (시)"
        elif graph_type == "2주 평균":
            two_weeks_avg = filtered_data[filtered_data['날짜'] >= datetime.now() - timedelta(days=14)] \
                            .groupby(filtered_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()
            title, xlabel = "2주 평균 온도", "날짜 (월-일)"
        else:
            daily_max = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()
            title, xlabel = "일단위 최대 온도", "날짜 (월-일)"

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(hourly_avg.index if graph_type == "최근 24시간" else two_weeks_avg.index if graph_type == "2주 평균" else daily_max.index,
                hourly_avg.values if graph_type == "최근 24시간" else two_weeks_avg.values if graph_type == "2주 평균" else daily_max.values,
                marker='o', linestyle='-', linewidth=2)
        ax.set_title(title, fontsize=18)
        ax.set_xlabel(xlabel, fontsize=16)
        ax.set_ylabel('온도 (°C)', fontsize=16)
        plt.xticks(rotation=45 if graph_type != "최근 24시간" else 0)
        plt.grid(True)
        st.pyplot(fig)

    plot_graph()
