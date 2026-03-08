import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto Hot-Pick Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #1a1c24; }
    h1, h2, h3, p, div { color: #ffffff !important; }
    .set-card {
        background-color: #2d303d;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3e4255;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px;
        text-align: center;
    }
    .set-label { color: #9aa0b1; font-size: 13px; margin-bottom: 10px; font-weight: bold; text-transform: uppercase; }
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
    }
    .stButton>button { background-color: #4e73df; color: white; border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

def get_ball_color(n):
    if 1 <= n <= 10: return "#EDB100"
    if 11 <= n <= 20: return "#2885D6"
    if 21 <= n <= 30: return "#E85151"
    if 31 <= n <= 40: return "#7A7A7A"
    return "#59A616"

df = load_data()

# --- 고도화된 번호 생성 엔진 ---
def generate_advanced_set(weights):
    while True:
        # 1. 가중치 기반 랜덤 추출
        res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        
        # 중복 제거 확인
        if len(set(res)) < 6: continue
        
        # 2. 합계 필터 (100 ~ 175)
        total_sum = sum(res)
        if not (100 <= total_sum <= 175): continue
        
        # 3. 홀짝 비율 필터 (홀:짝 비율이 2:4, 3:3, 4:2 중 하나여야 함)
        odds = len([n for n in res if n % 2 != 0])
        if odds not in [2, 3, 4]: continue
        
        # 4. 연속 번호 필터 (3개 이상 연속 방지)
        consecutive = 0
        max_consecutive = 0
        for i in range(len(res)-1):
            if res[i] + 1 == res[i+1]:
                consecutive += 1
            else:
                consecutive = 0
            max_consecutive = max(max_consecutive, consecutive)
        if max_consecutive >= 2: continue # 3연번 이상 탈락
        
        return res

# --- 메인 UI ---
st.title("🚀 Advanced Hot-Picker")
st.write("빈도 분석 + 합계/홀짝/연번 필터가 적용된 정밀 알고리즘입니다.")

if st.button("🔥 정밀 분석된 5세트 생성"):
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    weights = [counts.get(i, 1) for i in range(1, 46)]
    
    st.session_state.lucky_sets = [generate_advanced_set(weights) for _ in range(5)]

st.divider()

if 'lucky_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.lucky_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        st.markdown(f"""
        <div class="set-card">
            <div class="set-label">Verified Set {idx+1}</div>
            {html_balls}
            <div style="font-size:11px; color:#666; margin-top:10px;">
                Sum: {sum(s)} | Odds: {len([n for n in s if n%2!=0])}
            </div>
        </div>
        """, unsafe_allow_html=True)
