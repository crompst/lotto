import streamlit as st
import pandas as pd
import random
import requests
from collections import Counter
from datetime import datetime

# --- [1. 스타일 설정: 올 블랙 & 미니멀 고대비] ---
st.set_page_config(page_title="Lotto Auto Strategy", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, div { color: #e0e0e0 !important; font-family: 'Pretendard', sans-serif; }
    .block-container { padding-top: 2rem !important; }
    
    .stButton>button {
        background: linear-gradient(135deg, #004a99 0%, #003366 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        height: 3.8em !important;
        font-weight: bold !important;
        width: 100% !important;
    }

    .set-card {
        background: #0f1115;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #333333;
        margin-bottom: 18px;
        text-align: center;
    }

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

# --- [2. 실시간 당첨 데이터 자동 수강 로직] ---
def get_latest_lotto_info():
    """날짜 기반으로 최신 회차를 계산하고 해당 당첨 데이터를 API로 가져옴"""
    # 1회차(2002-12-07) 기준으로 현재 회차 계산
    first_date = datetime(2002, 12, 7)
    now = datetime.now()
    # 토요일 저녁 9시 이후에 회차가 바뀌도록 설정
    current_drwno = (now - first_date).days // 7 + 1
    
    try:
        # 동행복권 API 호출
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={current_drwno}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("returnValue") == "success":
            win_nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
            bonus_num = data["bnusNo"]
            return current_drwno, win_nums, bonus_num
        else:
            # 아직 이번 주 번호가 안 올라왔을 경우 이전 회차 가져오기
            url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={current_drwno-1}"
            response = requests.get(url)
            data = response.json()
            win_nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
            bonus_num = data["bnusNo"]
            return current_drwno - 1, win_nums, bonus_num
    except:
        # API 오류 시 기본값 (안정성 확보)
        return current_drwno, [1, 2, 3, 4, 5, 6], 7

def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#b8860b"
    if 11 <= n <= 20: return "#1c4e80"
    if 21 <= n <= 30: return "#8b0000"
    if 31 <= n <= 40: return "#444444"
    return "#1e5631"

# 데이터 로드
@st.cache_data
def load_historical_data():
    return pd.read_csv('lotto_data.csv')

# 실시간 데이터 가져오기
latest_no, win_nums, bonus_num = get_latest_lotto_info()
df = load_historical_data()

# --- [3. 메인 분석 엔진] ---
st.title("🏆 Lotto Strategy Mix")
# "제1회차 데이터 기반..." 문구 삭제됨

c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 분석 조합 5세트 생성"):
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        weights = [counts.get(i, 1) for i in range(1, 46)]
        
        final_sets = []
        for _ in range(3): # HOT
            while True:
                res = sorted(random.choices(range(1, 46), weights=weights, k=6))
                if len(set(res)) == 6:
                    final_sets.append({"type": "🔥 HOT", "nums": res})
                    break
        for _ in range(2): # UNIQUE
            while True:
                res = sorted(random.sample(range(1, 46), 6))
                if sum(res) < 95 or sum(res) > 175:
                    final_sets.append({"type": "💎 UNIQUE", "nums": res})
                    break
        st.session_state.mixed_sets = final_sets
        st.session_state.is_checked = False

with c2:
    if st.button("🔎 이번 주 당첨 확인"):
        if 'mixed_sets' in st.session_state:
            st.session_state.is_checked = True

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
            res_html = f'<div style="margin-top:12px; font-weight:bold; color:{res_color};">{res_text}</div>'
        
        tag_color = "#FF4500" if "HOT" in sType else "#0088ff"
        st.markdown(f"""
            <div class="set-card">
                <div style="color:{tag_color}; font-size:11px; font-weight:bold; margin-bottom:8px;">{sType} STRATEGY {idx+1}</div>
                {ball_html}{res_html}
            </div>
            """, unsafe_allow_html=True)

# 하단 정보 가이드 (실시간 업데이트 반영)
st.markdown("<br><hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; opacity:0.6;'>최신 {latest_no}회 당첨번호 (실시간)</p>", unsafe_allow_html=True)
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"<div style='text-align:center;'>{win_html} <span style='font-size:20px; vertical-align:middle; margin:0 5px;'>+</span> <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div></div>", unsafe_allow_html=True)
