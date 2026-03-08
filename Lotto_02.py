import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 스타일 ---
st.set_page_config(page_title="Lotto Admin Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, div { color: #ffffff !important; }
    .set-card {
        background-color: #1f2937; padding: 20px; border-radius: 15px; 
        border: 1px solid #3b82f6; margin-bottom: 20px; text-align: center;
    }
    .lotto-ball {
        display: inline-block; width: 40px; height: 40px; line-height: 40px;
        border-radius: 50%; text-align: center; margin: 3px;
        color: white; font-weight: 800; font-size: 16px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border-radius: 12px; height: 3.5em; font-weight: bold; width: 100%;
    }
    /* 입력창 스타일 */
    .stNumberInput div div input { background-color: #2d3748 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 기본 함수 ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#fbbf24"
    if 11 <= n <= 20: return "#3b82f6"
    if 21 <= n <= 30: return "#ef4444"
    if 31 <= n <= 40: return "#9ca3af"
    return "#10b981"

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

def check_winning(my_nums, win_nums, bonus):
    matched = len(set(my_nums) & set(win_nums))
    if matched == 6: return "🥇 1등 (인생역전!)", "#FFD700"
    if matched == 5 and bonus in my_nums: return "🥈 2등 (축하합니다!)", "#C0C0C0"
    if matched == 5: return "🥉 3등 (아쉽습니다!)", "#CD7F32"
    if matched == 4: return "4등 (50,000원)", "#ffffff"
    if matched == 3: return "5등 (5,000원)", "#ffffff"
    return f"낙첨 ({matched}개 일치)", "#9ca3af"

# --- 데이터 로드 및 수동 업데이트 로직 ---
df = load_data()

# 사이드바: 수동 번호 입력 관리
st.sidebar.header("🛠️ 이번 주 번호 수동 입력")
with st.sidebar.expander("신규 회차 추가하기"):
    new_no = st.number_input("회차", value=int(df.iloc[-1]['회차'])+1, step=1)
    c1, c2, c3 = st.columns(3)
    n1 = c1.number_input("번호1", 1, 45, 1)
    n2 = c2.number_input("번호2", 1, 45, 2)
    n3 = c3.number_input("번호3", 1, 45, 3)
    n4 = c1.number_input("번호4", 1, 45, 4)
    n5 = c2.number_input("번호5", 1, 45, 5)
    n6 = c3.number_input("번호6", 1, 45, 6)
    bn = st.number_input("보너스", 1, 45, 7)
    
    if st.sidebar.button("데이터 임시 반영"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"{new_no}회차 반영 완료!")

# 실제 사용할 데이터 결정 (임시 데이터가 있으면 그것을 사용)
current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- 메인 UI ---
st.title("🛡️ AI Picker & Manual Checker")
st.subheader(f"현재 분석 기준: 제 {latest_no}회차")

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 확률 최적화 5세트 생성"):
        all_nums = current_df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        sets = []
        for _ in range(5):
            while True:
                res = sorted(random.choices(range(1, 46), weights=weights, k=6))
                if len(set(res)) == 6 and 110 <= sum(res) <= 175:
                    sets.append(res)
                    break
        st.session_state.current_sets = sets
        st.session_state.is_checked = False

with col2:
    if st.button("🔎 당첨 결과 즉시 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True

st.divider()

if 'current_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.current_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        res_area = ""
        if st.session_state.get('is_checked', False):
            res_text, res_color = check_winning(s, win_nums, bonus_num)
            res_area = f'<div style="margin-top:10px; font-weight:bold; color:{res_color};">{res_text}</div>'
        st.markdown(f'<div class="set-card">SET {idx+1}<br>{html_balls}{res_area}</div>', unsafe_allow_html=True)

# 현재 기준 당첨번호 표시
st.write("---")
st.write(f"📢 **현재 당첨 확인 기준 ({latest_no}회)**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
