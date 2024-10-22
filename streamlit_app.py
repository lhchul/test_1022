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
        font_dir = r"C:\Users\SKTelecom\AppData\Local\Microsoft\Windows\Fonts"
        font_path = os.path.join(font_dir, "NanumGothic_0.ttf")
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
            plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
            st.success(f"폰트 설정 성공: {font_prop.get_name()}")
        except Exception as e:
            st.error(f"폰트 설정 실패: {e}")
            plt.rcParams['font.family'] = 'sans-serif'  # 기본 폰트로 폴백
    else:
        st.warning("NanumGothic 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'sans-serif'

# 폰트 설정 적용
set_font()

# 파일 저장 경로 설정
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 파일을 session_state에 저장하고 외부 접근 가능하게 처리
def save_file_to_session(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["uploaded_file_path"] = file_path
        st.success(f"파일이 저장되었습니다: {file_path}")
        st.write(f"[파일 다운로드](./{file_path})")  # 외부 접근 가능한 링크 제공

# 파일 업로드 또는 session_state에서 파일 불러오기
def get_uploaded_file():
    if "uploaded_file_path" in st.session_state:
        return st.session_state["uploaded_file_path"]
    else:
        uploaded_file = st.file_uploader("CSV 파일을 업로드하세요:", type="csv")
        if uploaded_file:
            save_file_to_session(uploaded_file)
            return os.path.join(UPLOAD_DIR, uploaded_file.name)
    return None

# Streamlit 앱 타이틀
st.title("온도 모니터링 대시보드")

# 업로드된 파일 가져오기
file_path = get_uploaded_file()

if file_path:
    # CSV 파일 읽기 및 날짜 변환
    data = pd.read_csv(file_path)
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
    st.subheader("최근 24시간 시간대별 평균 온도")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-', linewidth=2)
    ax1.set_title('최근 24시간 시간대별 평균 온도', fontsize=15)
    ax1.set_xlabel('시간대 (시)', fontsize=12)
    ax1.set_ylabel('평균 온도 (°C)', fontsize=12)
    plt.grid(True)
    st.pyplot(fig1)

    # 그래프 2: 2주 평균 온도
    st.subheader("2주 평균 온도")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(two_weeks_avg.index, two_weeks_avg.values, marker='o', linestyle='-', linewidth=2)
    ax2.set_title('2주 평균 온도', fontsize=15)
    ax2.set_xlabel('날짜 (월-일)', fontsize=12)
    ax2.set_ylabel('평균 온도 (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig2)

    # 그래프 3: 하루 중 최대 온도
    st.subheader("하루 중 최대 온도")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(daily_max.index, daily_max.values, marker='o', linestyle='-', linewidth=2)
    ax3.set_title('하루 중 최대 온도', fontsize=15)
    ax3.set_xlabel('날짜 (월-일)', fontsize=12)
    ax3.set_ylabel('최대 온도 (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig3)
