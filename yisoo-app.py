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

# --- [1] 실시간 AI 데이터 엔진 (9% 고정 및 강제 산출) ---
def get_intrinsic_value(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        
        # 1. 종목명 검색 (국장은 네이버 우선)
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = stock.info.get('shortName') or stock.info.get('longName') or ticker_input

        # 2. 적정주가 산출 (S-RIM 9% 모델)
        info = stock.info
        r = 0.09 # 요구수익률 9% 고정
        
        # BPS 확보 (없으면 PBR 역산)
        bps = info.get('bookValue')
        if not bps or bps <= 1:
            pbr = info.get('priceToBook') or 1
            price = info.get('currentPrice') or info.get('previousClose') or 1
            bps = price / pbr
            
        # ROE 확보 (없으면 15% 가정 - 성장주 고려)
        roe = info.get('returnOnEquity')
        if not roe or roe == 0: roe = 0.15 
        if roe > 1: roe = roe / 100
        
        target_val = float(bps * (roe / r)) if bps > 0 else 0.0
        
        # [수리 포인트] 1원 방지 하한선 (현재가의 80% 보장)
        curr_p = info.get('currentPrice') or info.get('previousClose') or 1.0
        if target_val < curr_p * 0.5: target_val = curr_p * 0.8
            
        return name, target_val, y_ticker, is_kr
    except:
        return ticker_input, 0.0, ticker_input, False

# --- [2] 세션 상태 관리 (실시간 동기화의 핵심) ---
if 'last_ticker' not in st.session_state: st.session_state['last_ticker'] = ""
if 'auto_name' not in st.session_state: st.session_state['auto_name'] = ""
if 'auto_target' not in st.session_state: st.session_state['auto_target'] = 0.0

# --- [3] 메인 화면 레이아웃 ---
st.title("🏆 v36000 AI 마스터: 실시간 동기화")

# 한 줄 입력창
t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커를 입력하고 [Enter]를 치세요", value="005930")

# 코드가 바뀌면 즉시 AI 계산 실행
if t_input != st.session_state['last_ticker']:
    name, target, y_tick, is_kr = get_intrinsic_value(t_input)
    st.session_state['auto_name'] = name
    st.session_state['auto_target'] = target
    st.session_state['last_ticker'] = t_input
    st.session_state['y_ticker'] = y_tick
    st.session_state['is_kr'] = is_kr

# 설정창 (AI가 채워준 값이 실시간으로 노출됨)
c1, c2 = st.columns(2)
with c1: in_name = st.text_input("📍 종목명", value=st.session_state['auto_name'])
with c2: in_target = st.number_input("💎 AI 적정주가 (9% 기준)", value=float(st.session_state['auto_target']), step=0.1)

# --- [4] 분석 실행 ---
if st.button("🚀 4대 지표 실시간 정밀 분석 시작"):
    df = yf.download(st.session_state['y_ticker'], period="6mo", interval="1d", progress=False)
    if df.empty and st.session_state['is_kr']: 
        df = yf.download(t_input + ".KQ", period="6mo", interval="1d", progress=False)

    if not df.empty:
        # [ValueError 해결] 모든 지표를 스칼라 숫자로 변환
        close = df['Close']
        price = float(close.iloc[-1])
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        up_band = float((ma20 + std * 2).iloc[-1])
        dn_band = float((ma20 - std * 2).iloc[-1])
        
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = float(((h14 - close) / (h14 - l14) * -100).iloc[-1])
        exp1 = close.ewm(span=12, adjust=False).mean(); exp2 = close.ewm(span=26, adjust=False).mean()
        macd_val = float((exp1 - exp2).iloc[-1])

        st.markdown("---")
        cur = "원" if st.session_state['is_kr'] else "$"
        f_p = f"{format(int(price), ',')} {cur}" if st.session_state['is_kr'] else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(in_target), ',')} {cur}" if st.session_state['is_kr'] else f"{cur}{in_target:,.2f}"

        st.markdown(f"<p class='big-price'>🔍 {in_name} 현재가: {f_p}</p>", unsafe_allow_html=True)
        
        # 신호등 로직
        if rsi > 70 or price > up_band:
            bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
        elif price < in_target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 적정주가 가이드(9%): {f_tg}</div>", unsafe_allow_html=True)

        # 4대 지표 표
        st.table(pd.DataFrame({
            "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
            "진단": ["과열" if price > up_band else "바닥" if price < dn_band else "정상", "주의" if rsi>70 else "바닥" if rsi<30 else "보통", "단기천장" if wr>-20 else "단기바닥" if wr<-80 else "보통", "상승세" if macd_val>0 else "하락 압력"]
        }))
    else:
        st.error("데이터 로딩 실패! 코드를 확인해 주세요.")
