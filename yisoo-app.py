import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 스타일 세팅: 시인성 극대화 ---
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

# --- [1] 통합 정밀 엔진 (r=9% 절대 기준) ---
@st.cache_data(ttl=3600)
def fetch_master_valuation(user_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', user_input))
        y_ticker = user_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # 이름 자동 감지
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={user_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = info.get('shortName') or info.get('longName') or user_input

        # [정밀 적정주가 산출 로직]
        r = 0.09  # 요구수익률 9% 고정
        
        # 데이터 확보 (EPS, BPS, ROE 중 있는 것부터 순차적 적용)
        eps = info.get('forwardEps') or info.get('trailingEps') or 0
        bps = info.get('bookValue') or (info.get('currentPrice', 1) / info.get('priceToBook', 1))
        roe = info.get('returnOnEquity') or (eps / bps if bps > 0 else 0.10)
        
        # 1순위: S-RIM 공식 (BPS + 초과이익 가치)
        if bps > 0 and roe > 0:
            # 공식: BPS * (ROE / r)
            target_val = bps * (roe / r)
        # 2순위: 수익성 멀티플 (EPS * 11.11)
        elif eps > 0:
            target_val = eps * (1 / r)
        else:
            target_val = info.get('currentPrice', 0) * 0.9 # 최후의 수단: 현재가 보정

        # 비정상 수치 보정 (현재가의 50% ~ 300% 사이로 제한하여 신뢰도 확보)
        curr = info.get('currentPrice') or info.get('previousClose') or 1
        if target_val < curr * 0.5: target_val = curr * 0.8
        if target_val > curr * 3.0: target_val = curr * 1.5
            
        return {"name": name, "target": float(target_val), "ticker": y_ticker, "is_kr": is_kr, "curr": curr}
    except:
        return None

# --- [2] 메인 화면 레이아웃 ---
st.title("🏆 v36000 AI 마스터: 정밀 리부트")

t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커를 입력하세요", value="005930")
data = fetch_master_valuation(t_input)

if data:
    c1, c2 = st.columns(2)
    with c1: st.text_input("📍 분석 종목명", value=data['name'], disabled=True)
    with c2: in_target = st.number_input("💎 AI 9% 기준 정밀 적정가", value=data['target'], step=0.1)
    
    if st.button("🚀 4대 지표 실시간 정밀 분석 시작"):
        # 기술적 분석 데이터 호출 (국장/미장 완벽 대응)
        y_ticker = data['ticker']
        df = yf.download(y_ticker, period="6mo", interval="1d", progress=False)
        if df.empty and data['is_kr']: 
            y_ticker = t_input + ".KQ"
            df = yf.download(y_ticker, period="6mo", interval="1d", progress=False)

        if not df.empty:
            close = df['Close']
            price = float(close.iloc[-1])
            ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
            up_band = float((ma20 + std * 2).iloc[-1])
            dn_band = float((ma20 - std * 2).iloc[-1])
            
            # 4대 지표 (RSI, Williams, MACD)
            delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            wr = float(((h14 - close) / (h14 - l14) * -100).iloc[-1])
            exp1 = close.ewm(span=12, adjust=False).mean(); exp2 = close.ewm(span=26, adjust=False).mean()
            macd_val = float((exp1 - exp2).iloc[-1])

            st.markdown("---")
            cur = "원" if data['is_kr'] else "$"
            f_p = f"{format(int(price), ',')} {cur}" if data['is_kr'] else f"{cur}{price:,.2f}"
            f_tg = f"{format(int(in_target), ',')} {cur}" if data['is_kr'] else f"{cur}{in_target:,.2f}"

            st.markdown(f"<p class='big-price'>🔍 {data['name']} 현재가: {f_p}</p>", unsafe_allow_html=True)
            
            # 신호등 로직
            if rsi > 70 or price > up_band:
                bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
            elif price < in_target * 0.95:
                bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
            else:
                bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
            
            st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='target-box'>💎 9% 기준 적정주가: {f_tg}</div>", unsafe_allow_html=True)

            # 4대 지표 상세 표
            st.table(pd.DataFrame({
                "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
                "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
                "진단 결과": ["상단 돌파(주의)" if price > up_band else "하단 지지(기회)" if price < dn_band else "안정 주행", "심리 과열" if rsi>70 else "심리 바닥" if rsi<30 else "보통", "단기천장" if wr>-20 else "단기바닥" if wr<-80 else "보통", "상승세 우세" if macd_val>0 else "하락세 우세"]
            }))
        else:
            st.error("데이터 로딩 실패! 종목 코드나 인터넷 연결을 확인해 주세요.")
else:
    st.info("종목 코드를 입력하면 AI가 가장 정확한 공식을 찾아 분석을 시작합니다.")
