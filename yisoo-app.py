import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 기본 설정 및 스타일 ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")

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

# --- [1] 지능형 데이터 엔진 (시장 자동 감지 및 S-RIM) ---
@st.cache_data(ttl=3600)
def fetch_stock_data(user_input):
    # 1. 시장 자동 판별 (숫자 6자리면 국장, 아니면 미장)
    is_kr = bool(re.match(r'^\d{6}$', user_input))
    market_type = "KR" if is_kr else "US"
    y_ticker = user_input + (".KS" if is_kr else "")
    
    try:
        stock = yf.Ticker(y_ticker)
        # 국장의 경우 Yahoo 데이터가 부실할 수 있어 Naver에서 이름 교차 확인
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={user_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = stock.info.get('shortName', user_input)

        # S-RIM 데이터 추출 (다양한 키값 대응)
        info = stock.info
        bps = info.get('bookValue') or info.get('priceToBook', 0) * (info.get('currentPrice', 0) / info.get('priceToBook', 1)) if info.get('priceToBook') else 0
        roe = info.get('returnOnEquity', 0)
        
        # 데이터가 없을 경우 재무제표 직접 조회 (미장 전용 보강)
        if not roe or roe == 0:
            try:
                fin = stock.financials
                net_income = fin.loc['Net Income'].iloc[0]
                equity = stock.balance_sheet.loc['Stockholders Equity'].iloc[0]
                roe = net_income / equity
            except: roe = 0.10 # 데이터 부재 시 기본 10% 가정

        r = 0.09 # 요구수익률 9% 고정
        srim_val = 0.0
        if bps > 0:
            srim_val = bps + (bps * (roe - r) / r)
            
        return {"name": name, "market": market_type, "target": srim_val, "ticker": y_ticker}
    except:
        return None

def get_realtime_price(code, is_kr):
    if is_kr:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            return int(soup.select_one(".no_today .blind").text.replace(",", ""))
        except: return None
    else:
        try:
            return yf.Ticker(code).history(period="1d")['Close'].iloc[-1]
        except: return None

# --- [2] 메인 화면 ---
st.title("🏆 이수할아버지 v36000 AI 마스터")

# 한 줄 입력: 국장/미장 선택 없이 바로 입력
t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커를 입력하세요", value="005930", help="예: 005930, NVDA, IONQ")

# 자동 데이터 로딩
data = fetch_stock_data(t_input)

if data:
    c1, c2 = st.columns(2)
    with c1: st.write(f"📍 **분석 종목:** {data['name']} ({t_input})")
    with c2: st.write(f"🌎 **판별 시장:** {'국내 주식' if data['market'] == 'KR' else '미국 주식'}")
    
    # 버튼 실행
    if st.button("🚀 실시간 AI 정밀 분석 시작"):
        price = get_realtime_price(t_input if data['market'] == 'KR' else data['ticker'], data['market'] == 'KR')
        
        # 기술적 분석 (v36000 로직)
        df = yf.download(data['ticker'], period="6mo", interval="1d", progress=False)
        close = df['Close']
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g/l))).iloc[-1]
        up_band = (ma20 + std * 2).iloc[-1]
        dn_band = (ma20 - std * 2).iloc[-1]
        
        st.markdown("---")
        cur = "원" if data['market'] == "KR" else "$"
        f_p = f"{format(int(price), ',')} {cur}" if data['market'] == "KR" else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(data['target']), ',')} {cur}" if data['market'] == "KR" else f"{cur}{data['target']:,.2f}"

        # 1. 결과 헤더
        st.markdown(f"<p class='big-price'>🔍 {data['name']} ({t_input}) 현재가: {f_p}</p>", unsafe_allow_html=True)

        # 2. 신호등
        if rsi > 70 or price > up_band:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < data['target'] * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 AI 산출 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        # 3. 상세 분석 요약
        st.markdown("### 📝 AI 추세 분석 요약")
        sum_msg = "상승 에너지가 강해 밴드 상단을 넘보고 있습니다." if price > up_band else "바닥 지지력을 테스트 중입니다."
        st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {data['name']}은(는) {sum_msg}<br>RSI {round(rsi,1)}는 {'과열 상태' if rsi>70 else '바닥 구간' if rsi<35 else '안정권'}입니다.</div>", unsafe_allow_html=True)

        # 4. 비교 지표 표
        st.table(pd.DataFrame({
            "핵심 지표": ["볼린저 밴드", "RSI (심리)", "적정가 대비"],
            "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(price/data['target']*100,1)}%"],
            "AI 진단": ["상단 돌파(주의)" if price > up_band else "하단 지입(기회)" if price < dn_band else "정상", "과열" if rsi>70 else "바닥" if rsi<30 else "보통", "고평가" if price > data['target'] else "저평가"]
        }))
else:
    st.info("종목 코드를 입력하면 AI가 자동으로 시장을 분석합니다.")
