import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 화면 설정
st.set_page_config(page_title="이수 투자비책 v13", layout="wide")

# [핵심] 미장 종목 한글 변환 사전 (자주 보시는 것 위주로 계속 추가 가능)
US_KR_MAP = {
    "AAPL": "애플", "TSLA": "테슬라", "NVDA": "엔비디아", "IONQ": "아이온큐",
    "MSFT": "마이크로소프트", "GOOGL": "구글", "AMZN": "아마존", "META": "메타",
    "NFLX": "넷플릭스", "TSM": "TSMC", "AVGO": "브로드컴", "ASML": "ASML",
    "INTC": "인텔", "AMD": "AMD", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로"
}

# [메모리 설정] 
if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX", "에스피지": "058610.KQ"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F0F2F6; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 45px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

# 종목 이름을 찾아오는 똑똑한 함수
def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    
    # 1. 한국 주식 (숫자 6자리)
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            return name, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    
    # 2. 미국 주식 (영어 알파벳)
    else:
        # 사전에 있는지 먼저 확인 (애플, 테슬라 등)
        if symbol in US_KR_MAP:
            return US_KR_MAP[symbol], symbol
        
        # 사전에 없으면 야후 금융에서 가져오기
        try:
            ticker_obj = yf.Ticker(symbol)
            # 영어 이름을 가져오되, 너무 길면 앞부분만 사용
            eng_name = ticker_obj.info.get('shortName', symbol)
            # "Apple Inc." -> "Apple" 정도로 다듬기
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

st.title("📈 이수 할아버지의 '미장 한글화' 분석기")

# [1구역] 종목 검색 및 입력
col_input, col_btn = st.columns([4, 1])

with col_input:
    history_list = list(st.session_state.name_map.keys())
    selected_name = st.selectbox("📋 나의 종목 수첩", options=history_list, index=None, placeholder="종목을 선택하세요")
    new_symbol = st.text_input("➕ 새 종목 추가 (번호 또는 영어 티커)", value="", placeholder="예: 000660 또는 AAPL")

target_name = ""; target_ticker = ""

if new_symbol:
    name, ticker = fetch_stock_name(new_symbol)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.success(f"✅ '{name}' 종목을 수첩에 저장했습니다!")
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
        
        # 보조지표 계산 (LaTeX 공식 적용)
        # RSI: $RSI = 100 - \frac{100}{1 + RS}$
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 윌리엄 %R
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()) * -100
        
        # MACD: $MACD = EMA_{12} - EMA_{26}$
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

        st.markdown(f"<p class='big-font'>{target_name}: {close.iloc[-1]:,.2f}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("RSI (가격 강도)", f"{rsi.iloc[-1]:.1f}")
        c2.metric("윌리엄 %R (바닥 확인)", f"{w_r.iloc[-1]:.1f}")
        c3.metric("MACD 에너지", "상승 중" if macd.iloc[-1] > macd.iloc[-2] else "하락 중")

        st.write("---")
        is_cheap = rsi.iloc[-1] <= 35 or w_r.iloc[-1] <= -80
        if is_cheap:
            if macd.iloc[-1] > macd.iloc[-2]: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출!) 🚨</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (하강 중)</div>", unsafe_allow_html=True)
        elif rsi.iloc[-1] >= 70: st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;' class='status-box'>💰 익절 권장 (과열) 💰</div>", unsafe_allow_html=True)
        else: st.markdown("<div style='background-color:#F0F2F6; color:#31333F; border-color:#D1D5DB;' class='status-box'>🟡 관망 (보통 상태) 🟡</div>", unsafe_allow_html=True)

        st.write("### 📊 주가 흐름 (볼린저 밴드)")
        st.line_chart(pd.DataFrame({'주가': close, '상단': upper, '중심': ma20, '하단': lower}).tail(80))
        
        st.write("### 📉 MACD 추세 (막대 차트)")
        st.area_chart(macd - sig)
        st.line_chart(pd.DataFrame({'MACD선': macd, '시그널선': sig}).tail(80))
    else:
        st.error("데이터를 가져올 수 없습니다.")

if st.sidebar.button("🗑️ 수첩 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
    st.rerun()
