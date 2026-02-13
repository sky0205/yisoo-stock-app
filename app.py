import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 화면 및 간판(제목) 고정 설정
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

# 미장 한글 이름 사전
US_KR_MAP = {
    "AAPL": "애플", "TSLA": "테슬라", "NVDA": "엔비디아", "IONQ": "아이온큐",
    "MSFT": "마이크로소프트", "GOOGL": "구글", "AMZN": "아마존", "META": "메타",
    "NFLX": "넷플릭스", "TSM": "TSMC", "AVGO": "브로드컴", "ASML": "ASML",
    "INTC": "인텔", "AMD": "AMD", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로"
}

# 메모리 설정 (종목 수첩)
if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F0F2F6; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .big-font { font-size:45px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 45px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

# 종목 이름 찾아오기 함수
def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            return name, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    else:
        if symbol in US_KR_MAP: return US_KR_MAP[symbol], symbol
        try:
            ticker_obj = yf.Ticker(symbol)
            eng_name = ticker_obj.info.get('shortName', symbol)
            clean_name = eng_name.split(' ')[0].split(',')[0]
            return clean_name, symbol
        except: return symbol, symbol

@st.cache_data(ttl=60)
def get_analysis_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

# ---------------------------------------------------------
# 앱 화면 시작
# ---------------------------------------------------------
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

# [1구역] 검색 및 입력
col_input, col_btn = st.columns([4, 1])

with col_input:
    history_list = list(st.session_state.name_map.keys())
    selected_name = st.selectbox("📋 나의 종목 수첩", options=history_list, index=None, placeholder="보관된 종목을 선택하세요")
    new_symbol = st.text_input("➕ 새 종목 추가 (번호 또는 영어 티커)", value="", placeholder="예: 000660 또는 TSLA")

target_name = ""; target_ticker = ""

if new_symbol:
    name, ticker = fetch_stock_name(new_symbol)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.success(f"✅ '{name}' 종목이 수첩에 등록되었습니다!")
        st.rerun()
    target_name = name; target_ticker = ticker
elif selected_name:
    target_name = selected_name; target_ticker = st.session_state.name_map[selected_name]

# [2구역] 분석 결과
if target_ticker:
    df = get_analysis_data(target_ticker)
    if df is None and ".KS" in target_ticker:
        target_ticker = target_ticker.replace(".KS", ".KQ")
        df = get_analysis_data(target_ticker)

    if df is not None:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()) * -100
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

        # 결과 출력
        st.markdown(f"<p class='big-font'>{target_name} 지표 분석</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("현재가", f"{close.iloc[-1]:,.2f}")
        c2.metric("RSI (강도)", f"{rsi.iloc[-1]:.1f}")
        c3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")

        # 신호등 로직
        st.write("---")
        is_cheap = rsi.iloc[-1] <= 35 or w_r.iloc[-1] <= -80
        macd_up = macd.iloc[-1] > macd.iloc[-2]
        
        if is_cheap:
            if macd_up: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 지금입니다! 강력 매수 🚨</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (하락 중)</div>", unsafe_allow_html=True)
        elif rsi.iloc[-1] >= 70: st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;' class='status-box'>💰 익절 권장 구간 💰</div>", unsafe_allow_html=True)
        else: st.markdown("<div style='background-color:#F0F2F6; color:#31333F; border-color:#D1D5DB;' class='status-box'>🟡 관망 및 관찰 구간 🟡</div>", unsafe_allow_html=True)

        st.write("### 📊 볼린저 밴드 흐름")
        st.line_chart(pd.DataFrame({'주가': close, '상단': upper, '중심': ma20, '하단': lower}).tail(80))
        
        # [수정] MACD는 선 그래프만 깔끔하게 표시
        st.write("### 📉 MACD 추세선 (파란선이 주황선을 뚫고 올라와야 합니다)")
        st.line_chart(pd.DataFrame({'MACD선': macd, '시그널선': sig}).tail(80))
    else:
        st.error("데이터를 가져올 수 없습니다.")

# 초기화 버튼
if st.sidebar.button("🗑️ 수첩 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
    st.rerun()
