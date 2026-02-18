import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 스타일 설정 (신호등 글자 크기 70px) ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")
st.markdown("""
    <style>
    .big-price { font-size: 50px !important; font-weight: 800; color: #E74C3C; }
    .signal-box { padding: 45px; border-radius: 30px; text-align: center; margin-bottom: 30px; }
    .signal-content { font-size: 70px !important; font-weight: 900; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 5px solid #007BFF; padding: 30px; border-radius: 25px; text-align: center; color: #0056b3; font-size: 40px; font-weight: 900; }
    .stButton>button { width: 100%; height: 80px; font-size: 28px; font-weight: 800; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 네이버/야후 미래 추정치 하이브리드 엔진 ---
def get_consensus_valuation(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        name, eps_f, per_f = ticker_input, 0.0, 0.0
        
        if is_kr:
            # 네이버 기업분석 테이블에서 직접 추정치(E) 낚아채기
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            try:
                # 컨센서스 테이블 행 분석
                rows = soup.select(".section.cop_analysis table tr")
                for row in rows:
                    if "EPS(원)" in row.text:
                        # 2025(E) 또는 2026(E) 위치의 데이터를 가져옴
                        tds = row.select("td")
                        eps_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
                    if "PER(배)" in row.text:
                        tds = row.select("td")
                        per_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
            except: pass

        # 추정치 부재 시 야후 Forward 데이터 활용
        if eps_f < 1 or per_f < 1:
            stock = yf.Ticker(y_ticker)
            eps_f = stock.info.get('forwardEps', 1.0)
            per_f = stock.info.get('forwardPE', 15.0)
            if not is_kr: name = stock.info.get('shortName', ticker_input)

        target_val = float(eps_f * per_f)
        return name, target_val, eps_f, per_f, y_ticker, is_kr
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False

# --- [2] 메인 레이아웃 ---
st.title("🏆 v36000 AI 마스터: 삼성전자 정밀 분석")

t_input = st.text_input("🔢 분석할 종목코드(6자리) 또는 티커를 입력하세요", value="005930")
name, target, eps_f, per_f, y_tick, is_kr = get_consensus_valuation(t_input)

st.success(f"📍 분석 종목: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("미래 추정 EPS", f"{format(int(eps_f), ',')}원" if is_kr else f"${round(eps_f, 2)}")
with c2: st.metric("시장 기대 PER", f"{round(per_f, 2)}배")
with c3: st.metric("추정 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 실시간 4대 지수 및 신호등 확인"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
        price = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_b = float((ma20 + std * 2).iloc[-1]); dn_b = float((ma20 - std * 2).iloc[-1])
        
        delta = df['Close'].diff()
        g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
        
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
        st.markdown(f"<div class='target-box'>💎 추정치 기반 적정가: {format(int(target), ',') if is_kr else round(target,2)} {cur}</div>", unsafe_allow_html=True)
        
        # 4대 지표 표
        st.markdown("### 📊 실시간 핵심 지표 분석")
        st.table(pd.DataFrame({
            "핵심 지표": ["볼린저 상단/하단", "RSI (심리도)", "현재가 상태"],
            "수치/진단": [f"{round(up_b,1)} / {round(dn_b,1)}", f"{round(rsi,1)}", "과열" if price > up_b else "바닥" if price < dn_b else "정상"]
        }))
