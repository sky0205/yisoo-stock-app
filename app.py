import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
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
    </style>
    """, unsafe_allow_html=True)

# 데이터 가져오기 (가장 강력한 수리 로직)
@st.cache_data(ttl=60)
def get_ultimate_data(ticker):
    try:
        # 최신 yfinance 버전에 맞춰 데이터 구조를 강제로 단순화함
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        
        if df.empty:
            return None
            
        # [핵심 수리] 컬럼 이름에 '종가'나 'Close'가 포함된 것을 무조건 찾아냄
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # 'close'라는 이름이 없으면 첫 번째 컬럼을 종가로 강제 지정
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
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

t_name, t_ticker = "", ""
if new_sym:
    name, ticker = fetch_name(new_sym)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    t_name, t_ticker = name, ticker
elif sel_name:
    t_name, t_ticker = sel_name, st.session_state.name_map[sel_name]

if t_ticker:
    with st.spinner(f'{t_name} 분석 중...'):
        df = get_ultimate_data(t_ticker)
        # 국장 재시도
        if (df is None or df.empty) and ".KS" in t_ticker:
            df = get_ultimate_data(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']
        rsi = 100 - (100 / (1 + (close.diff().where(close.diff()>0,0).rolling(14).mean() / -close.diff().where(close.diff()<0,0).rolling(14).mean().replace(0,0.001))))
        y_high = close.max(); curr_p = close.iloc[-1]

        st.markdown(f"<p class='big-font'>{t_name} 분석 결과</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        c2.metric("RSI (과열도)", f"{rsi.iloc[-1]:.1f}")
        c3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 신호등
        st.write("---")
        if rsi.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        st.write("### 📊 최근 주가 흐름")
        st.line_chart(close.tail(100))
    else:
        st.error("데이터를 가져오는 데 실패했습니다. 종목 번호를 확인하거나 잠시 후 다시 시도해 주세요.")

if st.sidebar.button("🗑️ 수첩 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA"}
    st.rerun()
