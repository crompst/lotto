import streamlit as st
import pandas as pd
import random
from collections import Counter
from datetime import datetime

# --- [1. 시인성 극대화 스타일 설정] ---
st.set_page_config(page_title="Lotto Premium Pro", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경을 아주 깊은 네이비로 고정 (라이트 모드 간섭 방지) */
    .stApp { background-color: #05070a !important; }
    
    /* 모든 글자를 흰색으로 강제하여 배경과 대비 생성 */
    h1, h2, h3, p, span, label, div { color: #ffffff !important; font-family: 'Pretendard', sans-serif; }
    
    /* 입력창(Number Input) 디자인 보정: 배경은 밝게, 숫자는 선명하게 */
    .stNumberInput div div input {
        background-color: #ffffff !important; /* 입력창 배경을 흰색으로 */
        color: #000000 !important; /* 숫자는 검정색으로 선명하게 */
        border: 2px solid #58a6ff !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 22px !important;
        height: 45px !important;
    }

    /* 사이드바 배경색 고정 */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }

    /* 결과 카드 디자인 */
    .set-card {
        background: #1c2128;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    /* 로또 볼 (입체감 강조) */
    .lotto-ball {
        display: inline-block;
        width: 44px; height: 44px;
        line-height: 44px;
        border-radius: 50%;
        text-align: center;
        margin: 4px;
        color: white !important;
        font-weight: 900;
        font-size: 18px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 유틸리티 함수] ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#eab308"
    if 11 <= n <= 20: return "#3b82f6"
    if 21 <= n <= 30: return "#ef4444"
    if 31 <= n <= 40: return "#6b7280"
    return "#22c55e"

def calculate_current_drwno():
    first_draw_date = datetime(2002, 12, 7)
    now = datetime.now()
    diff = now - first_draw_date
    return (diff.days // 7) + 1

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

# --- [3. 데이터 로드 및 사이드바 입력] ---
df = load_data()
auto_drwno = calculate_current_drwno()

st.sidebar.title("💎 Premium Admin")
st.sidebar.write(f"추천 회차: {auto_drwno}회")

with st.sidebar.expander("📝 이번 주 당첨번호 입력", expanded=True):
    new_no = st.number_input("회차 선택", value=auto_drwno, step=1)
    
    st.write("---")
    st.write("당첨번호 입력 (1~45)")
    # 입력 시 시각적 편의를 위해 그리드 배치
    c1, c2, c3 = st.columns(3)
    n1 = c1.number_input("1번", 1, 45, 1)
    n2 = c2.number_input("2번", 1, 45, 2)
    n3 = c3.number_input("3번", 1, 45, 3)
    n4 = c1.number_input("4번", 1, 45, 4)
    n5 = c2.number_input("5번", 1, 45, 5)
    n6 = c3.number_input("6번", 1, 45, 6)
    st.write("보너스")
    bn = st.number_input("Bonus", 1, 45, 7)
    
    if st.button("✨ 데이터 실시간 반영"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"{new_no}회차 반영 완료!")

# 데이터 확정
current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- [4. 메인 화면] ---
st.title("🏆 Lotto Premium Analysis")
st.write(f"현재 분석 기준: 제 {latest_no}회차")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🚀 프리미엄 5세트 생성"):
        all_nums = current_df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        sets = []
        for _ in range(5):
            while True:
                res = sorted(random.choices(range(1, 46), weights=weights, k=6))
                if len(set(res)) == 6:
                    sets.append(res)
                    break
        st.session_state.current_sets = sets
        st.session_state.is_checked = False

with col_b:
    if st.button("🔎 당첨 여부 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True

st.write("")

if 'current_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.current_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        res_area = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"일치: {matched}개"
            if matched == 6: res_text = "🥇 1등 당첨!"
            elif matched == 5 and bonus_num in s: res_text = "🥈 2등 당첨!"
            elif matched == 5: res_text = "🥉 3등 당첨!"
            res_area = f'<div style="margin-top:10px; font-weight:bold; color:#58a6ff;">{res_text}</div>'
        
        st.markdown(f'<div class="set-card"><div style="color:#8b949e; font-size:12px; margin-bottom:5px;">SET {idx+1}</div>{html_balls}{res_area}</div>', unsafe_allow_html=True)

# 하단 정보
st.write("---")
st.write(f"📢 **제 {latest_no}회 기준 당첨번호**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
