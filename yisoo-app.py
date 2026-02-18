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
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 수익성 직결 엔진 (EPS * PER) ---
def get_pure_valuation(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # 이름 자동 검색
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = info.get('shortName') or info.get('longName') or ticker_input

        # [공식 수정] 요구수익률 없이 시장 PER 기반 산출
        price = info.get('currentPrice') or info.get('previousClose') or 1.0
        eps = info.get('forwardEps') or info.get('trailingEps') or (price / info.get('trailingPE', 15))
        per = info.get('trailingPE') or info.get('forwardPE') or 15.0 # 데이터 없으면 시장 평균 15배
        
        # 적정주가 = 주당순이익(EPS) * 현재 배수(PER)
        target_val = float(eps * per)
        
        # 데이터 오류로 인한 '1원' 방지: 적정가가 현재가와 너무 동떨어지면 현재가로 보정
        if target_val <= 1 or target_val < price * 0.1:
            target_val = price 
            
        return name, target_val, y_ticker, is_kr
    except:
        return ticker_input, 0.0, ticker_input, False

# --- [2] 메인 레이아웃 ---
st.title("🏆 v36000 AI 마스터: 순수 수익성 모델")

t_input = st.text_input("🔢 종목코드 또는 티커를 입력하고 [Enter]", value="257720")
name, target, y_tick, is_kr = get_pure_valuation(t_input)

# 상단 결과 표시 (적정주가란 제거 및 결과 자동 노출)
st.success(f"📍 분석 종목: **{name}** | 💎 시장 PER 기반 적정가: **{format(int(target), ',') if is_kr else round(target, 2)}**")

if st.button("🚀 실시간 4대 지표 정밀 분석 시작"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
        # [ValueError 박멸] 모든 지표를 스칼라 숫자로 강제 변환
        price = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_band = float((ma20 + std * 2).iloc[-1]); dn_band = float((ma20 - std * 2).iloc[-1])
        
        delta = df['Close'].diff()
        g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
        
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = float(((h14 - df['Close']) / (h14 - l14) * -100).iloc[-1])
        
        exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd_val = float((exp1 - exp2).iloc[-1])

        st.markdown("---")
        cur = "원" if is_kr else "$"
        f_p = f"{format(int(price), ',')} {cur}" if is_kr else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(target), ',')} {cur}" if is_kr else f"{cur}{target:,.2f}"

        st.markdown(f"<p class='big-price'>🔍 {name} 현재가: {f_p}</p>", unsafe_allow_html=True)
        
        # 신호등 로직
        if rsi > 70 or price > up_band:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 EPS × PER 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        st.table(pd.DataFrame({
            "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
            "진단": ["과열" if price > up_band else "기회" if price < dn_band else "정상", "주의" if rsi>70 else "바닥" if rsi<30 else "보통", "천장" if wr>-20 else "바닥" if wr<-80 else "보통", "상승" if macd_val>0 else "하락"]
        }))
    else: st.error("데이터 로딩 실패!")
