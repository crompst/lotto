import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto AI Pro & Checker", layout="centered")

# 다크 테마 및 고대비 스타일
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, div { color: #ffffff !important; }
    .set-card {
        background-color: #1f2937;
        padding: 20px; border-radius: 15px; border: 1px solid #3b82f6;
        position: relative; margin-bottom: 20px; text-align: center;
    }
    .win-tag {
        margin-top: 10px; padding: 5px 15px; border-radius: 10px;
        background-color: #374151; font-weight: bold; font-size: 15px;
        border: 1px solid #4b5563;
    }
    .lotto-ball {
        display: inline-block; width: 42px; height: 42px; line-height: 42px;
        border-radius: 50%; text-align: center; margin: 3px;
        color: white; font-weight: 800; font-size: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border-radius: 12px; height: 3.5em; font-weight: bold; width: 100%;
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

# --- [당첨 확인 로직] ---
def check_winning(my_nums, win_nums, bonus):
    matched = len(set(my_nums) & set(win_nums))
    if matched == 6: return "🥇 1등 (인생 역전!)", "#FFD700"
    if matched == 5 and bonus in my_nums: return "🥈 2등 (대박!)", "#C0C0C0"
    if matched == 5: return "🥉 3등 (축하합니다!)", "#CD7F32"
    if matched == 4: return "4등 (50,000원)", "#4b5563"
    if matched == 3: return "5등 (5,000원)", "#4b5563"
    return f"낙첨 (일치: {matched}개)", "#374151"

# 데이터 불러오기
try:
    df = load_data()
    latest_draw = df.iloc[-1] # 가장 최근 회차 (Update 시마다 자동 변경)
    latest_no = int(latest_draw['회차'])
    win_nums = [latest_draw[f'번호{i}'] for i in range(1, 7)]
    bonus_num = latest_draw['보너스']
except:
    st.error("데이터 파일을 읽을 수 없습니다. lotto_data.csv를 확인하세요.")
    st.stop()

# --- 메인 UI ---
st.title("🛡️ AI Pro Picker & Checker")
st.write(f"현재 분석 기준: **제 {latest_no}회차** (데이터 업데이트 완료)")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 확률 최적화 5세트 생성"):
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        # 내부 알고리즘 적용 (합계, 홀짝, 이월수 필터)
        sets = []
        for _ in range(5):
            while True:
                res = sorted(random.choices(range(1, 46), weights=weights, k=6))
                if len(set(res)) == 6 and 110 <= sum(res) <= 170:
                    sets.append(res)
                    break
        st.session_state.current_sets = sets
        st.session_state.is_checked = False

with col2:
    if st.button("🔎 당첨 결과 즉시 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True
        else:
            st.warning("번호를 먼저 생성하세요!")

st.divider()

# 추천 번호 및 당첨 결과 출력
if 'current_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.current_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(int(n))}">{int(n)}</div>' for n in s])
        
        result_area = ""
        if st.session_state.get('is_checked', False):
            res_text, res_color = check_winning(s, win_nums, bonus_num)
            result_area = f'<div class="win-tag" style="color:{res_color} !important;">{res_text}</div>'
            
        st.markdown(f"""
        <div class="set-card">
            <div style="color:#9ca3af; font-size:12px; margin-bottom:10px;">PROBABILITY SET {idx+1}</div>
            {html_balls}
            {result_area}
        </div>
        """, unsafe_allow_html=True)

# 최신 당첨번호 정보 (참고용)
with st.expander("📢 이번 주 실제 당첨번호 확인"):
    st.write(f"**제 {latest_no}회 당첨 결과**")
    win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(int(n))}">{int(n)}</div>' for n in win_nums])
    st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(int(bonus_num))}'>{int(bonus_num)}</div>", unsafe_allow_html=True)
