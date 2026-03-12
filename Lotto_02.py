import streamlit as st
import pandas as pd
import random
from collections import Counter
from datetime import datetime

# --- [1. 스타일 설정: 올 블랙 & 미니멀 고대비] ---
st.set_page_config(page_title="Lotto Strategy Pro", layout="centered")

st.markdown("""
    <style>
    /* 배경 및 기본 텍스트 */
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, div { color: #e0e0e0 !important; font-family: 'Pretendard', sans-serif; }
    
    /* 불필요한 공백 제거 및 패딩 조절 */
    .block-container { padding-top: 2rem !important; }
    
    /* 버튼 디자인: 테두리 없이 깔끔한 다크 블루 그라데이션 */
    .stButton>button {
        background: linear-gradient(135deg, #004a99 0%, #003366 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        height: 3.8em !important;
        font-weight: bold !important;
        font-size: 16px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    /* 결과 카드: 테두리를 얇고 선명하게 */
    .set-card {
        background: #0f1115;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #333333;
        margin-bottom: 18px;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .set-card:hover { transform: translateY(-3px); border-color: #555555; }

    /* 로또 공: 입체감 있는 프리미엄 스타일 */
    .lotto-ball {
        display: inline-block;
        width: 44px; height: 44px;
        line-height: 44px;
        border-radius: 50%;
        text-align: center;
        margin: 4px;
        color: white !important;
        font-weight: 900;
        font-size: 17px;
        box-shadow: inset -2px -2px 4px rgba(0,0,0,0.4), 2px 2px 5px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로직 및 데이터 처리] ---
def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#b8860b" # 다크 골드
    if 11 <= n <= 20: return "#1c4e80" # 다크 블루
    if 21 <= n <= 30: return "#8b0000" # 다크 레드
    if 31 <= n <= 40: return "#444444" # 다크 그레이
    return "#1e5631"                   # 다크 그린

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

# 데이터 로드 (사이드바 입력란 삭제)
df = load_data()
latest_draw = df.iloc[-1]
latest_no = int(latest_draw['회차'])
win_nums = [int(latest_draw[f'번호{i}']) for i in range(1, 7)]
bonus_num = int(latest_draw['보너스'])

# --- [3. 메인 분석 엔진: 3(Hot) + 2(Unique)] ---
st.title("🏆 Lotto Strategy Mix")
st.markdown(f"<p style='opacity:0.7; font-size:1.1em;'>제 {latest_no}회차 데이터 기반 정밀 분석</p>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 분석 조합 5세트 생성"):
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        final_sets = []
        # 고빈도 3개
        for _ in range(3):
            while True:
                res = sorted(random.choices(range(1, 46), weights=weights, k=6))
                if len(set(res)) == 6:
                    final_sets.append({"type": "🔥 HOT", "nums": res})
                    break
        # 비인기 2개
        for _ in range(2):
            while True:
                res = sorted(random.sample(range(1, 46), 6))
                s = sum(res)
                if s < 95 or s > 175:
                    final_sets.append({"type": "💎 UNIQUE", "nums": res})
                    break
        
        st.session_state.mixed_sets = final_sets
        st.session_state.is_checked = False

with c2:
    if st.button("🔎 이번 주 당첨 확인"):
        if 'mixed_sets' in st.session_state:
            st.session_state.is_checked = True

st.markdown("<br>", unsafe_allow_html=True)

# 결과 출력
if 'mixed_sets' in st.session_state:
    for idx, data in enumerate(st.session_state.mixed_sets):
        s = data["nums"]
        sType = data["type"]
        ball_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        
        res_html = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"일치: {matched}개"
            res_color = "#FFFF00"
            if matched == 6: res_text, res_color = "🥇 1등 당첨!", "#FFD700"
            elif matched == 5 and bonus_num in s: res_text, res_color = "🥈 2등 당첨!", "#C0C0C0"
            elif matched >= 3: res_text, res_color = f"{8-matched}등 당첨", "#FFFFFF"
            
            res_html = f'<div style="margin-top:12px; font-weight:bold; color:{res_color}; font-size:1.1em;">{res_text}</div>'
        
        tag_color = "#FF4500" if "HOT" in sType else "#0088ff"
        st.markdown(f"""
            <div class="set-card">
                <div style="color:{tag_color}; font-size:11px; font-weight:bold; letter-spacing:2px; margin-bottom:8px;">{sType} STRATEGY {idx+1}</div>
                {ball_html}
                {res_html}
            </div>
            """, unsafe_allow_html=True)

# 하단 정보 가이드
st.markdown("<br><hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; opacity:0.6;'>제 {latest_no}회 공식 당첨번호</p>", unsafe_allow_html=True)
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"<div style='text-align:center;'>{win_html} <span style='font-size:20px; vertical-align:middle; margin:0 5px;'>+</span> <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div></div>", unsafe_allow_html=True)
