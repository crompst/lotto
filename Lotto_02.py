import streamlit as st
import pandas as pd
import random
from collections import Counter
from datetime import datetime

# --- [1. 화이트 제거 & 고대비 다크 스타일] ---
st.set_page_config(page_title="Lotto Dark Vision", layout="centered")

st.markdown("""
    <style>
    /* 1. 배경을 완전한 블랙으로 고정 (흰색 여백 제거) */
    .stApp { 
        background-color: #000000 !important; 
    }
    
    /* 2. 모든 흰색 칸 제거: 입력창 배경을 어두운 회색으로 */
    div[data-baseweb="input"] {
        background-color: #1a1a1a !important;
        border: 1px solid #FFFF00 !important; /* 테두리만 형광 노랑 */
    }

    /* 3. 입력창 내부 숫자 색상: 흰색 대신 형광 노란색 */
    .stNumberInput div div input {
        background-color: #1a1a1a !important;
        color: #FFFF00 !important;
        font-weight: bold !important;
        font-size: 24px !important;
        border: none !important;
    }

    /* 4. 사이드바 및 기타 요소에서 흰색 제거 */
    section[data-testid="stSidebar"] {
        background-color: #0c0c0c !important;
        border-right: 1px solid #333333;
    }
    
    /* 5. 텍스트는 보일 정도의 밝은 회색/연한 하늘색으로 조정 */
    h1, h2, h3, p, span, label, div { 
        color: #e0e0e0 !important; 
    }

    /* 6. 버튼: 클릭 시에도 흰색으로 변하지 않게 고정 */
    .stButton>button {
        background-color: #003d80 !important;
        color: #ffffff !important;
        border: 1px solid #0056b3 !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
    }
    .stButton>button:active, .stButton>button:focus {
        background-color: #003d80 !important;
        color: #ffffff !important;
    }

    /* 7. 결과 카드 디자인 */
    .set-card {
        background: #111111;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444444;
        margin-bottom: 20px;
        text-align: center;
    }

    /* 8. 로또 공: 눈부심을 방지하기 위해 밝기 소폭 하향 */
    .lotto-ball {
        display: inline-block;
        width: 45px; height: 45px;
        line-height: 45px;
        border-radius: 50%;
        text-align: center;
        margin: 4px;
        color: white !important;
        font-weight: 900;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터 및 로직] ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#b8860b" # 다크 골드
    if 11 <= n <= 20: return "#004080" # 다크 블루
    if 21 <= n <= 30: return "#8b0000" # 다크 레드
    if 31 <= n <= 40: return "#4f4f4f" # 다크 그레이
    return "#006400"                   # 다크 그린

def calculate_current_drwno():
    first_draw_date = datetime(2002, 12, 7)
    now = datetime.now()
    diff = now - first_draw_date
    return (diff.days // 7) + 1

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

df = load_data()
auto_drwno = calculate_current_drwno()

# --- [3. 사이드바 수동 입력 (화이트 제거 버전)] ---
st.sidebar.title("🛠️ ADMIN")
with st.sidebar:
    st.markdown("### 📝 당첨번호 입력")
    new_no = st.number_input("회차", value=auto_drwno, step=1)
    n1 = st.number_input("번호 1", 1, 45, 1, key='n1')
    n2 = st.number_input("번호 2", 1, 45, 2, key='n2')
    n3 = st.number_input("번호 3", 1, 45, 3, key='n3')
    n4 = st.number_input("번호 4", 1, 45, 4, key='n4')
    n5 = st.number_input("번호 5", 1, 45, 5, key='n5')
    n6 = st.number_input("번호 6", 1, 45, 6, key='n6')
    bn = st.number_input("보너스", 1, 45, 7, key='bn')
    
    if st.button("✨ 입력 완료"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success("데이터 반영됨!")

current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- [4. 메인 화면] ---
st.title("🏆 Lotto Analysis Pro")
st.markdown(f"#### 현재 기준: {latest_no}회차")

c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 분석 번호 생성"):
        all_nums = current_df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        sets = []
        for _ in range(5):
            res = sorted(random.choices(range(1, 46), weights=weights, k=6))
            while len(set(res)) < 6: res = sorted(random.choices(range(1, 46), weights=weights, k=6))
            sets.append(res)
        st.session_state.current_sets = sets
        st.session_state.is_checked = False

with c2:
    if st.button("🔎 당첨 결과 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True

if 'current_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.current_sets):
        ball_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        res_text = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"<div style='margin-top:10px; font-weight:bold; color:#FFFF00;'>맞은 개수: {matched}개</div>"
        st.markdown(f'<div class="set-card">SET {idx+1}<br>{ball_html}{res_text}</div>', unsafe_allow_html=True)

st.markdown("---")
st.write(f"📢 **이번 주 당첨번호 기준 ({latest_no}회)**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
