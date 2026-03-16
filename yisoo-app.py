import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (제목 강조 및 글로벌 통합형)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    /* 제목 글씨 크게 */
    .main-title { font-size: 50px !important; color: #0D47A1 !important; margin-bottom: 20px; text-align: center; border-bottom: 5px solid #1E88E5; padding-bottom: 10px; }
    /* 글로벌 전황 하나로 통합 */
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 25px; border-radius: 15px; border: 3px solid #455A64; margin-bottom: 25px; }
    .global-item { font-size: 24px !important; margin-bottom: 10px; }
    /* 나머지 스타일 유지 */
    .stock-header { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 60px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .diagnosis-box { border: 2px solid #D32F2F; padding: 20px; border-radius: 10px; background-color: #FFF8F1; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 3px solid #CFD8DC; text-align: center; margin-bottom: 20px; }
    .val-main { font-size: 42px !important; color: #D32F2F !important; display: block; }
    .ind-box { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 420px; margin-bottom: 15px; }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 12px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .ind-value { font-size: 60px !important; color: #B71C1C !important; text-align: center; display: block; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>👴 이수할아버지 냉정 진단기 v36056</div>", unsafe_allow_html=True)

# 2. 글로벌 전황 통합 보고 (하나의 박스로 구현)
def get_global_data(ticker):
    try:
        g_df = yf.download(ticker, period="2d", progress=False)
        curr = g_df['Close'].iloc[-1].item()
        prev = g_df['Close'].iloc[-2].item()
        pct = ((curr
