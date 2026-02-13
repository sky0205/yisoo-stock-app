import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. Page Config (번역 절대 금지)
st.set_page_config(page_title="Stock Analyzer for Isu Grandpa", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

# 2. UI 스타일 (Design)
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Fetching (번역 내성 강화)
@st.cache_data(ttl=60)
def get_bulletproof_data(ticker):
    try:
        # [수정] multi_level_index=False를 넣어 데이터 구조를 단순하게 만듭니다.
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        
        if df.empty:
            return None
            
        # [수정] 컬럼명을 강제로 영어로 다시 지정합니다 (번역기 방어)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # 'close' 컬럼이 없으면 가장 마지막 컬럼을 종가로 사용
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
        return df.ffill().bfill().dropna()
    except Exception as e:
        st.sidebar.error(f"내부 에러 발생: {e}")
        return None

def fetch_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            r = requests.get(f"https://finance.naver.com/item/main.naver?code={symbol}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    return symbol, symbol

# 4. 앱 시작 (Main UI)
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col_search, _ = st.columns([4, 1])
with col_search:
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

# 5. 분석 실행
if t_ticker:
    with st.spinner(f'{t_name}의 주가 정보를 가져오고 있습니다...'):
        df = get_bulletproof_data(t_ticker)
        # 한국 주식 재시도 (KOSPI -> KOSDAQ)
        if (df is None or df.empty) and ".KS" in t_ticker:
            df = get_bulletproof_data(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        try:
            close = df['close']; high = df['high']; low = df['low']
            
            # RSI 공식: $RSI = 100 - \frac{100}{1 + RS}$
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().replace(0, 0.001)
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            # MACD 공식: $MACD = EMA_{12} - EMA_{26}$
            macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
            sig = macd.ewm(span=9, adjust=False).mean()
            
            # 1년 최고가 및 현재 위치
            y_high = close.max(); curr_p = close.iloc[-1]
            is_high = curr_p >= y_high * 0.97

            st.markdown(f"<p class='big-font'>{t_name} 분석 결과</p>", unsafe_allow_html=True)
            
            if is_high:
                st.markdown(f"<div class='info-box'>🚀 <strong>신고가 근처:</strong> 전고점 돌파 기세가 강합니다!</div>", unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
            m2.metric("과열도(RSI)", f"{rsi.iloc[-1]:.1f}")
            m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

            # 신호등 로직
            st.write("---")
            if rsi.iloc[-1] <= 35:
                st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
            elif is_high:
                st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 (보유) 📈</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

            # 차트
            st.write("### 📊 최근 100일 주가 흐름")
            st.line_chart(close.tail(100))
            
            st.write("### 📉 MACD 추세")
            st.line_chart(pd.DataFrame({'MACD': macd, 'Signal': sig}).tail(100))
            
        except Exception as e:
            st.error(f"지표 계산 중 에러 발생: {e}. '영어 원본' 상태에서 실행 중인지 확인해 주세요.")
    else:
        st.error(f"'{t_ticker}' 데이터를 불러오지 못했습니다. 인터넷 연결이나 브라우저 번역 설정을 확인해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA"}
    st.rerun()
