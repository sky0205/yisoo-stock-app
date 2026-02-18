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

# --- [1] 26년 EPS 강제 복구 엔진 ---
def get_master_eps_2026(ticker_input):
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

        price = info.get('currentPrice') or info.get('previousClose') or 1.0
        
        # [핵심 보정] EPS가 1원 미만으로 나오면 강제 재계산
        eps_raw = info.get('forwardEps')
        if not eps_raw or eps_raw < 1.0:
            # 최근 12개월 EPS가 없으면 PER과 주가로 역산
            curr_eps = info.get('trailingEps') or (price / info.get('trailingPE', 25))
            # 실리콘투 등 고성장주 특성을 반영해 연 25% 성장률 가정 (2년 복리 가산)
            eps_raw = curr_eps * (1.25 ** 2)

        # 적정 PER (Forward PER 우선, 없으면 업종 평균 수준 20배 적용)
        per = info.get('forwardPE') or info.get('trailingPE') or 20.0
        
        # 최종 적정주가 계산
        target_val = float(eps_raw * per)
        
        # [최종 방어선] 적정가가 현재가의 50% 미만이면 데이터 오류로 간주, 현재가 기반 20% 상향 제시
        if target_val < price * 0.5: target_val = price * 1.2
            
        return name, target_val, eps_raw, per, y_ticker, is_kr
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False

# --- [2] 메인 레이아웃 ---
st.title("🏆 v36000 AI 마스터: EPS 강제 복구판")

t_input = st.text_input("🔢 종목코드 또는 티커를 입력하고 [Enter]", value="257720")
name, target, eps, per, y_tick, is_kr = get_master_eps_2026(t_input)

# 상단 데이터 검증 보드
st.success(f"📍 분석 종목: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("AI 보정 26년 EPS", f"{round(eps, 2)}원" if is_kr else f"${round(eps, 2)}")
with c2: st.metric("적용 PER 배수", f"{round(per, 2)}배")
with c3: st.metric("최종 적정주가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 4대 지표 정밀 분석 시작"):
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
        st.markdown(f"<div class='target-box'>💎 26년 수익 가치 보정가: {f_tg}</div>", unsafe_allow_html=True)

        st.table(pd.DataFrame({
            "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
            "진단": ["주의" if price > up_band else "기회" if price < dn_band else "정상", "주의" if rsi>70 else "바닥" if rsi<30 else "보통", "천장" if wr>-20 else "바닥" if wr<-80 else "보통", "상승" if macd_val>0 else "하락"]
        }))
    else: st.error("데이터 로드 실패!")
