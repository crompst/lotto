import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto AI & Checker", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #1a1c24; }
    h1, h2, h3, p, div, span { color: #ffffff !important; }
    .set-card {
        background-color: #2d303d;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #4e73df;
        position: relative;
        margin-bottom: 20px;
        text-align: center;
    }
    .score-badge {
        position: absolute; top: -10px; right: -10px;
        background: linear-gradient(135deg, #4e73df, #224abe);
        color: white !important; padding: 5px 12px;
        border-radius: 20px; font-weight: bold; font-size: 12px;
    }
    .result-badge {
        margin-top: 10px; padding: 5px; border-radius: 8px;
        background-color: #3e4255; font-weight: bold; font-size: 14px;
    }
    .lotto-ball {
        display: inline-block; width: 40px; height: 40px;
        line-height: 40px; border-radius: 50%; text-align: center;
        margin: 3px; color: white; font-weight: 800; font-size: 16px;
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
latest_draw = df.iloc[-1] # 가장 최근 회차 데이터

# --- 로직: 당첨 확인 함수 ---
def check_win(my_nums, win_nums, bonus):
    matched = len(set(my_nums) & set(win_nums))
    if matched == 6: return "🥇 1등 (전부 일치!)"
    if matched == 5 and bonus in my_nums: return "🥈 2등 (5개 + 보너스)"
    if matched == 5: return "🥉 3등 (5개 일치)"
    if matched == 4: return "4등 (5,000원)"
    if matched == 3: return "5등 (5,000원)"
    return f"낙첨 ({matched}개 일치)"

# --- 메인 UI ---
st.title("🛡️ AI Picker & Checker")
st.write(f"현재 데이터 기준: **{int(latest_draw['회차'])}회차**")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🔥 고빈도 5세트 생성"):
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        new_sets = []
        for _ in range(5):
            res = sorted(random.choices(range(1, 46), weights=weights, k=6))
            while len(set(res)) < 6: res = sorted(random.choices(range(1, 46), weights=weights, k=6))
            new_sets.append(res)
        st.session_state.current_sets = new_sets
        st.session_state.checked = False

with col_btn2:
    if st.button("✅ 최신 회차 당첨 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.checked = True
        else:
            st.warning("번호를 먼저 생성하세요!")

st.divider()

# 결과 출력
if 'current_sets' in st.session_state:
    win_nums = [latest_draw['번호1'], latest_draw['번호2'], latest_draw['번호3'], 
                latest_draw['번호4'], latest_draw['번호5'], latest_draw['번호6']]
    bonus = latest_draw['보너스']

    for idx, s in enumerate(st.session_state.current_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(int(n))}">{int(n)}</div>' for n in s])
        
        result_html = ""
        if st.session_state.get('checked', False):
            res_text = check_win(s, win_nums, bonus)
            result_html = f'<div class="result-badge">{res_text}</div>'

        st.markdown(f"""
        <div class="set-card">
            <div class="score-badge">SET {idx+1}</div>
            {html_balls}
            {result_html}
        </div>
        """, unsafe_allow_html=True)

# 최신 당첨번호 안내 (참고용)
with st.expander("📢 최신 당첨번호 보기"):
    st.write(f"**제 {int(latest_draw['회차'])}회 당첨번호**")
    win_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(int(latest_draw[f"번호{i}"]))}">{int(latest_draw[f"번호{i}"])}</div>' for i in range(1, 7)])
    st.markdown(f"{win_balls} + <div class='lotto-ball' style='background-color:{get_ball_color(int(latest_draw['보너스']))}'>{int(latest_draw['보너스'])}</div>", unsafe_allow_html=True)
