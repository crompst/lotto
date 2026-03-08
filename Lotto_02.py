import streamlit as st
import pandas as pd
import random
import requests
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto Auto-Sync Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, div { color: #ffffff !important; }
    .set-card {
        background-color: #1f2937; padding: 20px; border-radius: 15px; 
        border: 1px solid #3b82f6; margin-bottom: 20px; text-align: center;
    }
    .lotto-ball {
        display: inline-block; width: 42px; height: 42px; line-height: 42px;
        border-radius: 50%; text-align: center; margin: 3px;
        color: white; font-weight: 800; font-size: 16px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border-radius: 12px; height: 3.5em; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [핵심: 실시간 최신번호 크롤링 함수] ---
@st.cache_data(ttl=3600) # 1시간마다 새로 확인
def sync_latest_lotto(current_df):
    latest_no_in_file = int(current_df.iloc[-1]['회차'])
    next_no = latest_no_in_file + 1
    
    # 다음 회차 데이터 가져오기 시도 (API 방식)
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={next_no}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        
        if data.get('returnValue') == 'success':
            new_row = {
                '회차': next_no,
                '번호1': data['drwtNo1'], '번호2': data['drwtNo2'], '번호3': data['drwtNo3'],
                '번호4': data['drwtNo4'], '번호5': data['drwtNo5'], '번호6': data['drwtNo6'],
                '보너스': data['bnusNo']
            }
            # 파일 데이터와 합치기
            updated_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
            return updated_df, True
    except:
        pass
    return current_df, False

# 데이터 로드 및 동기화
df_base = pd.read_csv('lotto_data.csv')
df, is_updated = sync_latest_lotto(df_base)
latest_draw = df.iloc[-1]

# --- UI 및 당첨 확인 ---
st.title("🔄 Lotto Auto-Sync")
if is_updated:
    st.success(f"✨ 최신 {int(latest_draw['회차'])}회차 데이터를 자동으로 불러왔습니다!")
else:
    st.info(f"현재 데이터 기준: 제 {int(latest_draw['회차'])}회차")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 확률 최적화 5세트 생성"):
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
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

with col2:
    if st.button("🔎 당첨 결과 즉시 확인"):
        if 'current_sets' in st.session_state:
            st.session_state.is_checked = True

st.divider()

# 결과 출력 섹션 (이전 코드와 동일)
if 'current_sets' in st.session_state:
    win_nums = [latest_draw[f'번호{i}'] for i in range(1, 7)]
    bonus_num = latest_draw['보너스']
    
    for idx, s in enumerate(st.session_state.current_sets):
        html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(int(n))}">{int(n)}</div>' for n in s])
        res_area = ""
        if st.session_state.get('is_checked', False):
            # 당첨 확인 로직 적용 (생략된 함수 호출)
            matched = len(set(s) & set(win_nums))
            res_text = f"일치: {matched}개"
            if matched == 6: res_text = "🥇 1등!"
            elif matched == 5 and bonus_num in s: res_text = "🥈 2등!"
            res_area = f'<div style="margin-top:10px; font-weight:bold; color:#60a5fa;">{res_text}</div>'
            
        st.markdown(f'<div class="set-card">SET {idx+1}<br>{html_balls}{res_area}</div>', unsafe_allow_html=True)
