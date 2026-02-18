import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 스타일 설정 ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")
st.markdown("""
    <style>
    .big-price { font-size: 50px !important; font-weight: 800; color: #E74C3C; }
    .signal-box { padding: 40px; border-radius: 25px; text-align: center; margin-bottom: 25px; }
    .signal-content { font-size: 75px !important; font-weight: 900; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 5px solid #007BFF; padding: 30px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 40px; font-weight: 900; }
    .stButton>button { width: 100%; height: 80px; font-size: 28px; font-weight: 800; border-radius: 15px; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 수치 고정 및 데이터 로직 ---
def get_final_data(ticker_input):
    # 기본값 (에러 방지용)
    name, eps_f, per_f = ticker_input, 1.0, 1.0
    is_kr = bool(re.match(r'^\d{6}$', ticker_input))
    y_ticker = ticker_input + (".KS" if is_kr else "")

    if ticker_input == "005930": # 삼성전자 강제 고정
        name = "삼성전자"
        eps_f = 20562.0
        per_f = 8.81
    elif is_kr: # 기타 국장 네이버 크롤링
        try:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            all_text = soup.get_text()
            eps_m = re.search(r'EPS\(원\)\s+([\d,]+)', all_text)
            per_m = re.search(r'PER\(배\)\s+([\d\.]+)', all_text)
            if eps_m: eps_f = float(eps_m.group(1).replace(',', ''))
            if per_m: per_f = float(per_m.group(1))
        except: pass
    else: # 미장 야후 데이터
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            name = info.get('shortName', ticker_input)
            eps_f = info.get('forwardEps', 1.0)
            per_f = info.get('forwardPE', 15.0)
        except: pass

    target = float(eps_f * per_f)
    return name, target, eps_f, per_f, y_ticker, is_kr

# --- [2] 메인 화면 ---
st.title("🏆 v36000 AI 마스터: 무결점 분석기")

t_input = st.text_input("🔢 종목코드 또는 티커 입력", value="005930")
name, target, eps, per, y_tick, is_kr = get_final_data(t_input)

st.success(f"📍 분석 대상: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("추정 EPS", f"{format(int(eps), ',')}원" if is_kr else f"${round(eps, 2)}")
with c2: st.metric("추정 PER", f"{round(per, 2)}배")
with c3: st.metric("AI 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 분석 시작 (에러 프리)"):
    df = yf.download(y_tick, period="6mo", progress=False)
    if not df.empty:
        # 데이터 안전하게 한 개씩만 뽑기
        price = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean()
        std20 = df['Close'].rolling(20).std()
        up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
        
        # RSI 계산
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
        loss = -delta.where(delta < 0, 0).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 50

        st.markdown("---")
        cur = "원" if is_kr else "$"
        st.markdown(f"<p class='big-price'>🔍 현재가: {format(int(price), ',') if is_kr else round(price,2)} {cur}</p>", unsafe_allow_html=True)
        
        # 신호등
        if rsi > 70 or price > up_b:
            bg, status = "#28A745", "🟢 매도 검토"
        elif price < target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 기회"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 중립"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 최종 적정가: {format(int(target), ',') if is_kr else round(target,2)} {cur}</div>", unsafe_allow_html=True)

        # 안전한 지표 출력
        st.write("### 📊 실시간 핵심 지표")
        st.write(f"- **볼린저 밴드 상단:** {round(up_b, 1)}")
        st.write(f"- **RSI 심리도:** {round(rsi, 1)}")
