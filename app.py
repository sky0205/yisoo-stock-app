import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. Page Config (Must be in English)
st.set_page_config(page_title="Isu Grandpa Analyzer", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# Data Fetching (Defense against translation and Multi-index)
@st.cache_data(ttl=60)
def get_stock_data_final(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        
        # Force column names to lowercase and strip spaces (Crucial for defense)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # Ensure we have a column to work with
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
        return df.ffill().bfill().dropna()
    except: return None

# UI Start
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col1, _ = st.columns([4, 1])
with col1:
    h_list = list(st.session_state.name_map.keys())
    sel_name = st.selectbox("📋 나의 종목 수첩", options=h_list, index=None)
    new_sym = st.text_input("➕ 새 종목 추가", placeholder="예: 000660")

t_name = ""; t_ticker = ""
if new_sym:
    # Get name from Naver
    s = new_sym.upper().strip()
    if s.isdigit() and len(s) == 6:
        try:
            r = requests.get(f"https://finance.naver.com/item/main.naver?code={s}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            n = BeautifulSoup(r.text, 'html.parser').select_one(".wrap_company h2 a").text
            t_name, t_ticker = n, s + ".KS"
        except: t_name, t_ticker = s, s + ".KS"
    else: t_name, t_ticker = s, s
    
    if t_name not in st.session_state.name_map:
        st.session_state.name_map[t_name] = t_ticker
        st.rerun()
elif sel_name:
    t_name, t_ticker = sel_name, st.session_state.name_map[sel_name]

if t_ticker:
    df = get_stock_data_final(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_stock_data_final(t_ticker.replace(".KS", ".KQ"))

    if df is not None and 'close' in df.columns:
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        
        # Indicators
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        sig = macd.ewm(span=9).mean()
        y_high = close.max(); curr_p = close.iloc[-1]

        st.markdown(f"<p class='big-font'>{t_name} 분석 결과</p>", unsafe_allow_html=True)
        
        if curr_p >= y_high * 0.97:
            st.markdown(f"<div class='info-box'>🚀 <strong>신고가 근처:</strong> 현재 돌파 기세가 아주 강합니다!</div>", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi.iloc[-1]:.1f}")
        m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        st.write("---")
        if rsi.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97 and macd.iloc[-1] > macd.iloc[-2]:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 (보유) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        st.write("### 📊 최근 주가 흐름")
        st.line_chart(close.tail(100))
    else:
        st.error("데이터 로딩 실패. 반드시 브라우저 상단의 '번역 기능'을 끄고 [영문 원본] 상태에서 실행해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA"}
    st.rerun()
