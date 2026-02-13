import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정 (영문 유지 필수)
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 15px 0; border: 5px solid; }
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
            return soup.select_one(".wrap_company h2 a").text, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    return symbol, symbol

@st.cache_data(ttl=60)
def get_clean_data(ticker):
    try:
        # 최신 yfinance 구조 강제 정렬
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df.empty: return None
        
        # [핵심] 이중 이름표(Multi-index)를 일괄 제거하고 단일화
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).lower() for c in df.columns]
        
        # 데이터가 비어있으면 앞뒤 데이터로 채움
        return df.ffill().bfill().dropna()
    except: return None

# 앱 시작
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col1, _ = st.columns([4, 1])
with col1:
    h_list = list(st.session_state.name_map.keys())
    sel_name = st.selectbox("📋 나의 종목 수첩", options=h_list, index=None)
    new_sym = st.text_input("➕ 새 종목 추가", placeholder="예: 000660")

t_name = ""; t_ticker = ""
if new_sym:
    name, ticker = fetch_stock_name(new_sym)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    t_name, t_ticker = name, ticker
elif sel_name:
    t_name, t_ticker = sel_name, st.session_state.name_map[sel_name]

if t_ticker:
    df = get_clean_data(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_clean_data(t_ticker.replace(".KS", ".KQ"))

    if df is not None and 'close' in df.columns:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산 ($RSI$, $MACD$, $Bollinger$)
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        sig = macd.ewm(span=9).mean()
        
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

        # 결과 출력
        st.markdown(f"<p class='big-font'>{t_name} 분석 결과</p>", unsafe_allow_html=True)
        
        year_high = close.iloc[:-1].max(); curr_p = close.iloc[-1]
        if curr_p >= year_high * 0.97:
            st.markdown(f"<div class='info-box'>🚀 <strong>신고가 근처:</strong> 전고점을 돌파하려는 기세가 아주 강합니다!</div>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("1년 최고가", f"{year_high:,.2f}")

        # 신호등 로직
        st.write("---")
        if curr_p >= year_high * 0.97 and macd.iloc[-1] > macd.iloc[-2]:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 (수익 극대화) 📈</div>", unsafe_allow_html=True)
        elif rsi_val.iloc[-1] <= 35 or w_r.iloc[-1] <= -80:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 차트 수리 (Bollinger Band Area)
        st.write("### 📊 볼린저 밴드 및 주가 (빨간선: 중심선)")
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(100).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        
        # 밴드 영역
        area = base.mark_area(opacity=0.1, color='#B0BEC5').encode(y='Lower:Q', y2='Upper:Q')
        # 주가선
        line = base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        # 중심선
        ma_line = base.mark_line(color='#EF5350', strokeWidth=2).encode(y='MA20:Q')
        
        st.altair_chart((area + line + ma_line).properties(height=400), use_container_width=True)

        # MACD 차트
        st.write("### 📉 MACD 추세")
        m_df = pd.DataFrame({'Date': df.index, 'MACD': macd, 'Signal': sig}).tail(100).reset_index()
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        m_line = m_base.mark_line(color='#0059FF').encode(y='MACD:Q')
        s_line = m_base.mark_line(color='#FF8000').encode(y='Signal:Q')
        st.altair_chart((m_line + s_line).properties(height=200), use_container_width=True)
    else:
        st.error("데이터 로딩 실패. 종목 코드를 다시 확인하거나 번역 기능을 꺼주세요.")
