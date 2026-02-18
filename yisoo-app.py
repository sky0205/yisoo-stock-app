import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 스타일 설정 (신호등 70px 대왕 글자) ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")
st.markdown("""
    <style>
    .big-price { font-size: 50px !important; font-weight: 800; color: #E74C3C; }
    .signal-box { padding: 45px; border-radius: 30px; text-align: center; margin-bottom: 30px; }
    .signal-content { font-size: 70px !important; font-weight: 900; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 5px solid #007BFF; padding: 30px; border-radius: 25px; text-align: center; color: #0056b3; font-size: 40px; font-weight: 900; }
    .stButton>button { width: 100%; height: 80px; font-size: 28px; font-weight: 800; border-radius: 20px; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 실시간 추정치 낚시 엔진 (캐시 무시 로직) ---
def get_fresh_data(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        name, eps_f, per_f = ticker_input, 0.0, 0.0
        
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            # 네이버 컨센서스 표 직접 파싱
            rows = soup.select(".section.cop_analysis table tr")
            for row in rows:
                if "EPS(원)" in row.text:
                    tds = row.select("td")
                    eps_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
                if "PER(배)" in row.text:
                    tds = row.select("td")
                    per_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
        
        # 미장 또는 국장 데이터 부재 시 야후 실시간 호출
        if eps_f < 1 or per_f < 1:
            stock = yf.Ticker(y_ticker)
            eps_f = stock.info.get('forwardEps') or stock.info.get('trailingEps') or 1.0
            per_f = stock.info.get('forwardPE') or stock.info.get('trailingPE') or 15.0
            if not is_kr: name = stock.info.get('shortName', ticker_input)

        return name, float(eps_f * per_f), eps_f, per_f, y_ticker, is_kr
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False

# --- [2] 메인 레이아웃 (실시간 동기화 장착) ---
st.title("🏆 v36000 AI 마스터: 실시간 강제 동기화")

t_input = st.text_input("🔢 종목코드 또는 티커를 입력하고 [Enter]", value="005930")

# 입력이 바뀔 때마다 세션 초기화 및 재계산
name, target, eps, per, y_tick, is_kr = get_fresh_data(t_input)

st.success(f"📍 분석 종목: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("미래 추정 EPS", f"{format(int(eps), ',')}원" if is_kr else f"${round(eps, 2)}")
with c2: st.metric("예상 PER", f"{round(per, 2)}배")
with c3: st.metric("추정 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 분석 데이터 새로고침 및 신호등 확인"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
        price = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_b = float((ma20 + std * 2).iloc[-1])
        rsi = float((100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean())))).iloc[-1])
        
        st.markdown("---")
        cur = "원" if is_kr else "$"
        st.markdown(f"<p class='big-price'>🔍 현재가: {format(int(price), ',') if is_kr else round(price,2)} {cur}</p>", unsafe_allow_html=True)
        
        # 신호등 (글자 70px)
        if rsi > 70 or price > up_b:
            bg, status = "#28A745", "🟢 매도 검토"
        elif price < target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 기회"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 중립"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 2026 추정 적정가: {format(int(target), ',') if is_kr else round(target,2)} {cur}</div>", unsafe_allow_html=True)
