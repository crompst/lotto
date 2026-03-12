import streamlit as st
import pandas as pd
import random
import requests
from collections import Counter
from datetime import datetime

# --- 스타일 및 설정 ---
st.set_page_config(page_title="Lotto Auto Pro", layout="centered")
st.markdown("<style>.stApp { background-color: #000000 !important; } h1, h2, h3, p, span, div { color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# --- 데이터 가져오기 (속도 최적화) ---
@st.cache_data(ttl=3600) # 1시간 동안 결과 기억 (매번 API 호출 안 함)
def get_lotto_auto():
    first_date = datetime(2002, 12, 7)
    now = datetime.now()
    curr_no = (now - first_date).days // 7 + 1
    
    # 동행복권 API 시도
    try:
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={curr_no}"
        data = requests.get(url, timeout=3).json()
        if data.get("returnValue") == "success":
            return curr_no, [data[f"drwtNo{i}"] for i in range(1, 7)], data["bnusNo"]
    except:
        pass
    return curr_no - 1, [1, 2, 3, 4, 5, 6], 7 # 실패 시 안전 장치

# 데이터 준비
target_no, win_nums, bonus_no = get_lotto_auto()
df = pd.read_csv('lotto_data.csv')

# --- 메인 화면 ---
st.title("🏆 Weekly Analysis")
st.write(f"현재 분석 회차: {target_no}회")

if st.button("🚀 이번 주 번호 생성 (고정)"):
    random.seed(target_no) # 회차별 번호 고정
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    weights = [counts.get(i, 1) for i in range(1, 46)]
    
    res_sets = []
    for _ in range(5):
        res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        while len(set(res)) < 6: res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        res_sets.append(res)
    st.session_state.my_sets = res_sets

if 'my_sets' in st.session_state:
    for s in st.session_state.my_sets:
        st.write(f"⭐ {s}")

# 당첨 확인 버튼
if st.button("🔎 당첨 확인"):
    if 'my_sets' in st.session_state:
        for s in st.session_state.my_sets:
            match = len(set(s) & set(win_nums))
            st.write(f"{s} -> 일치: {match}개")
