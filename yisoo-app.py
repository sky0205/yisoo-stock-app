import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 기본 설정 ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 32px; font-weight: 700; margin-bottom: 25px; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 미장·국장 하이브리드 추정치 엔진 ---
def get_global_forward_valuation(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        
        name, eps_f, per_f = ticker_input, 0.0, 0.0
        
        # 🟢 국장: 네이버 증권 추정치 우선
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            
            try:
                table = soup.select(".section.cop_analysis table")[0]
                rows = table.select("tr")
                for row in rows:
                    if "EPS" in row.text:
                        tds = row.select("td")
                        eps_f = float(tds[-2].text.replace(',', '').strip())
                    if "PER" in row.text:
                        tds = row.select("td")
                        per_f = float(tds[-2].text.replace(',', '').strip())
            except: pass

        # 🔵 미장 (또는 국장 데이터 부재 시): 야후 파이낸스 추정치 호출
        if eps_f < 1 or per_f < 1:
            stock = yf.Ticker(y_ticker)
            info = stock.info
            # 미장의 핵심: Forward EPS (2026년 이후 추정치)
            eps_f = info.get('forwardEps') or info.get('trailingEps') or 1.0
            per_f = info.get('forwardPE') or info.get('trailingPE') or 15.0
            if not is_kr: name = info.get('shortName', ticker_input)

        target_val = float(eps_f * per_f)
        price = yf.Ticker(y_ticker).fast_info['lastPrice']
            
        return name, target_val, eps_f, per_f, y_ticker, is_kr, price
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False, 0.0

# --- [2] 메인 화면 ---
st.title("🏆 v36000 AI 마스터: 글로벌 추정치 통합 분석")

t_input = st.text_input("🔢 종목코드(국장) 또는 티커(미장, 예: NVDA)를 입력하세요", value="NVDA")
name, target, eps_f, per_f, y_tick, is_kr, curr_p = get_global_forward_valuation(t_input)

st.success(f"📍 분석 종목: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("미래 추정 EPS", f"{format(int(eps_f), ',')}원" if is_kr else f"${round(eps_f, 2)}")
with c2: st.metric("기대 멀티플(PER)", f"{round(per_f, 2)}배")
with c3: st.metric("추정 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 실시간 정밀 분석 시작"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
        price = float(df['Close'].iloc[-1])
        # 기술적 지표 계산 (스칼라 변환)
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_band = float((ma20 + std * 2).iloc[-1]); dn_band = float((ma20 - std * 2).iloc[-1])
        delta = df['Close'].diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
        
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
        st.markdown(f"<div class='target-box'>💎 글로벌 추정치 기반 적정주가: {f_tg}</div>", unsafe_allow_html=True)
