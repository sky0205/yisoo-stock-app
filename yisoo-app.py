import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 검색 기록 저장소 ---
st.set_page_config(page_title="v36000 글로벌 실시간 분석기", layout="wide")

if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- [1] 종목 데이터베이스 (티커 및 적정주가 설정) ---
# 국장 종목은 네이버용 코드로, 미장은 야후 티커로 관리합니다.
stock_info = {
    "아이온큐 (IONQ)": {"ticker": "IONQ", "market": "US", "target": 39.23},
    "엔비디아 (NVDA)": {"ticker": "NVDA", "market": "US", "target": 170.00},
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 68000},
    "유한양행": {"ticker": "000100", "market": "KR", "target": 162000},
    "대한항공": {"ticker": "003490", "market": "KR", "target": 28500},
    "실리콘투": {"ticker": "257720", "market": "KR", "target": 49450},
    "넷플릭스 (NFLX)": {"ticker": "NFLX", "market": "US", "target": 850.00},
}

# --- [2] 데이터 수집 및 지수 계산 엔진 ---
def get_naver_price(code):
    """네이버 금융에서 국장 실시간 주가 크롤링"""
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        price = soup.select_one(".no_today .blind").text.replace(",", "")
        return int(price)
    except: return None

@st.cache_data(ttl=60)
def get_full_analysis(ticker):
    """야후 파이낸스 데이터를 통한 4대 기술지표(Bollinger, RSI, WR, MACD) 계산"""
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty: return None
        
        close = df['Close']
        # 1. 볼린저 밴드 (20일)
        ma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        upper, lower = ma20 + (std20 * 2), ma20 - (std20 * 2)
        
        # 2. RSI (14일)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 3. Williams %R (14일)
        high14 = df['High'].rolling(window=14).max()
        low14 = df['Low'].rolling(window=14).min()
        w_r = (high14 - close) / (high14 - low14) * -100
        
        # 4. MACD (12, 26, 9)
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_osc = macd_line - signal_line
        
        return {
            "price": round(float(close.iloc[-1]), 2),
            "upper": round(float(upper.iloc[-1]), 2), "lower": round(float(lower.iloc[-1]), 2),
            "rsi": round(float(rsi.iloc[-1]), 2), "wr": round(float(w_r.iloc[-1]), 2),
            "macd": round(float(macd_osc.iloc[-1]), 4)
        }
    except: return None

# --- [3] 메인 화면 구성 ---
st.title("🏆 이수할아버지 v36000 글로벌 실시간 분석기")

# 종목 선택 창
search_stock = st.selectbox("분석할 종목을 선택하세요", list(stock_info.keys()))
info = stock_info[search_stock]

if st.button("🚀 실시간 정밀 분석 시작"):
    if search_stock not in st.session_state['history']:
        st.session_state['history'].insert(0, search_stock)

# 데이터 실시간 로딩
y_ticker = info["ticker"] + (".KS" if info["market"] == "KR" and len(info["ticker"]) == 6 else ".KQ" if len(info["ticker"]) == 6 else "")
tech = get_full_analysis(y_ticker)
price = get_naver_price(info["ticker"]) if info["market"] == "KR" else (tech["price"] if tech else None)

if price and tech:
    st.markdown("---")
    
    # 1. 종목명 및 현주가 표시
    unit = "원" if info["market"] == "KR" else "$"
    fmt_p = f"{format(int(price), ',')} 원" if info["market"] == "KR" else f"${price}"
    st.header(f"🔍 종목명: {search_stock} ({info['ticker']})")
    st.markdown(f"# **현주가: {fmt_p}**")

    # 2. 신호등 표시 (특대형)
    if price < info["target"] * 0.9:
        st.error(f"# 🚦 신호등: 🔴 매수 사정권 (적기)")
    elif price > info["target"]:
        st.success(f"# 🚦 신호등: 🟢 매도 검토 (수익실현)")
    else:
        st.warning(f"# 🚦 신호등: 🟡 관망 (대기)")

    # 3. 적정주가 표시 (특대형)
    fmt_t = f"{format(int(info['target']), ',')} 원" if info["market"] == "KR" else f"${info['target']}"
    st.info(f"## 💎 테이버 적정주가: {fmt_t}")

    # 4. 추세 분석 요약
    st.markdown("### 📝 추세 분석 요약")
    sum_text = "상승 에너지가 포착되었습니다." if tech['macd'] > 0 else "현재 조정을 받으며 에너지를 모으는 중입니다."
    st.success(f"**이수할아버지 의견:** {sum_text} 자전거 타이어에 바람을 채우듯 천천히 대응하세요.")

    # 5. 추세 분석표 (Trend)
    st.markdown("### 📈 추세 분석표 (Trend)")
    st.table(pd.DataFrame({
        "분석 항목": ["가격 위치", "에너지 방향", "투자 심리"],
        "현재 상태": [
            "밴드 하단선 지지 중" if price < tech['lower'] * 1.05 else "밴드 상단 저항 돌파 중",
            "상승 동력 발생" if tech['macd'] > 0 else "하락 압력 우세",
            "공포 구간 (저점 매수 유효)" if tech['rsi'] < 40 else "탐욕 구간 (추격 매수 주의)"
        ]
    }))

    # 6. 지수 분석표 (4대 지수 정밀 표시)
    st.markdown("### 📊 상세 지수 분석표 (Index)")
    st.table(pd.DataFrame({
        "핵심 지표": ["Bollinger Band (상/하)", "RSI (심리지수)", "Williams %R", "MACD Osc"],
        "실시간 수치": [
            f"{tech['upper']} / {tech['lower']}",
            f"{tech['rsi']} (●)",
            f"{tech['wr']} (▲)",
            f"{tech['macd']} (■)"
        ],
        "해석 가이드": [
            "밴드 이격도를 통한 가격 통로 확인",
            "30이하(바닥), 70이상(과열)",
            "-80이하(강력바닥), -20이상(고점)",
            "0보다 크면 매수세(페달링의 힘) 우위"
        ]
    }))

else:
    st.error("실시간 데이터를 불러오는 중입니다. 잠시만 기다려 주세요!")

# 7. 오늘 검색한 종목 (History)
st.markdown("---")
st.subheader("🕒 오늘 검색한 종목 (History)")
if st.session_state['history']:
    st.write(", ".join(st.session_state['history']))
