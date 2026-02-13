import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. Page Config (번역 절대 금지)
st.set_page_config(page_title="Isu Grandpa Stock Analyzer v43", layout="wide")

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

# 2. Data Fetching (Defense against Multi-index & Translation)
@st.cache_data(ttl=60)
def get_clean_data_final(ticker):
    try:
        # Get data with auto_adjust
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df.empty: return None
        
        # [CRITICAL] 2층 이름표를 1층으로 강제 통합
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
            
        # 모든 컬럼명을 영어 소문자로 고정 (번역기 방어 핵심)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # 'close'라는 이름이 없으면 첫 번째 컬럼을 가격으로 사용
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

# 3. UI Start
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col1, _ = st.columns([4, 1])
with col1:
    h_list = list(st.session_state.name_map.keys())
    sel_name = st.selectbox("📋 종목 선택", options=h_list, index=0)
    t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_clean_data_final(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_clean_data_final(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty and 'close' in df.columns:
        close = df['close']
        
        # 지표 계산: RSI
        # $RSI = 100 - \frac{100}{1 + RS}$
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        y_high = close.max()
        curr_p = close.iloc[-1]

        # 4. 분석 보고서 출력
        st.markdown(f"<p class='big-font'>{sel_name} 분석 보고서</p>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 5. 신호등
        st.write("---")
        if rsi_val.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 6. 차트
        st.write("### 📊 최근 주가 흐름")
        st.line_chart(close.tail(100))
        
    else:
        st.error("데이터 이름표(Close 등)를 찾는 데 실패했습니다. 브라우저 번역 기능을 끄고 영문 원본 상태로 실행해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
