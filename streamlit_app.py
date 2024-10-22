import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 폰트 경로 설정 (Windows, Mac, Linux에 맞게 수정)
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # Ubuntu 예시
# font_path = "C:/Windows/Fonts/NanumGothic.ttf"  # Windows 예시
# font_path = "/Library/Fonts/NanumGothic.ttf"  # Mac 예시

# 폰트 설정
font_prop = fm.FontProperties(fname=font_path)
plt.rc('font', family=font_prop.get_name())

# 그래프 예제
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot([1, 2, 3, 4], [25.3, 26.1, 26.8, 27.0], marker='o', linestyle='-', linewidth=2)
ax.set_title('최근 24시간 시간대별 평균 온도', fontsize=15)
ax.set_xlabel('시간대 (시)', fontsize=12)
ax.set_ylabel('평균 온도 (°C)', fontsize=12)
plt.grid(True)

# 그래프 표시
plt.show()
