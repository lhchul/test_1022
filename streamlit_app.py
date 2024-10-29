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

# CSS 스타일 설정 함수
def set_css():
    st.markdown("""
        <style>
        .stDownloadButton > button { color: blue !important; }
        .large-font { font-size: 24px !important; }
        .medium-font { font-size: 20px !important; }
        .bold-larger { font-size: 22px !important; font-weight: bold !important; }
        </style>
    """, unsafe_allow_html=True)

# CSS 적용
set_css()

# 타이틀 설정
st.markdown('<h1 class="large-font">🌡️ 통합국 온도 모니터링 대시보드</h1>', unsafe_allow_html=True)

# CSV 파일 업로드
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요:", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 결측값 및 온도 0 제거
    data = data.dropna(subset=['온도'])
    data = data[data['온도'] > 0]

    # 통합국명 선택 및 데이터 필터링
    unique_locations = sorted(data['통합국명'].unique())
    st.markdown('<p class="bold-larger">📍 통합국명을 선택하세요:</p>', unsafe_allow_html=True)
    selected_location = st.selectbox("", ["전체"] + unique_locations)

    filtered_data = data if selected_location == "전체" else data[data['통합국명'] == selected_location]

    # CSV 다운로드 버튼
    st.download_button(
        label="CSV 다운로드",
        data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{selected_location}_온도데이터.csv",
        mime='text/csv'
    )

    # 데이터의 마지막 날짜를 기준으로 1주일 데이터 필터링
    last_date = filtered_data['날짜'].max()
    one_week_data = filtered_data[filtered_data['날짜'] >= last_date - timedelta(days=7)]

    # 최신 데이터 및 1주일 평균 온도 계산
    latest_data = filtered_data.sort_values(by='날짜', ascending=False).groupby('모듈번호').first().reset_index()
    daily_avg_temp_data = one_week_data.groupby(one_week_data['날짜'].dt.date)['온도'].mean().reset_index()
    daily_avg_temp_data.columns = ['날짜', '평균 온도']

    # 통계 정보 출력
    st.markdown('<p class="medium-font">📈 <b>각 모듈번호의 현재 온도:</b></p>', unsafe_allow_html=True)
    st.dataframe(latest_data[['모듈번호', '온도']])

    max_module = latest_data.loc[latest_data['온도'].idxmax()]
    st.markdown(f'<p class="medium-font">🔥 <b>가장 높은 온도를 가진 모듈번호:</b> {max_module["모듈번호"]} (온도: {max_module["온도"]}°C)</p>', unsafe_allow_html=True)

    st.markdown('<p class="medium-font">🌡️ <b>최근 1주일 평균 온도:</b></p>', unsafe_allow_html=True)
    st.dataframe(daily_avg_temp_data)

    # 주간 최고/최저 온도 데이터 표시
    max_temp_row = one_week_data.loc[one_week_data['온도'].idxmax()]
    min_temp_row = one_week_data.loc[one_week_data['온도'].idxmin()]
    styled_week_data = pd.DataFrame({
        '날짜': [max_temp_row['날짜'].date(), min_temp_row['날짜'].date()],
        '온도': [max_temp_row['온도'], min_temp_row['온도']],
        '유형': ['최고 온도', '최저 온도']
    }).style.applymap(lambda val: 'color: red' if val >= 31 else 'color: black', subset=['온도'])
    st.dataframe(styled_week_data)

    # 그래프 선택 및 시각화
    graph_type = st.selectbox("📊 보고 싶은 그래프를 선택하세요:", ["전체 보기", "최근 24시간 평균 온도", "2주 평균 온도", "일단위 최대 온도"])

    def plot_graph(graph_type):
        if graph_type in ["전체 보기", "최근 24시간 평균 온도"]:
            recent_data = filtered_data[filtered_data['날짜'] >= last_date - timedelta(hours=24)]
            hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(hourly_avg.index, hourly_avg.values, marker='o')
            ax.set_title('최근 24시간 시간대별 평균 온도', fontsize=18)
            ax.set_xticks([])  # 가로축 레이블 제거
            ax.set_ylabel('평균 온도 (°C)', fontsize=16)
            plt.grid(True)
            st.pyplot(fig)

        if graph_type in ["전체 보기", "2주 평균 온도"]:
            two_weeks_data = filtered_data[filtered_data['날짜'] >= last_date - timedelta(days=14)]
            two_weeks_avg = two_weeks_data.groupby(two_weeks_data['날짜'].dt.strftime('%m-%d'))['온도'].mean()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o')
            ax.set_title('2주 평균 온도', fontsize=18)
            ax.set_xticks([])  # 가로축 레이블 제거
            ax.set_ylabel('평균 온도 (°C)', fontsize=16)
            plt.grid(True)
            st.pyplot(fig)

        if graph_type in ["전체 보기", "일단위 최대 온도"]:
            daily_max = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(daily_max.index, daily_max.values, marker='o')
            ax.set_title('일단위 최대 온도', fontsize=18)
            ax.set_xticks([])  # 가로축 레이블 제거
            ax.set_ylabel('최대 온도 (°C)', fontsize=16)
            plt.grid(True)
            st.pyplot(fig)

    plot_graph(graph_type)
