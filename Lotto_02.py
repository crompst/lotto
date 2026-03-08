import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 고대비 스타일 ---
st.set_page_config(page_title="Lotto Admin Pro", layout="centered")

st.markdown("""
    <style>
    /* 1. 배경을 아주 어두운 색으로 고정 (글자 대비 강화) */
    .stApp { 
        background-color: #0b0e14 !important; 
    }
    
    /* 2. 모든 기본 텍스트를 흰색으로 강제 */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }

    /* 3. 사이드바 스타일 (배경색과 입력창 테두리 강조) */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #ecf2f8 !important;
        font-weight: bold;
    }

    /* 4. 입력창(Number Input) 배경 및 글자색 수정 */
    input {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 1px solid #58a6ff !important;
    }

    /* 5. 카드 및 공 디자인 */
    .set-card {
        background-color: #1c2128;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        text-align: center;
    }
    .lotto-ball {
        display: inline-block;
        width: 40px; height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        margin: 3px;
        color: white !important;
        font-weight: 800;
        font-size: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* 6. 버튼 스타일 */
    .stButton>button {
        background-color: #238636 !important; /* 초록색 버튼으로 변경 */
        color: white !important;
        border-radius: 8px;
        border: none;
        height: 3em;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 기본 함수 ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#d29922" # 금색
    if 11 <= n <= 20: return "#58a6ff" # 파랑
    if 21 <= n <= 30: return "#f85149" # 빨강
    if 31 <= n <= 40: return "#8b949e" # 회색
    return "#3fb950"                   # 초록

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

def check_winning(my_nums, win_nums, bonus):
    matched = len(set(my_nums) & set(win_nums))
    if matched == 6: return "🥇 1등 (축하합니다!)", "#ffd700"
    if matched == 5 and bonus in my_nums: return "🥈 2등 (보너스 일치!)", "#c0c0c0"
    if matched == 5: return "🥉 3등 (5개 일치)", "#cd7f32"
    if matched == 4: return "4등 (50,000원)", "#ffffff"
    if matched == 3: return "5등 (5,000원)", "#ffffff"
    return f"낙첨 (일치: {matched}개)", "#8b949e"

# --- 데이터 처리 ---
df = load_data()

# 사이드바: 수동 입력 관리
st.sidebar.title("🛠️ 관리자 설정")
st.sidebar.subheader("이번 주 당첨번호 입력")

with st.sidebar:
    new_no = st.number_input("회차", value=int(df.iloc[-1]['회차'])+1, step=1)
    
    st.write("당첨번호 6개")
    c1, c2, c3 = st.columns(3)
    n1 = c1.number_input("1", 1, 45, 1, key='n1')
    n2 = c2.number_input("2", 1, 45, 2, key='n2')
    n3 = c3.number_input("3", 1, 45, 3, key='n3')
    n4 = c1.number_input("4", 1, 45, 4, key='n4')
    n5 = c2.number_input("5", 1, 45, 5, key='n5')
    n6 = c3.number_input("6", 1, 45, 6, key='n6')
    
    bn = st.number_input("보너스 번호", 1, 45, 7)
    
    if st.button("데이터 즉시 반영"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"{new_no}회차 데이터가 반영되었습니다!")

# 실제 데이터 로드
current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- 메인 화면 ---
st.title("🎯 Lotto High-Contrast Pro")
st.subheader(f"현재 기준: 제 {latest_no}회차")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🚀 행운의 5세트 생성"):
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
    if st.button("🔎 당첨 결과 확인"):
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
        
        st.markdown(f'<div class="set-card"><div style="color:#8b949e; font-size:12px;">SET {idx+1}</div>{html_balls}{res_area}</div>', unsafe_allow_html=True)

# 하단 정보
st.write("---")
st.write(f"📢 **당첨 확인 기준 ({latest_no}회)**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
