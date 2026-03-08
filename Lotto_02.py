import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 스타일 ---
st.set_page_config(page_title="Lotto Probability Optimizer", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span { color: #ffffff !important; }
    .set-card {
        background-color: #1f2937;
        padding: 20px; border-radius: 15px; border: 1px solid #3b82f6;
        margin-bottom: 15px; text-align: center;
    }
    .lotto-ball {
        display: inline-block; width: 42px; height: 42px; line-height: 42px;
        border-radius: 50%; text-align: center; margin: 3px;
        color: white; font-weight: 800; font-size: 16px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border-radius: 12px; height: 4em; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

def get_ball_color(n):
    if 1 <= n <= 10: return "#fbbf24"
    if 11 <= n <= 20: return "#3b82f6"
    if 21 <= n <= 30: return "#ef4444"
    if 31 <= n <= 40: return "#9ca3af"
    return "#10b981"

# --- 핵심: 확률 최적화 엔진 ---
def optimize_lotto_set(weights, last_win_nums):
    while True:
        # 1. 가중치 기반 생성
        res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        if len(set(res)) < 6: continue
        
        # 2. 합계 필터 (가장 확률 높은 120~160 구간)
        if not (120 <= sum(res) <= 160): continue
        
        # 3. 홀짝 비율 (3:3 또는 2:4/4:2로 제한)
        odds = len([n for n in res if n % 2 != 0])
        if odds not in [2, 3, 4]: continue
        
        # 4. 이월수 필터 (지난주 번호가 1~2개 포함될 때 확률 높음)
        carry_over = len(set(res) & set(last_win_nums))
        if carry_over not in [1, 2]: continue
        
        # 5. AC값 계산 (복잡도 검증)
        diffs = set()
        for i in range(len(res)):
            for j in range(i + 1, len(res)):
                diffs.add(abs(res[i] - res[j]))
        ac_val = len(diffs) - (6 - 1)
        if ac_val < 7: continue # 패턴이 너무 단순하면 탈락
        
        return res, sum(res), odds

# --- UI 실행 ---
df = load_data()
latest_draw = df.iloc[-1]
last_nums = [latest_draw[f'번호{i}'] for i in range(1, 7)]

st.title("🛡️ Probability Optimizer")
st.write(f"현재 데이터 기준: **{int(latest_draw['회차'])}회차** 분석 중")

if st.button("🚀 확률 최적화 5세트 생성 (AC & 이월수 필터링)"):
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    weights = [counts.get(i, 1) for i in range(1, 46)]
    
    st.session_state.opt_sets = [optimize_lotto_set(weights, last_nums) for _ in range(5)]

st.divider()

if 'opt_sets' in st.session_state:
    for idx, (s, s_sum, s_odds) in enumerate(st.session_state.opt_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(int(n))}">{int(n)}</div>' for n in s])
        st.markdown(f"""
        <div class="set-card">
            <div style="color:#60a5fa; font-size:12px; margin-bottom:10px; font-weight:bold;">OPTIMIZED SET {idx+1}</div>
            {html_balls}
            <div style="font-size:11px; color:#9ca3af; margin-top:10px;">
                Sum: {s_sum} | Odds:Evens {s_odds}:{6-s_odds} | Carry-over: Included
            </div>
        </div>
        """, unsafe_allow_html=True)
