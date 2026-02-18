import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 ---
st.set_page_config(page_title="v36000 글로벌 실시간 분석기", layout="wide")
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- [1] 종목 데이터베이스 (네이버용 코드는 숫자만 사용) ---
stock_info = {
    "아이온큐 (IONQ)": {"ticker": "IONQ", "market": "US", "target": 39.23},
    "엔비디아 (NVDA)": {"ticker": "NVDA", "market": "US", "target": 170.00},
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 68000},
    "유한양행": {"ticker": "000100", "market": "KR", "target": 162000},
    "대한항공": {"ticker": "003490", "market": "KR", "target": 28500},
    "실리콘투": {"ticker": "257720", "market": "KR", "target": 49450},
}

# --- [2] 네이버 실시간 국장 주가 가져오기 (고속 엔진) ---
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        # 네이버 금융에서 현재가 추출
        price_tag = soup.select_one(".no_today .blind")
        return int(price_tag.text.replace(",", ""))
    except:
        return None

# --- [3] 야후 미장 실시간 주가 및 볼린저 밴드 가져오기 ---
@st.cache_data(ttl=60)
def get_us_data(ticker):
    try:
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        current_price = data['Close'].iloc[-1]
        ma20 = data['Close'].rolling(window=20).mean()
        std20 = data['Close'].rolling(window=20).std()
        return round(float(current_price), 2), {"upper": round(float((ma20 + std20 * 2).iloc[-1]), 2), "lower": round(float((ma20 - std20 * 2).iloc[-1]), 2)}
    except:
        return None, None

# --- [4] 화면 구성 및 검색 ---
st.title("🏆 이수할아버지 v36000 실시간 분석기 (Naver Engine)")

search_stock = st.selectbox("분석 종목 선택", list(stock_info.keys()))
info = stock_info[search_stock]

if st.button("정밀 분석 시작"):
    if search_stock not in st.session_state['history']:
        st.session_state['history'].insert(0, search_stock)

# 주가 데이터 호출 (국적에 맞게 분기)
if info["market"] == "KR":
    price = get_naver_price(info["ticker"])
    _, bands = get_us_data(info["ticker"] + ".KS" if "KQ" not in search_stock else info["ticker"] + ".KQ")
else:
    price, bands = get_us_data(info["ticker"])

# --- [5] 결과 표시 (선생님 요청 순서 준수) ---
if price:
    st.markdown("---")
    st.header(f"🔍 종목명: {search_stock}")
    
    # 단위 설정
    fmt_price = f"{format(int(price), ',')} 원" if info["market"] == "KR" else f"${price}"
    fmt_target = f"{format(int(info['target']), ',')} 원" if info["market"] == "KR" else f"${info['target']}"
    
    st.subheader(f"현주가: {fmt_price}")

    # 신호등 로직
    if price < info["target"] * 0.9:
        st.error("🚦 **신호등 상태: 🔴 매수 사정권 (적기)**")
    elif price > info["target"]:
        st.success("🚦 **신호등 상태: 🟢 매도 검토 (수익실현)**")
    else:
        st.warning("🚦 **신호등 상태: 🟡 관망 (대기)**")

    st.info(f"💎 **테이버 적정주가: {fmt_target}**")

    # 추세 분석표
    st.markdown("### 1. 📈 추세 분석표 (Trend Analysis)")
    st.table(pd.DataFrame({
        "분석 항목": ["가격 위치", "에너지 방향", "국적 및 환율 영향"],
        "현재 상태": [
            "밴드 하단 부근" if bands and price < bands['lower'] * 1.05 else "밴드 상단 부근",
            "에너지 응축 중",
            "1,440원대 고환율 주의" if info["market"] == "US" else "정치적 리스크(국장) 경계"
        ]
    }))

    # 지수 분석표
    st.markdown("### 2. 📊 지수 분석표 (Index Analysis)")
    if bands:
        st.table(pd.DataFrame({
            "핵심 지표": ["Bollinger Upper", "Bollinger Lower", "현재가"],
            "실시간 수치": [f"{bands['upper']}", f"{bands['lower']}", f"{price}"]
        }))
else:
    st.error("네이버/야후 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")

# 히스토리
st.markdown("---")
st.subheader("🕒 오늘 검색한 종목 (History)")
st.write(", ".join(st.session_state['history']))
