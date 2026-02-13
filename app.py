import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. Page Config
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

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

# Data Fetch Function (Multi-index & Translation Defense)
@st.cache_data(ttl=60)
def get_ironclad_data(ticker):
    try:
        # Get data with auto_adjust
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df.empty: return None
        
        # [CRITICAL] Flatten Multi-index columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Clean column names (Force lowercase to prevent translation matching)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Ensure 'close' exists
        if 'close' not in df.columns and 'adj close' in df.columns:
            df['close'] = df['adj close']
            
        return df.ffill().bfill().dropna()
    except:
        return None

def fetch_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            r = requests.get(f"https://finance.naver.com/item/main.naver?code={symbol}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            n = BeautifulSoup(r.text, 'html.parser').select_one(".wrap_company h2 a").text
            return n, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    return symbol, symbol

st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col1, _ = st.columns([4, 1])
with col1:
    h_list = list(st.session_state.name_map.keys())
    sel_name = st.selectbox("📋 나의 종목 수첩", options=h_list, index=None)
    new_sym = st.text_input("➕ 새 종목 추가", placeholder="예: 000660")

t_name = ""; t_ticker = ""
if new_sym:
    name, ticker = fetch_name(new_sym)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    t_name, t_ticker = name, ticker
elif sel_name:
    t_name, t_ticker = sel_name, st.session_state.name_map[sel_name]

if t_ticker:
    df = get_ironclad_data(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_ironclad_data(t_ticker.replace(".KS", ".KQ"))

    if df is not None and 'close' in df.columns:
        close = df['close']; high = df['high']; low = df['low']
        
        # Calculations: $RSI$, $MACD$
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        sig = macd.ewm(span=9).mean()
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        ma20 = close.rolling(20).mean()

        st.markdown(f"<p class='big-font'>{t_name} 분석 결과</p>", unsafe_allow_html=True)
        
        y_high = close.iloc[:-1].max(); curr_p = close.iloc[-1]
        if curr_p >= y_high * 0.97:
            st.markdown(f"<div class='info-box'>🚀 <strong>신고가 근처:</strong> 전고점 돌파 기세가 대단합니다!</div>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        st.write("---")
        if curr_p >= y_high * 0.97 and macd.iloc[-1] > macd.iloc[-2]:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 (수익 극대화) 📈</div>", unsafe_allow_html=True)
        elif rsi.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        st.write("### 📊 주가 흐름 (빨간선: 20일 중심선)")
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'MA20': ma20}).tail(100).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart((base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False))) + 
                         base.mark_line(color='#EF5350', strokeWidth=2).encode(y='MA20:Q')).properties(height=400), use_container_width=True)
    else:
        st.error("데이터 로딩 실패. 반드시 브라우저 상단의 '번역 기능'을 끄고 [영문 원본] 상태에서 실행해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA"}
    st.rerun()
