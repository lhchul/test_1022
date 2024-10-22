import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
from flask import Flask, send_from_directory
import threading

# Flask 애플리케이션 생성
app = Flask(__name__)
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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
            plt.rcParams['axes.unicode_minus'] = False
            st.success(f"폰트 설정 성공: {font_prop.get_name()}")
        except Exception as e:
            st.error(f"폰트 설정 실패: {e}")
            plt.rcParams['font.family'] = 'sans-serif'
    else:
        st.warning("NanumGothic 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'sans-serif'

# Flask 경로에서 업로드된 파일 제공
@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# Streamlit 파일 업로드 및 경로 반환
def save_file(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["uploaded_file_path"] = file_path
        return uploaded_file.name
    return None

# Flask 서버 시작 함수
def start_flask():
    app.run(port=8501)

# Flask 서버를 별도의 스레드에서 실행
threading.Thread(target=start_flask, daemon=True).start()

# Streamlit 앱 타이틀 및 파일 업로드 인터페이스
st.title("온도 모니터링 대시보드")
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요:", type="csv")

if uploaded_file:
    filename = save_file(uploaded_file)
    if filename:
        file_url = f"http://localhost:8501
