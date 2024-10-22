import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 폴더 생성 함수 (이미지 저장용)
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 시스템 폰트 중 'NanumGothic' 폰트 자동 탐색
def find_available_font():
    font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_list:
        if "NanumGothic" in font:
            return font
    st.warning("⚠️ 'NanumGothic' 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    return None

# 폰트 설정
font_path = find_available_font()
if font_path:
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())

# 그래프를 이미지로 저장하고 경로 반환
def save_plot(fig, filename):
    ensure_dir("images")
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

    # 통합국명 목록 정렬
    unique_locations = sorted(data['통합국명'].unique())

    # 전체 선택 기능
    all_selected = st.checkbox("전체 선택")

    # 선택 데이터 필터링
    if all_selected:
        selected_location = "전체"
    else:
        selected_location = st.selectbox("통합국명을 선택하세요:", unique_locations)

    filtered_data = data if selected_location == "전체" else data[data['통합국명'] == selected_location]

    # 선택된 통합국명 출력
    st.write(f"**선택된 통합국명**: {selected_location}")

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

    # 최근 24시간 시간대별 평균 온도
    last_24_hours = datetime.now() - timedelta(hours=24)
    recent_data = filtered_data[filtered_data['날짜'] >= last_24_hours]
    hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

    # 2주 평균 온도
    two_weeks_ago = datetime.now() - timedelta(days=14)
    two_weeks_data = filtered_data[filtered_data['날짜'] >= two_weeks_ago]
    two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()

    # 하루 중 최대 온도
    daily_max = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()

    # 결과 출력
    st.write(f"📈 각 모듈번호의 현재 온도:")
    st.dataframe(latest_data[['모듈번호', '온도']])

    st.write(f"🔥 가장 높은 온도를 가진 모듈번호: **{max_module['모듈번호']}** 온도: **{max_module['온도']}°C**")
    st.write(f"🌡️ 일평균 온도: {daily_avg_temp:.2f}°C")
    st.write(f"🔺 일주일 최고 온도: {max_temp}°C")
    st.write(f"🔻 일주일 최저 온도: {min_temp}°C")

    # 그래프 1: 최근 24시간 평균 온도
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-', linewidth=2)
    ax1.set_title('최근 24시간 시간대별 평균 온도', fontsize=15)
    ax1.set_xlabel('시간대 (시)', fontsize=12)
    ax1.set_ylabel('평균 온도 (°C)', fontsize=12)
    plt.grid(True)
    img1_path = save_plot(fig1, "hourly_avg.png")
    st.image(img1_path)

    # 그래프 2: 2주 평균 온도
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
    ax2.set_title('2주 평균 온도', fontsize=15)
    ax2.set_xlabel('날짜 (월-일)', fontsize=12)
    ax2.set_ylabel('평균 온도 (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    img2_path = save_plot(fig2, "two_weeks_avg.png")
    st.image(img2_path)

    # 그래프 3: 하루 중 최대 온도
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(daily_max.index, daily_max.values, marker='o', linestyle='-', linewidth=2)
    ax3.set_title('하루 중 최대 온도', fontsize=15)
    ax3.set_xlabel('날짜 (월-일)', fontsize=12)
    ax3.set_ylabel('최대 온도 (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    img3_path = save_plot(fig3, "daily_max.png")
    st.image(img3_path)
