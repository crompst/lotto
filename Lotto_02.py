import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto AI Analyzer", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #1a1c24; }
    h1, h2, h3, p, div { color: #ffffff !important; }
    .set-card {
        background-color: #2d303d;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3e4255;
        position: relative;
        margin-bottom: 20px;
        text-align: center;
    }
    /* 적합도 점수 배지 스타일 */
    .score-badge {
        position: absolute;
        top: -10px;
        right: -10px;
        background: linear-gradient(135.deg, #ff5f6d, #ffc371);
        color: white !important;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
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

# --- 점수 계산 엔진 ---
def calculate_score(nums, counts):
    score = 0
    # 1. 빈도 점수 (Max 40)
    freq_sum = sum([counts.get(n, 1) for n in nums])
    max_possible_freq = sum(sorted(counts.values(), reverse=True)[:6])
    score += (freq_sum / max_possible_freq) * 40
    
    # 2. 합계 점수 (Max 30) - 138에 가까울수록 고득점
    total_sum = sum(nums)
    dist = abs(138 - total_sum)
    score += max(0, 30 - (dist * 0.5))
    
    # 3. 홀짝 점수 (Max 30) - 3:3일 때 최고
    odds = len([n for n in nums if n % 2 != 0])
    if odds == 3: score += 30
    elif odds in [2, 4]: score += 20
    else: score += 10
    
    return round(score, 1)

def generate_scored_set(weights, counts):
    while True:
        res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        if len(set(res)) < 6: continue
        
        # 기본 필터링 (최소한의 가이드)
        if not (90 <= sum(res) <= 185): continue
        
        score = calculate_score(res, counts)
        # 점수가 80점 이상인 '우량 조합'만 반환
        if score >= 80:
            return res, score

# --- 메인 UI ---
st.title("🛡️ Lotto Scored Picker")
st.write("통계적 적합도를 계산하여 상위 20% 이내의 조합만 추천합니다.")

if st.button("📊 정밀 분석 세트 생성 (Score 표시)"):
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    weights = [counts.get(i, 1) for i in range(1, 46)]
    
    st.session_state.scored_sets = [generate_scored_set(weights, counts) for _ in range(5)]

st.divider()

if 'scored_sets' in st.session_state:
    for idx, (s, score) in enumerate(st.session_state.scored_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        st.markdown(f"""
        <div class="set-card">
            <div class="score-badge">적합도 {score}%</div>
            <div style="color:#9aa0b1; font-size:12px; margin-bottom:10px;">PROBABILITY ANALYSIS SET {idx+1}</div>
            {html_balls}
        </div>
        """, unsafe_allow_html=True)
