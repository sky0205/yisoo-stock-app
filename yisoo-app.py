import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 (에러 방지 및 시인성 극대화) ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

# 미리 등록된 종목 (타겟가 보관용)
stock_db = {
    "005930": {"target": 210000.0},
    "000100": {"target": 135000.0},
    "NVDA": {"target": 195.00},
    "IONQ": {"target": 39.23},
    "AAPL": {"target": 250.00},
}

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-content { font-size: 48px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 30px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #000000 !important; }
    .summary-box b { color: #000000 !important; font-weight: 800; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 데이터 엔진 (이름 자동 검색 기능 포함) ---
@st.cache_data(ttl=3600)
def get_auto_name(code, market):
    try:
        if "KR" in market:
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            # 네이버 금융에서 종목명 추출
            return soup.select_one(".wrap_company h2 a").text
        else:
            ticker = yf.Ticker(code)
            return ticker.info.get('shortName', "미상 종목")
    except: return "새로운 종목"

def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        p = soup.select_one(".no_today .blind").text.replace(",", "")
        return int(p)
    except: return None

@st.cache_data(ttl=60)
def get_tech_analysis(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty: return None
        close = df['Close']
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g/l)))
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean(); macd = (e12 - e26) - (e12 - e26).ewm(span=9).mean()
        return {"p": float(close.iloc[-1]), "up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), 
                "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float(macd.iloc[-1])}
    except: return None

# --- [2] 실시간 지능형 설정창 ---
st.title("🏆 이수할아버지 v36000 마스터")

# 1단계: 코드 입력
t_code = st.text_input("🔢 종목 코드(6자리) 또는 미장 티커(영문) 입력", value="005930")
in_market = st.selectbox("🌎 시장 선택 (먼저 선택해 주세요)", ["국장 (KR)", "미장 (US)"])

# 2단계: 종목명 자동 검색 로직
auto_name = get_auto_name(t_code, in_market)
db_target = stock_db.get(t_code, {"target": 0.0})["target"]

# 3단계: 가로 배치 입력창
c1, c2 = st.columns([1, 1])
with c1: in_name = st.text_input("📍 종목명 (네이버 자동검색 결과)", value=auto_name)
with c2: in_target = st.number_input("💎 나의 적정주가", value=float(db_target), step=0.1)

# --- [3] 분석 실행부 (에러 방지 꼼꼼하게 처리) ---
if st.button("🚀 실시간 정밀 분석 시작"):
    st.markdown("---")
    y_ticker = t_code + (".KS" if "KR" in in_market else "")
    tech = get_tech_analysis(y_ticker)
    
    # 국장 코스닥 대응
    if "KR" in in_market and not tech:
        tech = get_tech_analysis(t_code + ".KQ")
    
    price = get_naver_price(t_code) if "KR" in in_market else (tech["p"] if tech else None)

    if price and tech:
        cur = "원" if "KR" in in_market else "$"
        f_p = f"{format(int(price), ',')} {cur}" if "KR" in in_market else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(in_target), ',')} {cur}" if "KR" in in_market else f"{cur}{in_target:,.2f}"
        
        # 1. 현재가 (최상단 강조)
        st.markdown(f"<p class='big-price'>🔍 {in_name} ({t_code}) 현재가: {f_p}</p>", unsafe_allow_html=True)

        # 2. 2단 지능형 신호등
        if tech['rsi'] > 70 or price > tech['up']:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < in_target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 설정된 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        # 3. 추세 요약 (시인성 보정)
        st.markdown("### 📝 추세 분석 요약")
        sum_msg = "에너지가 위로 폭발하여 밴드 상단을 넘보고 있습니다." if price > tech['up'] else "바닥에서 지지를 확인하며 반등을 준비 중입니다."
        st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {in_name}은(는) {sum_msg}<br>RSI {round(tech['rsi'],1)}는 {'과열 상태입니다' if tech['rsi']>70 else '바닥 구간입니다' if tech['rsi']<35 else '안정권'}입니다.</div>", unsafe_allow_html=True)

        # 4. 상세 지표 비교
        b_diag = "⚠️ 상단 돌파 (매도주의)" if price > tech['up'] else "✅ 하단 지입 (매수기회)" if price < tech['dn'] else "밴드 내 안정적 주행"
        f_up = f"{tech['up']:,.2f}" if "US" in in_market else f"{round(tech['up'],0):,.0f}"
        f_dn = f"{tech['dn']:,.2f}" if "US" in in_market else f"{round(tech['dn'],0):,.0f}"

        st.table(pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{f_up} / {f_dn}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "상세 진단 (현지수 비교)": [b_diag, "과열" if tech['rsi']>70 else "바닥" if tech['rsi']<30 else "보통", "단기천장" if tech['wr']>-20 else "단기바닥" if tech['wr']<-80 else "보통", "상승 동력 우세" if tech['macd']>0 else "하락 압력 우세"]
        }))
    else:
        st.error(f"❌ '{t_code}' 데이터를 가져올 수 없습니다. 시장(국장/미장) 선택과 코드가 일치하는지 확인해 주세요!")
