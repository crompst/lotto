import streamlit as st
import pandas as pd
import random
from collections import Counter
from datetime import datetime

# --- [1. 시인성 극대화 및 고대비 테마 설정] ---
st.set_page_config(page_title="Lotto High-Contrast Pro", layout="centered")

st.markdown("""
    <style>
    /* 배경은 완전한 검정색으로 고정 */
    .stApp { background-color: #000000 !important; }
    
    /* 모든 텍스트를 순백색으로 강제 */
    h1, h2, h3, p, span, label, div { color: #ffffff !important; font-family: 'Pretendard', sans-serif; }
    
    /* 입력창 디자인: 노란색 테두리와 흰색 배경으로 시인성 확보 */
    .stNumberInput div div input {
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border: 3px solid #FFD700 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 24px !important;
        height: 50px !important;
    }

    /* 사이드바 가독성 강화 */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 2px solid #FFD700;
    }

    /* 결과 카드: 테두리를 밝게 하여 구분감 생성 */
    .set-card {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #444444;
        margin-bottom: 20px;
        text-align: center;
    }

    /* 로또 공: 그림자 효과를 강화하여 더 선명하게 */
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
        box-shadow: 3px 3px 10px rgba(0,0,0,0.8);
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 핵심 로직 및 데이터 처리] ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#EAB308"
    if 11 <= n <= 20: return "#3B82F6"
    if 21 <= n <= 30: return "#EF4444"
    if 31 <= n <= 40: return "#6B7280"
    return "#22C55E"

def calculate_current_drwno():
    first_draw_date = datetime(2002, 12, 7)
    now = datetime.now()
    diff = now - first_draw_date
    return (diff.days // 7) + 1

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

# 데이터 로딩
try:
    df = load_data()
except:
    st.error("lotto_data.csv 파일을 찾을 수 없습니다.")
    st.stop()

auto_drwno = calculate_current_drwno()

# --- [3. 사이드바 수동 입력창] ---
st.sidebar.title("🛠️ 번호 수동 입력")
st.sidebar.write("글씨가 안 보일 땐 아래 칸에 집중하세요!")

with st.sidebar:
    new_no = st.number_input("회차", value=auto_drwno, step=1)
    st.markdown("---")
    st.write("당첨번호 6개 입력")
    # 한 줄에 하나씩 배치하여 가독성 확보
    n1 = st.number_input("첫 번째 번호", 1, 45, 1, key='n1')
    n2 = st.number_input("두 번째 번호", 1, 45, 2, key='n2')
    n3 = st.number_input("세 번째 번호", 1, 45, 3, key='n3')
    n4 = st.number_input("네 번째 번호", 1, 45, 4, key='n4')
    n5 = st.number_input("다섯 번째 번호", 1, 45, 5, key='n5')
    n6 = st.number_input("여섯 번째 번호", 1, 45, 6, key='n6')
    bn = st.number_input("보너스 번호", 1, 45, 7, key='bn')
    
    if st.button("✨ 입력 완료 (즉시 반영)"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"{new_no}회차 반영됨!")

# 최종 데이터 확정
current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- [4. 메인 분석 영역] ---
st.title("🏆 Lotto Analysis Pro")
st.write(f"분석 기준 회차: **제 {latest_no}회**")

c_btn1, c_btn2 = st.columns(2)
with c_btn1:
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

with c_btn2:
    if st.button("🔎 당첨 결과 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True

st.markdown("<br>", unsafe_allow_html=True)

if 'current_sets' in st.session_state:
    for idx, s in enumerate(st.session_state.current_sets):
        # 공 색상 함수(get_ball_color) 호출 오류 방지
        ball_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        
        res_text = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"<div style='margin-top:10px; font-weight:bold; color:#FFD700;'>일치 개수: {matched}개</div>"
            if matched == 6: res_text = "<div style='margin-top:10px; font-weight:bold; color:#FFD700;'>🥇 1등 당첨!</div>"
        
        st.markdown(f'<div class="set-card">SET {idx+1}<br>{ball_html}{res_text}</div>', unsafe_allow_html=True)

# 하단 당첨번호 안내
st.write("---")
st.write(f"📢 **현재 당첨 확인 기준 ({latest_no}회)**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
