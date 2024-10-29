# 필요한 라이브러리 임포트
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
from datetime import timedelta
import streamlit as st

# NanumGothic 폰트 설정
def set_font():
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 폰트 설정 적용
set_font()

# CSV 파일 업로드 및 데이터 로딩 (Colab 환경에서는 수동으로 업로드 필요)
from google.colab import files
uploaded = files.upload()

# 업로드한 CSV 파일 읽기
for filename in uploaded.keys():
    data = pd.read_csv(filename)
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
plt.figure(figsize=(10, 5))
plt.plot(daily_avg_temp_data['날짜'], daily_avg_temp_data['평균 온도'], marker='o', linestyle='-')
plt.title('최근 1주일 평균 온도', fontsize=18)
plt.ylabel('평균 온도 (°C)', fontsize=16)
plt.grid(True)
plt.xticks(rotation=45)  # 날짜 라벨 회전
plt.show()

# 최근 24시간 데이터 필터링 및 시간대별 평균 계산
recent_data = data[data['날짜'] >= last_date - timedelta(hours=24)]
hourly_avg = recent_data.groupby(recent_data['날짜'].dt.hour)['온도'].mean()

# 최근 24시간 시간대별 평균 온도 그래프
plt.figure(figsize=(10, 5))
plt.plot(hourly_avg.index, hourly_avg.values, marker='o', linestyle='-')
plt.title('최근 24시간 시간대별 평균 온도', fontsize=18)
plt.xlabel('시간대 (시)', fontsize=16)
plt.ylabel('평균 온도 (°C)', fontsize=16)
plt.grid(True)
plt.show()
