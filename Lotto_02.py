import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from collections import Counter

# --- 설정 및 데이터 로드 ---
st.set_page_config(page_title="Lotto Analysis Pro", layout="wide")

# UI 커스텀 스타일 (배경 대비 강화 및 카드형 레이아웃)
st.markdown("""
    <style>
    /* 전체 배경을 연한 회색으로 설정하여 흰색 카드 부각 */
    .stApp { background-color: #eef2f6; }
    
    /* 카드 디자인 */
    .set-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #3366ff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 12px;
    }
    
    .set-title {
        font-weight: bold;
        color: #334455;
        margin-bottom: 8px;
        font-size: 14px;
    }

    .lotto-ball {
        display: inline-block;
        width: 42px; height: 42px;
        line-height: 42px;
        border-radius: 50%;
        text-align: center;
        margin: 3px;
        color: white;
        font-weight: 800;
        font-size: 16px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
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

# --- 상단: 대시보드 타이틀 ---
st.title("🎯 Lotto High-Frequency Analysis")
st.info("💡 분석 필터가 **'고빈도(Hot) 데이터 기반'**으로 고정되었습니다.")

# --- 메인: 5세트 번호 생성 ---
if st.button("🔥 고빈도 기반 행운의 5세트 생성"):
    # 고빈도 가중치 계산
    all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
    counts = Counter(all_nums)
    weights = [counts.get(i, 1) for i in range(1, 46)]
    
    st.session_state.sets = []
    for _ in range(5):
        # 가중치를 적용한 랜덤 추출 (중복 제거를 위해 샘플링 방식 사용)
        res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        # 만약 한 세트 내 중복이 생기면 재추출 (드문 경우)
        while len(set(res)) < 6:
            res = sorted(random.choices(range(1, 46), weights=weights, k=6))
        st.session_state.sets.append(res)

# 생성된 번호 출력 (5세트 카드 레이아웃)
if 'sets' in st.session_state:
    for idx, s in enumerate(st.session_state.sets):
        with st.container():
            html_balls = "".join([f'<div class="lotto-ball" style="background-color:{get_ball_color(n)}">{n}</div>' for n in s])
            st.markdown(f"""
            <div class="set-card">
                <div class="set-title">SET {idx+1}</div>
                {html_balls}
            </div>
            """, unsafe_allow_html=True)

st.divider()

# --- 중단: 시각화 섹션 (스케일 조정) ---
st.subheader("📊 역대 출현 빈도 상세 분석")

all_nums = df[['번호1', '번호2', '번호3', '번호4', '번호5', '번호6']].values.flatten()
count_df = pd.DataFrame(Counter(all_nums).items(), columns=['번호', '출현횟수']).sort_values('번호')
avg_count = count_df['출현횟수'].mean()

# 막대 그래프 시각화 (Y축 스케일 최적화)
fig_bar = px.bar(count_df, x='번호', y='출현횟수', 
                 color='출현횟수', 
                 color_continuous_scale='Reds', # 고빈도 강조를 위해 레드 스케일
                 text='출현횟수')

fig_bar.update_traces(textposition='outside', textfont_size=9, marker_line_color='rgb(8,48,107)', marker_line_width=1)
fig_bar.add_hline(y=avg_count, line_dash="dot", line_color="blue", annotation_text="평균 빈도")

# 스케일 조정: 차이를 더 극명하게 보기 위해 최소값 근처로 고정
min_y = count_df['출현횟수'].min() - 3
max_y = count_df['출현횟수'].max() + 7
fig_bar.update_yaxes(range=[min_y, max_y])

fig_bar.update_layout(
    xaxis=dict(dtick=1), 
    height=450, 
    margin=dict(t=30, b=20, l=10, r=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_bar, use_container_width=True)

# 하단 데이터 테이블
with st.expander("데이터 원본 확인"):
    st.dataframe(df.tail(15).sort_values('회차', ascending=False), use_container_width=True)
