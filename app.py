import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 및 간판 고정
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

# 미장 한글 사전
US_KR_MAP = {
    "AAPL": "애플", "TSLA": "테슬라", "NVDA": "엔비디아", "IONQ": "아이온큐",
    "MSFT": "마이크로소프트", "GOOGL": "구글", "AMZN": "아마존", "META": "메타",
    "NFLX": "넷플릭스", "TSM": "TSMC", "PLTR": "팔란티어"
}

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:45px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            return name, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    else:
        if symbol in US_KR_MAP: return US_KR_MAP[symbol], symbol
        try:
            t = yf.Ticker(symbol)
            name = t.info.get('shortName', symbol)
            return name.split(' ')[0].split(',')[0], symbol
        except: return symbol, symbol

@st.cache_data(ttl=60)
def get_safe_data(ticker):
    try:
        # [핵심 수리] 데이터를 가져올 때 '그룹화'를 끄고 가져옵니다.
        data = yf.download(ticker, period="1y", interval="1d", group_by='column', auto_adjust=True)
        if data.empty: return None
        
        # [핵심 수리] 만약 데이터 층이 2층(MultiIndex)이면 1층으로 강제 통합합니다.
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        # 컬럼명을 소문자로 통일 (Close -> close)
        data.columns = [str(c).lower() for c in data.columns]
        return data.dropna()
    except:
        return None

st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col1, _ = st.columns([4, 1])
with col1:
    history_list = list(st.session_state.name_map.keys())
    selected_name = st.selectbox("📋 나의 종목 수첩", options=history_list, index=None, placeholder="종목을 선택하세요")
    new_symbol = st.text_input("➕ 새 종목 추가", placeholder="예: 000660")

target_name = ""; target_ticker = ""
if new_symbol:
    name, ticker = fetch_stock_name(new_symbol)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    target_name = name; target_ticker = ticker
elif selected_name:
    target_name = selected_name; target_ticker = st.session_state.name_map[selected_name]

if target_ticker:
    df = get_safe_data(target_ticker)
    
    # 한국 주식 재시도
    if (df is None or df.empty) and ".KS" in target_ticker:
        df = get_safe_data(target_ticker.replace(".KS", ".KQ"))

    if df is not None and 'close' in df.columns:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산 (분모 0 방지)
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

        # 신고가 분석
        year_high = close.iloc[:-1].max()
        curr_p = close.iloc[-1]
        is_high = curr_p >= (year_high * 0.97)

        st.markdown(f"<p class='big-font'>{target_name} 분석 결과</p>", unsafe_allow_html=True)
        
        if is_high:
            st.markdown(f"<div class='info-box'>🚀 <strong>신고가 영역:</strong> 대장주의 기세가 살아있습니다!</div>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".KS" in target_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI", f"{rsi.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("전고점", f"{year_high:,.0f}" if ".KS" in target_ticker else f"{year_high:,.2f}")

        # 신호등
        st.write("---")
        if is_high and macd.iloc[-1] > macd.iloc[-2]:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 📈</div>", unsafe_allow_html=True)
        elif rsi.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 구간 🟡</div>", unsafe_allow_html=True)

        # 차트 (박스 제거)
        st.write("### 📊 주가 흐름 (빨간선: 중심선)")
        c_df = pd.DataFrame({'Date': df.index, 'Price': close, 'MA20': ma20}).tail(80).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart(alt.layer(
            base.mark_line(color='#1E1E1E').encode(y=alt.Y('Price:Q', scale=alt.Scale(zero=False))),
            base.mark_line(color='#EF5350').encode(y='MA20:Q')
        ).properties(height=300), use_container_width=True)

        st.write("### 📉 MACD (파란선이 주황선 위에 있어야 함)")
        m_df = pd.DataFrame({'Date': df.index, 'MACD': macd, 'Signal': sig}).tail(80).reset_index()
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart(alt.layer(
            m_base.mark_line(color='#0059FF').encode(y=alt.Y('MACD:Q')),
            m_base.mark_line(color='#FF8000').encode(y='Signal:Q')
        ).properties(height=200), use_container_width=True)
    else:
        st.error("데이터 구조 분석에 실패했습니다. 코드를 다시 한 번 확인해 주세요.")
