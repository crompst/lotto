import streamlit as st
import pandas as pd
import random
import requests
from collections import Counter
from datetime import datetime

# --- [1. 스타일 설정: 올 블랙 & 미니멀] ---
st.set_page_config(page_title="Lotto Auto-Evolution Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, div { color: #e0e0e0 !important; font-family: 'Pretendard', sans-serif; }
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
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 로직: 실시간 데이터 수집 및 과거 데이터 병합] ---
def get_lotto_data(drwNo):
    """특정 회차의 당첨 데이터를 API에서 가져옴"""
    try:
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drwNo}"
        data = requests.get(url, timeout=5).json()
        if data.get("returnValue") == "success":
            return {
                '회차': drwNo,
                '번호1': data['drwtNo1'], '번호2': data['drwtNo2'], '번호3': data['drwtNo3'],
                '번호4': data['drwtNo4'], '번호5': data['drwtNo5'], '번호6': data['drwtNo6'],
                '보너스': data['bnusNo']
            }
    except:
        return None

def get_latest_info_and_update_df():
    """현재 회차를 계산하고, 과거 CSV 데이터에 최신 정보를 실시간으로 덧붙여 분석용 DF 생성"""
    first_date = datetime(2002, 12, 7)
    now = datetime.now()
    # 현재 시점의 최신 회차 (토요일 밤 9시 기준)
    calc_no = (now - first_date).days // 7 + 1
    
    # 1. 과거 CSV 로드
    df_hist = pd.read_csv('lotto_data.csv')
    last_csv_no = df_hist.iloc[-1]['회차']
    
    # 2. CSV 이후의 누락된 데이터부터 현재 직전 회차까지 실시간으로 가져와 병합
    # 예: CSV가 1160회까지 있다면 1161, 1162... 현재 직전까지 자동으로 채움
    missing_data = []
    for no in range(int(last_csv_no) + 1, calc_no):
        d = get_lotto_data(no)
        if d: missing_data.append(d)
    
    if missing_data:
        df_hist = pd.concat([df_hist, pd.DataFrame(missing_data)], ignore_index=True)
    
    # 3. 이번 주 당첨 정보 (확인용)
    current_win_info = get_lotto_data(calc_no)
    if not current_win_info: # 아직 발표 전이면 이전 회차 정보 사용
        calc_no -= 1
        current_win_info = get_lotto_data(calc_no)
        
    return calc_no, current_win_info, df_hist

def get_ball_color(n):
    n = int(n)
    if 1 <= n <= 10: return "#b8860b"
    if 11 <= n <= 20: return "#1c4e80"
    if 21 <= n <= 30: return "#8b0000"
    if 31 <= n <= 40: return "#444444"
    return "#1e5631"

# 데이터 실행 및 준비
target_no, win_info, analysis_df = get_latest_info_and_update_df()
win_nums = [win_info[f'번호{i}'] for i in range(1, 7)]
bonus_num = win_info['보너스']

# --- [3. 고정 분석 생성기] ---
def generate_fixed_strategy(seed_no, df):
    random.seed(seed_no) # 회차 번호로 결과 고정
    
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    weights = [counts.get(i, 1) for i in range(1, 46)]
    
    sets = []
    # 3 HOT
    for _ in range(3):
        while True:
            res = sorted(random.choices(range(1, 46), weights=weights, k=6))
            if len(set(res)) == 6:
                sets.append({"type": "🔥 HOT", "nums": res})
                break
    # 2 UNIQUE
    for _ in range(2):
        while True:
            res = sorted(random.sample(range(1, 46), 6))
            if sum(res) < 95 or sum(res) > 175:
                sets.append({"type": "💎 UNIQUE", "nums": res})
                break
    return sets

# --- [4. 메인 화면] ---
st.title("🏆 Weekly Evolution Strategy")

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 이번 주 고정 조합 보기"):
        # 다음 주가 되면 target_no가 바뀌므로 자동으로 새로운 고정 번호 세트가 생성됨
        st.session_state.current_fixed = generate_fixed_strategy(target_no + 1, analysis_df)
        st.session_state.is_checked = False

with col2:
    if st.button("🔎 당첨 결과 확인"):
        if 'current_fixed' in st.session_state:
            st.session_state.is_checked = True

if 'current_fixed' in st.session_state:
    for idx, data in enumerate(st.session_state.current_fixed):
        s = data["nums"]
        sType = data["type"]
        ball_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
        
        res_html = ""
        if st.session_state.get('is_checked', False):
            matched = len(set(s) & set(win_nums))
            res_text = f"일치: {matched}개"
            res_color = "#FFFF00"
            if matched == 6: res_text, res_color = "🥇 1등!", "#FFD700"
            res_html = f'<div style="margin-top:12px; font-weight:bold; color:{res_color};">{res_text}</div>'
        
        tag_color = "#FF4500" if "HOT" in sType else "#0088ff"
        st.markdown(f'<div class="set-card"><div style="color:{tag_color}; font-size:11px; font-weight:bold; margin-bottom:8px;">{sType} {idx+1}</div>{ball_html}{res_html}</div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; opacity:0.6;'>최신 {target_no}회 당첨번호 (자동 업데이트)</p>", unsafe_allow_html=True)
win_html = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in win_nums])
st.markdown(f"<div style='text-align:center;'>{win_html} + <div class='lotto-ball' style='background-color:{get_ball_color(bonus_num)}'>{bonus_num}</div></div>", unsafe_allow_html=True)
