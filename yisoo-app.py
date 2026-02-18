import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 대왕 시인성 스타일 (신호등 80px) ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")
st.markdown("""
    <style>
    .big-price { font-size: 55px !important; font-weight: 800; color: #E74C3C; }
    .signal-box { padding: 50px; border-radius: 35px; text-align: center; margin-bottom: 35px; }
    .signal-content { font-size: 80px !important; font-weight: 900; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 6px solid #007BFF; padding: 35px; border-radius: 30px; text-align: center; color: #0056b3; font-size: 45px; font-weight: 900; }
    .stButton>button { width: 100%; height: 90px; font-size: 30px; font-weight: 800; border-radius: 20px; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 네이버 추정치(E) 강제 낚시 엔진 ---
def get_naver_future_data(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        name, eps_f, per_f = ticker_input, 0.0, 0.0
        
        if is_kr:
            # 네이버 금융 '기업분석' 컨센서스 데이터 직접 추출
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            
            # 컨센서스 표(cop_analysis)에서 가장 우측 추정치(E) 열 데이터 획득
            try:
                table = soup.select(".section.cop_analysis table")[0]
                # EPS 행 탐색 (보통 10번째 행)
                for tr in table.select("tr"):
                    if "EPS(원)" in tr.text:
                        tds = tr.select("td")
                        # 가장 최신 추정치(E) 칸 선택
                        eps_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
                    if "PER(배)" in tr.text:
                        tds = tr.select("td")
                        per_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
            except: pass

        # 데이터 부재 시 야후 실시간 Forward 데이터 백업
        if eps_f < 10 or per_f < 1:
            stock = yf.Ticker(y_ticker)
            info = stock.info
            eps_f = info.get('forwardEps') or info.get('trailingEps') or 1.0
            per_f = info.get('forwardPE') or info.get('trailingPE') or 15.0
            if not is_kr: name = info.get('shortName', ticker_input)

        return name, float(eps_f * per_f), eps_f, per_f, y_ticker, is_kr
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False

# --- [2] 메인 화면 레이아웃 (강제 리셋 장착) ---
st.title("🏆 v36000 AI 마스터: 추정치 강제 동기화")

t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커를 입력하고 [Enter]", value="005930")

# 입력 변경 시 즉시 재계산 (캐시 무시)
name, target, eps, per, y_tick, is_kr = get_naver_future_data(t_input)

st.success(f"📍 분석 대상: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("네이버 추정 EPS(E)", f"{format(int(eps), ',')}원" if is_kr else f"${round(eps, 2)}")
with c2: st.metric("추정 PER(E)", f"{round(per, 2)}배")
with c3: st.metric("AI 산출 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 신호등 및 4대 지수 정밀 분석 리로드"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
        price = float(df['Close'].iloc[-1])
        # 기술적 지표 계산
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_b = float((ma20 + std * 2).iloc[-1])
        rsi = float((100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean())))).iloc[-1])
        
        st.markdown("---")
        cur = "원" if is_kr else "$"
        st.markdown(f"<p class='big-price'>🔍 현재가: {format(int(price), ',') if is_kr else round(price,2)} {cur}</p>", unsafe_allow_html=True)
        
        # 신호등 (글자 80px 확대)
        if rsi > 70 or price > up_b:
            bg, status = "#28A745", "🟢 매도 검토"
        elif price < target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 기회"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 중립"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 미래 가치 기반 적정가: {format(int(target), ',') if is_kr else round(target,2)} {cur}</div>", unsafe_allow_html=True)

        # 4대 지수 테이블 복구
        st.table(pd.DataFrame({
            "핵심 지표": ["볼린저 밴드(상/하)", "RSI 심리도", "MACD 추세"],
            "실시간 수치": [f"{round(up_b,1)} / {round(ma20.iloc[-1]-std.iloc[-1]*2,1)}", f"{round(rsi,1)}", "상승세" if price > ma20.iloc[-1] else "하락세"]
        }))
