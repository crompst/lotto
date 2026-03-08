import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
from collections import Counter
import plotly.express as px  # 시각화를 위해 추가

# --- 1. 데이터 수집 함수 (최신 회차 자동 업데이트) ---
@st.cache_data
def load_lotto_data(limit=100):
    # 실제로는 이전에 짠 크롤링 코드를 활용해 CSV를 읽거나 
    # 여기서는 데모를 위해 최근 데이터를 가져오는 로직을 시뮬레이션합니다.
    # 실 서비스 시에는 위에서 만든 크롤링 데이터를 lotto_data.csv로 저장해두고 활용하세요.
    try:
        df = pd.read_csv('lotto_data.csv')
    except:
        st.error("데이터 파일(lotto_data.csv)이 없습니다. 먼저 크롤링을 수행해 주세요!")
        return pd.DataFrame()
    return df

# --- 2. 알고리즘 정의 ---
def gen_weighted(df):
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    numbers = list(range(1, 46))
    weights = [counts.get(i, 1) for i in numbers]
    return sorted(random.choices(numbers, weights=weights, k=6))

def gen_cold(df):
    recent_nums = set(df.tail(10)[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten())
    cold_nums = [i for i in range(1, 46) if i not in recent_nums]
    return sorted(random.sample(cold_nums, 6))

def gen_balanced():
    while True:
        nums = sorted(random.sample(range(1, 46), 6))
        if 100 <= sum(nums) <= 175: # 총합 필터
            return nums

# --- 3. Streamlit UI 구성 ---
st.set_page_config(page_title="나만의 로또 분석기", layout="wide")
st.title("🎯 로또 번호 통계 분석 & 생성기")

df = load_lotto_data()

if not df.empty:
    # 사이드바: 알고리즘 선택
    st.sidebar.header("설정")
    method = st.sidebar.selectbox("알고리즘 선택", ["가중치 기반 (Hot)", "최근 미출현 (Cold)", "균형 잡힌 패턴 (Balanced)"])
    
    # 메인 화면 - 번호 생성 섹션
    st.subheader(f"🔮 {method} 알고리즘 결과")
    if st.button("번호 생성하기"):
        if method == "가중치 기반 (Hot)":
            res = gen_weighted(df)
        elif method == "최근 미출현 (Cold)":
            res = gen_cold(df)
        else:
            res = gen_balanced()
            
        cols = st.columns(6)
        for i, n in enumerate(res):
            cols[i].markdown(f"<h2 style='text-align: center; background-color: #f0f2f6; border-radius: 10px; padding: 10px;'>{n}</h2>", unsafe_allow_html=True)
        st.balloons()

    st.divider()

    # 시각화 섹션
    st.subheader("📊 데이터 시각화 분석")
    tab1, tab2 = st.tabs(["번호별 빈도", "최근 당첨 번호"])

    with tab1:
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        count_df = pd.DataFrame(Counter(all_nums).items(), columns=['Number', 'Count']).sort_values('Number')
        fig = px.bar(count_df, x='Number', y='Count', title="번호별 누적 당첨 횟수", color='Count')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(df.tail(10).sort_values('회차', ascending=False), use_container_width=True)

else:
    st.warning("데이터를 불러올 수 없습니다.")