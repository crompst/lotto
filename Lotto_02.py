import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto Insight", layout="wide")

# 아이패드 가독성을 위한 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .lotto-ball {
        display: inline-block;
        width: 50px; height: 50px;
        line-height: 50px;
        border-radius: 50%;
        text-align: center;
        margin: 5px;
        color: white;
        font-weight: bold;
        font-size: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('lotto_data.csv')
    return df

# 번호별 색상 지정 함수 (공식 로또 색상)
def get_ball_color(n):
    if 1 <= n <= 10: return "#fbc400" # 노랑
    if 11 <= n <= 20: return "#69c8f2" # 파랑
    if 21 <= n <= 30: return "#ff7272" # 빨강
    if 31 <= n <= 40: return "#aaa"    # 회색
    return "#b0d840"                   # 초록

df = load_data()

# --- 사이드바 영역 ---
st.sidebar.title("🧬 분석 설정")
method = st.sidebar.radio("번호 추출 전략", ["가중치 기반 (Hot)", "최근 미출현 (Cold)", "완전 균형 (Balanced)"])
st.sidebar.divider()
st.sidebar.info("데이터 기준: 1회 ~ 최근 업데이트 회차")

# --- 메인 영역: 번호 생성 ---
st.title("🎯 Lotto Insight Dashboard")

# 번호 생성 로직
def generate_nums():
    if method == "가중치 기반 (Hot)":
        all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
        counts = Counter(all_nums)
        return sorted(random.choices(range(1, 46), weights=[counts.get(i, 1) for i in range(1, 46)], k=6))
    elif method == "최근 미출현 (Cold)":
        recent = set(df.tail(10)[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten())
        return sorted(random.sample([i for i in range(1, 46) if i not in recent], 6))
    else:
        while True:
            nums = sorted(random.sample(range(1, 46), 6))
            if 100 <= sum(nums) <= 175: return nums

# 번호 출력 섹션
col1, col2 = st.columns([1, 3])
with col1:
    st.write("") # 간격 조절
    if st.button("새로운 번호 분석 실행"):
        st.session_state.current_nums = generate_nums()

if 'current_nums' in st.session_state:
    with col2:
        html_balls = ""
        for n in st.session_state.current_nums:
            color = get_ball_color(n)
            html_balls += f'<div class="lotto-ball" style="background-color:{color}">{n}</div>'
        st.markdown(html_balls, unsafe_allow_html=True)

st.divider()

# --- 데이터 시각화 섹션 ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 번호별 출현 빈도")
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    count_df = pd.DataFrame(Counter(all_nums).items(), columns=['번호', '횟수']).sort_values('번호')
    
    # Plotly 막대 그래프 (터치 인터렉션 지원)
    fig1 = px.bar(count_df, x='번호', y='횟수', color='횟수', color_continuous_scale='Viridis')
    fig1.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("📉 당첨번호 합계 추이")
    df['합계'] = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].sum(axis=1)
    
    # 선 그래프로 흐름 시각화
    fig2 = px.line(df.tail(30), x='회차', y='합계', markers=True)
    fig2.add_hline(y=138, line_dash="dash", line_color="red", annotation_text="평균 합계(138)")
    fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- 하단 데이터 요약 ---
with st.expander("📄 최근 당첨 데이터 상세보기"):
    st.dataframe(df.tail(20).sort_values('회차', ascending=False), use_container_width=True)
