import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto Analysis Pro", layout="wide")

# UI 커스텀 스타일 (카드형 레이아웃 및 폰트 강조)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .lotto-ball {
        display: inline-block;
        width: 48px; height: 48px;
        line-height: 48px;
        border-radius: 50%;
        text-align: center;
        margin: 4px;
        color: white;
        font-weight: 800;
        font-size: 18px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('lotto_data.csv')

def get_ball_color(n):
    if 1 <= n <= 10: return "#fbc400" # 노랑
    if 11 <= n <= 20: return "#69c8f2" # 파랑
    if 21 <= n <= 30: return "#ff7272" # 빨강
    if 31 <= n <= 40: return "#aaa"    # 회색
    return "#b0d840"                   # 초록

df = load_data()

# --- 사이드바 ---
st.sidebar.header("⚙️ 분석 필터")
method = st.sidebar.select_slider("추출 전략 선택", options=["Hot", "Balanced", "Cold"])
st.sidebar.caption("Hot: 고빈도 위주 | Balanced: 평균합 기준 | Cold: 미출현 위주")

# --- 상단: 번호 생성 섹션 ---
st.title("📊 Lotto Insight Dashboard")

with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("✨ 새로운 행운 번호 생성"):
            if method == "Hot":
                all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
                counts = Counter(all_nums)
                st.session_state.res = sorted(random.choices(range(1, 46), weights=[counts.get(i, 1) for i in range(1, 46)], k=6))
            elif method == "Cold":
                recent = set(df.tail(15)[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten())
                st.session_state.res = sorted(random.sample([i for i in range(1, 46) if i not in recent], 6))
            else:
                while True:
                    nums = sorted(random.sample(range(1, 46), 6))
                    if 110 <= sum(nums) <= 165: 
                        st.session_state.res = nums
                        break
    
    with col2:
        if 'res' in st.session_state:
            html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in st.session_state.res])
            st.markdown(html_balls, unsafe_allow_html=True)

st.divider()

# --- 중단: 시각화 강화 섹션 ---
tab1, tab2 = st.tabs(["📈 출현 빈도 정밀 분석", "📉 흐름 분석"])

with tab1:
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    count_df = pd.DataFrame(Counter(all_nums).items(), columns=['번호', '출현횟수']).sort_values('번호')
    
    # 평균 출현 횟수 계산
    avg_count = count_df['출현횟수'].mean()

    # 1. 막대 그래프 최적화 (색상 스케일 및 폰트 조정)
    fig_bar = px.bar(count_df, x='번호', y='출현횟수', 
                     color='출현횟수', 
                     color_continuous_scale='Bluered', # 많이 나올수록 빨간색에 가깝게
                     text='출현횟수', # 막대 위에 숫자 표시
                     title='번호별 누적 당첨 빈도 (상세)')
    
    fig_bar.update_traces(textposition='outside', textfont_size=10)
    fig_bar.add_hline(y=avg_count, line_dash="dot", line_color="green", annotation_text="평균 빈도")
    
    # y축 범위 조절로 차이 극대화 (스케일 조정)
    min_y = count_df['출현횟수'].min() - 5
    max_y = count_df['출현횟수'].max() + 10
    fig_bar.update_yaxes(range=[min_y, max_y])
    
    fig_bar.update_layout(xaxis=dict(dtick=1), height=500, margin=dict(t=50, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        # 최근 50회차 합계 분포
        df['합계'] = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].sum(axis=1)
        fig_sum = px.histogram(df, x='합계', nbins=30, title="당첨번호 총합 분포 (정규성 확인)", color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_sum, use_container_width=True)
    
    with col_b:
        # 홀짝 비율 시각화 (최근 100회)
        recent_df = df.tail(100).copy()
        def get_odd_even(row):
            nums = [row['번호1'], row['번호2'], row['번호3'], row['번호4'], row['번호5'], row['번호6']]
            odds = len([n for n in nums if n % 2 != 0])
            return f"{odds}:{6-odds}"
        
        recent_df['홀짝비율'] = recent_df.apply(get_odd_even, axis=1)
        ratio_df = recent_df['홀짝비율'].value_counts().reset_index()
        fig_pie = px.pie(ratio_df, values='count', names='홀짝비율', title="최근 100회 홀:짝 비율", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- 하단: 데이터 요약 ---
st.expander("📄 데이터 원본 보기").dataframe(df.tail(30).sort_values('회차', ascending=False), use_container_width=True)
