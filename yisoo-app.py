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
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; color: #000000 !important; border-radius: 0 15px 15px 0; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 최적 적정주가 엔진 (보정형 S-RIM, r=9%) ---
@st.cache_data(ttl=3600)
def fetch_refined_stock_info(user_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', user_input))
        y_ticker = user_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # 1. 이름 검색
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={user_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = info.get('shortName') or info.get('longName') or user_input

        # 2. 보정형 S-RIM 엔진 (가장 적합한 공식)
        r = 0.09 # 요구수익률 9% 고정
        
        # BPS 확보 (누락 시 PBR 역산)
        bps = info.get('bookValue')
        if not bps or bps == 0:
            price = info.get('currentPrice') or info.get('previousClose') or 1
            pbr = info.get('priceToBook') or 1
            bps = price / pbr
            
        # ROE 확보 (누락 시 PER/PBR 역산 또는 기본치 적용)
        roe = info.get('returnOnEquity')
        if not roe or roe == 0:
            per = info.get('trailingPE')
            pbr = info.get('priceToBook')
            if per and pbr: roe = pbr / per
            else: roe = 0.10 # 데이터 전무할 경우 시장 평균 10%
            
        # ROE 단위 보정 (퍼센트 -> 소수점)
        if roe > 1: roe = roe / 100
        
        # [최적 공식 적용] 적정주가 = BPS * (ROE / r)
        # 이 공식은 미래의 초과이익이 영구히 지속된다고 가정하는 S-RIM의 가장 합리적인 요약 버전입니다.
        target_val = float(bps * (roe / r))
        
        # [이상치 보정 로직] 
        # ROE가 마이너스(적자)거나 너무 낮아 적정주가가 터무니없을 경우: BPS의 70%를 청산 가치로 인정
        if roe <= 0.03 or target_val < bps * 0.7:
            target_val = bps * 0.7
            
        # 지나친 고평가 방지 (ROE가 너무 높을 경우 캡 씌움)
        if roe > 0.40: # ROE 40% 이상은 지속 불가능하다고 판단
            target_val = bps * (0.40 / r)

        return {"name": name, "target": target_val, "ticker": y_ticker, "is_kr": is_kr}
    except:
        return None

# --- [2] 메인 화면 ---
st.title("🏆 이수할아버지 v36000 AI 마스터 (9% 최적화)")

t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커(영문) 입력", value="005930")
ai_data = fetch_refined_stock_info(t_input)

if ai_data:
    c1, c2 = st.columns(2)
    with c1: st.text_input("📍 분석 종목명", value=ai_data['name'], disabled=True)
    with c2: in_target = st.number_input("💎 AI 최적 적정주가 (9%)", value=ai_data['target'], step=0.1)
    
    if st.button("🚀 실시간 4대 지표 정밀 분석 시작"):
        df = yf.download(ai_data['ticker'], period="6mo", interval="1d", progress=False)
        if df.empty and ai_data['is_kr']: 
            df = yf.download(t_input + ".KQ", period="6mo", interval="1d", progress=False)

        if not df.empty:
            close = df['Close']
            price = float(close.iloc[-1])
            ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
            up_band = float((ma20 + std * 2).iloc[-1])
            dn_band = float((ma20 - std * 2).iloc[-1])
            
            # 4대 지수 계산 (ValueError 방지 스칼라화)
            delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            wr = float(((h14 - close) / (h14 - l14) * -100).iloc[-1])
            exp1 = close.ewm(span=12, adjust=False).mean(); exp2 = close.ewm(span=26, adjust=False).mean()
            macd_val = float((exp1 - exp2).iloc[-1])

            st.markdown("---")
            cur = "원" if ai_data['is_kr'] else "$"
            f_p = f"{format(int(price), ',')} {cur}" if ai_data['is_kr'] else f"{cur}{price:,.2f}"
            f_tg = f"{format(int(in_target), ',')} {cur}" if ai_data['is_kr'] else f"{cur}{in_target:,.2f}"

            st.markdown(f"<p class='big-price'>🔍 {ai_data['name']} 현재가: {f_p}</p>", unsafe_allow_html=True)
            
            # 신호등 로직
            if rsi > 70 or price > up_band:
                bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
            elif price < in_target * 0.95:
                bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
            else:
                bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
            
            st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='target-box'>💎 최적 적정주가: {f_tg}</div>", unsafe_allow_html=True)

            # 4대 지표 표
            st.table(pd.DataFrame({
                "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
                "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
                "AI 진단": ["상단 돌파(주의)" if price > up_band else "하단 지지(기회)" if price < dn_band else "정상", "과열" if rsi>70 else "바닥" if rsi<30 else "보통", "단기천장" if wr>-20 else "단기바닥" if wr<-80 else "보통", "상승세" if macd_val>0 else "하락세"]
            }))
        else:
            st.error("데이터 로딩 실패! 코드 확인 요망")
