import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto Hot-Pick", layout="centered")

# 다크 테마 및 고대비 스타일 적용
st.markdown("""
    <style>
    /* 전체 배경을 어두운 네이비톤으로 설정 */
    .stApp { 
        background-color: #1a1c24; 
    }
    
    /* 텍스트 색상 전체 조정 */
    h1, h2, h3, p, div {
        color: #ffffff !important;
    }

    /* 번호 세트 카드 디자인 (배경과 확연히 구분되도록 어두운 회색) */
    .set-card {
        background-color: #2d303d;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3e4255;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px;
        text-align: center;
    }
    
    .set-label {
        color: #9aa0b1;
        font-size: 13px;
        margin-bottom: 10px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 로또 공 디자인 */
    .lotto-ball {
        display: inline-block;
        width: 45px; height: 45px;
        line-height: 45px;
        border-radius: 50%;
        text-align: center;
        margin: 5px;
        color: white;
        font-weight: 800;
        font-size: 18px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.4);
    }

    /* 버튼 스타일 강화 */
    .stButton>button {
        background-color: #4e73df;
        color: white;
        border: none;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        font-size: 18px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2e59d9;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

def get_ball_color(n):
    if 1 <= n <= 10: return "#EDB100" # 골드 노랑
    if 11 <= n <= 20: return "#2885D6" # 블루
    if 21 <= n <= 30: return "#E85151" # 레드
    if 31 <= n <= 40: return "#7A7A7A" # 그레이
    return "#59A616"                   # 그린

# 데이터 읽기
try:
    df = pd.read_csv('lotto_data.csv')
except:
    st.error("데이터 파일이 없습니다.")
    st.stop()

# --- 메인 대시보드 ---
st.title("🔥 Hot-Number Picker")
st.write("과거 당첨 빈도가 높은 번호들을 분석하여 5세트를 추천합니다.")

# 번호 생성 로직 (고빈도 가중치 고정)
if
