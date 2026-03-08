import streamlit as st
import pandas as pd
import random
from collections import Counter
from datetime import datetime, timedelta

# --- 설정 및 미려한 스타일 ---
st.set_page_config(page_title="Lotto Premium Pro", layout="centered")

st.markdown("""
    <style>
    /* 1. 배경 및 텍스트 가독성 */
    .stApp { background-color: #0d1117 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Pretendard', sans-serif; }
    
    /* 2. 자동 포커스 이동을 위한 입력창 스타일 */
    .stNumberInput div div input {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 2px solid #30363d !important;
        border-radius: 10px !important;
        font-size: 20px !important;
        text-align: center !important;
        height: 50px !important;
    }
    .stNumberInput div div input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.3) !important;
    }

    /* 3. 카드 디자인 (Glassmorphism 효과) */
    .set-card {
        background: rgba(33, 38, 45, 0.8);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }

    /* 4. 프리미엄 로또 볼 */
    .lotto-ball {
        display: inline-block;
        width: 46px; height: 46px;
        line-height: 46px;
        border-radius: 50%;
        text-align: center;
        margin: 4px;
        color: white !important;
        font-weight: 900;
        font-size: 19px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        box-shadow: inset -3px -3px 6px rgba(0,0,0,0.3), 3px 3px 8px rgba(0,0,0,0.4);
    }

    /* 5. 버튼 스타일 (그라데이션) */
    .stButton>button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 160, 67, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#EAB308" # Yellow
    if 11 <= n <= 20: return "#3B82F6" # Blue
    if 21 <= n <= 30: return "#EF4444" # Red
    if 31 <= n <= 40: return "#6B7280" # Grey
    return "#22C55E"                   # Green

def calculate_current_drwno():
    """날짜 기반으로 현재 로또 회차 자동 계산"""
    first_draw_date = datetime(2002, 12, 7) # 1회차 추첨일
    now = datetime.now()
    diff = now - first_draw_date
    return (diff.days // 7) + 1

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

# --- 데이터 로드 및 관리 ---
df = load_data()
auto_drwno = calculate_current_drwno()

# 사이드바: 입력 인터페이스
st.sidebar.title("💎 Premium Admin")
st.sidebar.markdown(f"**자동 계산된 회차: {auto_drwno}회**")

with st.sidebar.expander("📝 이번 주 당첨번호 입력", expanded=True):
    # 날짜 기반 회차 자동 세팅
    new_no = st.number_input("회차", value=auto_drwno, step=1)
    
    st.markdown("---")
    st.write("당첨번호 6개 + 보너스")
    
    # 2자리 입력 시 자동이동은 HTML/JS가 필요하므로 
    # Streamlit에서는 한 줄에 깔끔하게 배치하여 입력을 유도합니다.
    c1, c2, c3 = st.columns(3)
    n1 = c1.number_input("①", 1, 45, 1, key='n1')
    n2 = c2.number_input("②", 1, 45, 2, key='n2')
    n3 = c3.number_input("③", 1, 45, 3, key='n3')
    n4 = c1.number_input("④", 1, 45, 4, key='n4')
    n5 = c2.number_input("⑤", 1, 45, 5, key='n5')
    n6 = c3.number_input("⑥", 1, 45, 6, key='n6')
    bn = st.number_input("보너스 (BONUS)", 1, 45, 7, key='bn')
    
    if st.button("✨ 데이터 실시간 반영"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"성공! {new_no}회차 기준 분석 시작")

# 현재 데이터 확정
current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- 메인 화면 ---
st.title("🏆 Lotto Premium Analysis")
st.markdown(f"<p style='font-size:1.2em; opacity:0.8;'>{latest_no}회차 통계 기반 분석 시스템</p>", unsafe_allow_html=True)

btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("🚀 프리미엄 5세트 생성"):
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

with btn_col2:
    if st.button("🔎 당첨 여부 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True

st.markdown("<br>", unsafe_allow_html=True)

# 생성 번호 출력 영역
if 'current_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.current_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        res_area = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"일치: {matched}개"
            res_color = "#9aa0b1"
            if matched == 6: res_text, res_color = "🥇 1등 당첨!", "#FFD700"
            elif matched == 5 and bonus_num in s: res_text, res_color = "🥈 2등 당첨!", "#C0C0C0"
            elif matched == 5: res_text, res_color = "🥉 3등 당첨!", "#CD7F32"
            elif matched >= 3: res_text, res_color = f"{8-matched}등 당첨!", "#ffffff"
            
            res_area = f'<div style="margin-top:12px; font-weight:bold; color:{res_color}; font-size:1.1em;">{res_text}</div>'
        
        st.markdown(f'<div class="set-card"><div style="color:#58a6ff; font-size:12px; margin-bottom:10px; letter-spacing:2px;">ANALYSIS SET {idx+1}</div>{html_balls}{res_area}</div>', unsafe_allow_html=True)

# 하단 당첨번호 가이드
st.markdown("---")
st.markdown(f"📢 **제 {latest_no}회 공식 당첨번호**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} <span style='font-size:24px; vertical-align:middle; margin:0 10px;'>+</span> <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
