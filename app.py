import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 (선생님 맞춤형)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div.stButton > button { background-color: white !important; color: #1E3A8A !important; border: 2px solid #1E3A8A !important; font-weight: bold !important; width: 100%; border-radius: 8px; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 42px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👨‍💻 이수할아버지의 '부드러운' 분석기 v2300")

# 2. 종목 입력
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).
