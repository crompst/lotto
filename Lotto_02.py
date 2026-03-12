import streamlit as st
import pandas as pd
import random
from collections import Counter
from datetime import datetime

# --- [1. 스타일 설정: 올 블랙 & 고대비] ---
st.set_page_config(page_title="Lotto Strategy Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label, div { color: #e0e0e0 !important; font-family: 'Pretendard', sans-serif; }
    
    /* 입력창: 화이트 제거, 다크 배경 + 형광 노랑 테두리 */
    .stNumberInput div div input {
        background-color: #1a1a1a !important;
        color: #FFFF00 !important;
        border: 1px solid #FFFF00 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 22px !important;
    }

    /* 버튼 스타일 고정 */
    .stButton>button {
        background-color: #003d80 !important;
        color: #ffffff !important;
        border: 1px solid #0056b3 !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
    }

    /* 결과 카드 */
    .set-card {
        background: #111111;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444444;
        margin-bottom: 15px;
        text-align: center;
    }

    /* 로또 공 */
    .lotto-ball {
        display: inline-block;
        width: 42px; height: 42px;
        line-height: 42px;
        border-radius: 50%;
        text-align: center;
        margin: 3px;
        color: white !important;
        font-weight: 900;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로직: 고빈도 및 비인기 생성] ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#b8860b"
    if 11 <= n <= 20: return "#004080"
    if 21 <= n <= 30: return "#8b0000"
    if 31 <= n <= 40: return "#4f4f4f"
    return "#006400"

def calculate_current_drwno():
    first_draw_date = datetime(2002, 12, 7)
    now = datetime.now()
    diff = now - first_draw_date
    return (diff.days // 7) + 1

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

# 데이터 로드
df = load_data()
auto_drwno = calculate_current_drwno()

# --- [3. 사이드바 수동 입력] ---
st.sidebar.title("🛠️ ADMIN")
with st.sidebar:
    st.markdown("### 📝 이번 주 당첨번호")
    new_no = st.number_input("회차", value=auto_drwno, step=1)
    n1 = st.number_input("번호 1", 1, 45, 1, key='n1')
    n2 = st.number_input("번호 2", 1, 45, 2, key='n2')
    n3 = st.number_input("번호 3", 1, 45, 3, key='n3')
    n4 = st.number_input("번호 4", 1, 45, 4, key='n4')
    n5 = st.number_input("번호 5", 1, 45, 5, key='n5')
    n6 = st.number_input("번호 6", 1, 45, 6, key='n6')
    bn = st.number_input("보너스", 1, 45, 7, key='bn')
    
    if st.button("✨ 데이터 반영"):
        new_row = {'회차': new_no, '번호1': n1, '번호2': n2, '번호3': n3, '번호4': n4, '번호5': n5, '번호6': n6, '보너스': bn}
        st.session_state.temp_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success("반영 완료")

current_df = st.session_state.get('temp_df', df)
latest_draw = current_df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- [4. 메인: 3(고빈도)+2(비인기) 생성 전략] ---
st.title("🏆 Strategy Mix (3+2)")
st.markdown(f"#### 분석 기준: 제 {latest_no}회차 데이터")

c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 전략적 5세트 생성"):
        all_nums = current_df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        
        # 가중치 기반 (Hot)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        final_sets = []
        
        # 1. 고빈도 조합 3개 생성
        for _ in range(3):
            while True:
                res = sorted(random.choices(range(1, 46), weights=weights, k=6))
                if len(set(res)) == 6:
                    final_sets.append({"type": "🔥 고빈도(HOT)", "nums": res})
                    break
        
        # 2. 비인기 조합 2개 생성 (패턴 기피 방식)
        for _ in range(2):
            while True:
                # 가중치 없이 완전 랜덤 추출
                res = sorted(random.sample(range(1, 46), 6))
                total_sum = sum(res)
                # 일반적인 합계 범위(100~170)를 벗어나거나 특정 끝수가 몰리는 경우를 선택
                if total_sum < 90 or total_sum > 180:
                    final_sets.append({"type": "💎 비인기(UNIQUE)", "nums": res})
                    break
        
        st.session_state.mixed_sets = final_sets
        st.session_state.is_checked = False

with c2:
    if st.button("🔎 당첨 결과 확인"):
        if 'mixed_sets' in st.session_state:
            st.session_state.is_checked = True

if 'mixed_sets' in st.session_state:
    for idx, data in enumerate(st.session_state.mixed_sets):
        s = data["nums"]
        sType = data["type"]
        ball_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        
        res_text = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"<div style='margin-top:8px; font-weight:bold; color:#FFFF00;'>맞은 개수: {matched}개</div>"
            if matched == 6: res_text = "<div style='margin-top:8px; font-weight:bold; color:#FFD700;'>🥇 1등 당첨!</div>"
        
        label_color = "#FF4500" if "HOT" in sType else "#58a6ff"
        st.markdown(f'''
            <div class="set-card">
                <div style="color:{label_color}; font-size:11px; margin-bottom:5px; font-weight:bold;">{sType} SET {idx+1}</div>
                {ball_html}
                {res_text}
            </div>
            ''', unsafe_allow_html=True)

st.divider()
st.write(f"📢 **{latest_no}회 당첨번호 (분석 기준)**")
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div>", unsafe_allow_html=True)
