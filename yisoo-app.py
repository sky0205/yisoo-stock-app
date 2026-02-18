import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-content { font-size: 48px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 32px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #000000 !important; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] AI 데이터 및 S-RIM 엔진 ---
@st.cache_data(ttl=3600)
def get_stock_info(ticker_code, market):
    try:
        y_ticker = ticker_code + (".KS" if "KR" in market else "")
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # 이름 가져오기
        name = info.get('shortName', "새 종목")
        if "KR" in market:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_code}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            
        # S-RIM 계산용 수치
        bps = info.get('bookValue', 0)
        roe = info.get('returnOnEquity', 0)
        r = 0.09 # 요구수익률 9% 고정 (선생님과 합의된 수치)
        
        # S-RIM 공식: BPS + (BPS * (ROE - r) / r)
        if bps > 0 and roe > 0:
            srim_target = bps + (bps * (roe - r) / r)
        else:
            srim_target = 0.0
            
        return name, float(srim_target)
    except:
        return "데이터 오류", 0.0

def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return int(soup.select_one(".no_today .blind").text.replace(",", ""))
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

# --- [2] 메인 화면 ---
st.title("🏆 이수할아버지 v36000 AI 마스터")

# 1. 티커 입력 및 시장 선택
c1, c2 = st.columns([1, 1])
with c1: t_code = st.text_input("🔢 종목 코드 / 티커 입력", value="005930")
with c2: in_market = st.selectbox("🌎 시장 선택", ["국장 (KR)", "미장 (US)"])

# 2. AI 자동 계산 실행
auto_name, ai_target = get_stock_info(t_code, in_market)

# 3. 설정 확인 (AI가 채워줌)
c3, c4 = st.columns([1, 1])
with c3: in_name = st.text_input("📍 종목명 (AI 자동완성)", value=auto_name)
with c4: in_target = st.number_input("💎 AI 산출 적정주가 (수정가능)", value=ai_target, step=0.1)

# --- [3] 분석 결과 ---
if st.button("🚀 AI 정밀 분석 시작"):
    st.markdown("---")
    y_ticker = t_code + (".KS" if "KR" in in_market else "")
    tech = get_tech_analysis(y_ticker)
    if "KR" in in_market and not tech: tech = get_tech_analysis(t_code + ".KQ")
    price = get_naver_price(t_code) if "KR" in in_market else (tech["p"] if tech else None)

    if price and tech:
        cur = "원" if "KR" in in_market else "$"
        f_p = f"{format(int(price), ',')} {cur}" if "KR" in in_market else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(in_target), ',')} {cur}" if "KR" in in_market else f"{cur}{in_target:,.2f}"
        
        st.markdown(f"<p class='big-price'>🔍 {in_name} ({t_code}) 현재가: {f_p}</p>", unsafe_allow_html=True)

        if tech['rsi'] > 70 or price > tech['up']:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < in_target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 AI 기반 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        st.markdown("### 📝 AI 추세 분석 요약")
        sum_msg = "에너지가 밴드 상단을 넘보고 있습니다." if price > tech['up'] else "바닥 지지력을 테스트 중입니다."
        st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {in_name}은(는) {sum_msg}<br>RSI {round(tech['rsi'],1)}는 {'과열 상태' if tech['rsi']>70 else '바닥 구간' if tech['rsi']<35 else '안정권'}입니다.</div>", unsafe_allow_html=True)

        # 상세 지표 표
        idx_df = pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{tech['up']:,.2f} / {tech['dn']:,.2f}" if "US" in in_market else f"{round(tech['up'],0):,.0f} / {round(tech['dn'],0):,.0f}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "실시간 진단": ["상단 돌파(주의)" if price > tech['up'] else "하단 지입(기회)" if price < tech['dn'] else "안정 주행", "심리 과열" if tech['rsi']>70 else "심리 바닥" if tech['rsi']<30 else "보통", "단기천장" if tech['wr']>-20 else "단기바닥" if tech['wr']<-80 else "보통", "상승세" if tech['macd']>0 else "하락세"]
        })
        st.table(idx_df)
    else:
        st.error("데이터 로딩 실패! 코드와 시장 선택을 확인해 주세요.")
