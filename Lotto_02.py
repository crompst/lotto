import streamlit as st
import pandas as pd
import random
from collections import Counter

# --- 설정 및 고대비 스타일 ---
st.set_page_config(page_title="Lotto Admin Pro", layout="centered")

st.markdown("""
    <style>
    /* 1. 배경을 아주 어두운 색으로 고정 (글자 대비 강화) */
    .stApp { 
        background-color: #0b0e14 !important; 
    }
    
    /* 2. 모든 기본 텍스트를 흰색으로 강제 */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }

    /* 3. 사이드바 스타일 (배경색과 입력창 테두리 강조) */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #ecf2f8 !important;
        font-weight: bold;
    }

    /* 4. 입력창(Number Input) 배경 및 글자색 수정 */
    input {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 1px solid #58a6ff !important;
    }

    /* 5. 카드 및 공 디자인 */
    .set-card {
        background-color: #1c2128;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        text-align: center;
    }
    .lotto-ball {
        display: inline-block;
        width: 40px; height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        margin: 3px;
        color: white !important;
        font-weight: 800;
        font-size: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* 6. 버튼 스타일 */
    .stButton>button {
        background-color: #238636 !important; /*
