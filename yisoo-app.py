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
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; color: #000000 !important; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 신규 공식 엔진 (EPS x PER & BPS x PBR) ---
def get_dual_valuation(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # 이름 검색
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = info.get('shortName') or info.get('longName') or ticker_input

        # 공식 재설계 (9% 요구수익률 기준)
        r = 0.09
        eps = info.get('forwardEps') or info.get('trailingEps') or 0
        bps = info.get('bookValue') or (info.get('currentPrice', 1) / info.get('priceToBook', 1))
        roe = info.get('returnOnEquity') or 0.10
        if roe > 1: roe /= 100

        # 방식 1: EPS x 적정 PER (11.1배)
        val_eps = eps * (1/r)
        # 방식 2: BPS x 적정 PBR (ROE/r)
        val_bps = bps * (roe / r)
        
        # 두 방식의 평균을 적정가로 산출 (데이터 누락 대비)
        if val_eps > 0 and val_bps > 0: target_val = (val_eps + val_bps) / 2
        else: target_val = max(val_eps, val_bps)

        # 1원 방지용 하한선
        curr_p = info.get('currentPrice') or info.get('previousClose') or 1.0
        if target_val < curr_p * 0.5: target_val = curr_p * 0.8
            
        return name, target_val, y_ticker, is_kr
    except:
        return ticker_input, 0.0, ticker_input, False

# --- [2] 세션 및 메인 화면 ---
if 'last_ticker' not in st.session_state: st.session_state['last_ticker'] = ""
t_input = st.text_input("🔢 종목코드 또는 티커를 입력하고 엔터를 치세요", value="005930")

if t_input != st.session_state['last_ticker']:
    name, target, y_tick, is_kr = get_dual_valuation(t_input)
    st.session_state['auto_name'], st.session_state['auto_target'] = name, target
    st.session_state['last_ticker'], st.session_state['y_ticker'], st.session_state['is_kr'] = t_input, y_tick, is_kr

c1, c2 = st.columns(2)
with c1: in_name = st.text_input("📍 종목명", value=st.session_state.get('auto_name', ''))
with c2: in_target = st.number_input("💎 새 공식 적정주가 (9%)", value=float(st.session_state.get('auto_target', 0)))

if st.button("🚀 정밀 분석 시작"):
    df = yf.download(st.session_state['y_ticker'], period="6mo", interval="1d", progress=False)
    if not df.empty:
        # [ValueError 해결] 모든 데이터를 float(숫자)로 강제 변환
        price = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_band = float((ma20 + std * 2).iloc[-1])
        dn_band = float((ma20 - std * 2).iloc[-1])
        
        delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = float(((h14 - df['Close']) / (h14 - l14) * -100).iloc[-1])
        exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd_val = float((exp1 - exp2).iloc[-1])

        st.markdown("---")
        cur = "원" if st.session_state['is_kr'] else "$"
        f_p = f"{format(int(price), ',')} {cur}" if st.session_state['is_kr'] else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(in_target), ',')} {cur}" if st.session_state['is_kr'] else f"{cur}{in_target:,.2f}"

        st.markdown(f"<p class='big-price'>🔍 {in_name} 현재가: {f_p}</p>", unsafe_allow_html=True)
        
        # 신호등 로직 (9% 기준 적정가 비교)
        if rsi > 70 or price > up_band:
            bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
        elif price < in_target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 새 공식 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        st.table(pd.DataFrame({
            "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
            "진단": ["과열" if price > up_band else "바닥" if price < dn_band else "정상", "주의" if rsi>70 else "바닥" if rsi<30 else "보통", "단기천장" if wr>-20 else "단기바닥" if wr<-80 else "보통", "상승세" if macd_val>0 else "하락 압력"]
        }))
    else: st.error("데이터 로딩 실패!")
