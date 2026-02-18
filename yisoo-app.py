import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 기본 설정 및 스타일 (시인성 극대화) ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-content { font-size: 48px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 32px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #000000 !important; }
    .summary-box b { color: #000000 !important; font-weight: 800; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 지능형 데이터 엔진 (ValueError 방지 보강) ---
@st.cache_data(ttl=3600)
def fetch_ai_stock_info(user_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', user_input))
        y_ticker = user_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        
        # 이름 자동 검색 (국장은 네이버, 미장은 야후)
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={user_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = stock.info.get('shortName', user_input)

        # AI 적정주가 (S-RIM) 계산
        info = stock.info
        bps = info.get('bookValue') or info.get('priceToBook', 0) * (info.get('currentPrice', 1) / info.get('priceToBook', 1))
        roe = info.get('returnOnEquity') or 0.10
        r = 0.09 # 요구수익률 9%
        target_val = float(bps + (bps * (roe - r) / r)) if bps > 0 else 0.0
            
        return {"name": name, "target": target_val, "ticker": y_ticker, "is_kr": is_kr}
    except:
        return None

# --- [2] 메인 화면 및 입력부 ---
st.title("🏆 이수할아버지 v36000 AI 마스터")

t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커를 입력하세요", value="005930")
ai_data = fetch_ai_stock_info(t_input)

if ai_data:
    c1, c2 = st.columns(2)
    with c1: in_name = st.text_input("📍 종목명 (자동완성)", value=ai_data['name'])
    with c2: in_target = st.number_input("💎 AI 적정주가 (S-RIM)", value=ai_data['target'], step=0.1)
    
    if st.button("🚀 실시간 AI 정밀 분석 시작"):
        # 기술적 분석 데이터 (ValueError 방지를 위해 scalar 변환 철저히)
        df = yf.download(ai_data['ticker'], period="6mo", interval="1d", progress=False)
        if df.empty and ai_data['is_kr']: 
            df = yf.download(t_input + ".KQ", period="6mo", interval="1d", progress=False)

        if not df.empty:
            close_series = df['Close']
            price = float(close_series.iloc[-1]) # 마지막 가격을 숫자로 확정
            ma20 = close_series.rolling(20).mean()
            std = close_series.rolling(20).std()
            
            up_band = float((ma20 + std * 2).iloc[-1]) # 숫자로 확정
            dn_band = float((ma20 - std * 2).iloc[-1]) # 숫자로 확정
            
            # RSI 계산
            delta = close_series.diff()
            g = delta.where(delta > 0, 0).rolling(14).mean()
            l = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1]) # 숫자로 확정

            st.markdown("---")
            cur = "원" if ai_data['is_kr'] else "$"
            f_p = f"{format(int(price), ',')} {cur}" if ai_data['is_kr'] else f"{cur}{price:,.2f}"
            f_tg = f"{format(int(in_target), ',')} {cur}" if ai_data['is_kr'] else f"{cur}{in_target:,.2f}"

            # 1. 결과 헤더
            st.markdown(f"<p class='big-price'>🔍 {in_name} 현재가: {f_p}</p>", unsafe_allow_html=True)
            
            # 2. 신호등 (ValueError 완전 차단)
            if rsi > 70 or price > up_band:
                bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
            elif price < in_target * 0.95:
                bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
            else:
                bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
            
            st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='target-box'>💎 적정주가 기준: {f_tg}</div>", unsafe_allow_html=True)

            # 3. 요약 (시인성 보정)
            st.markdown("### 📝 AI 추세 분석 요약")
            sum_msg = "상승 에너지가 강해 밴드 상단을 넘보고 있습니다." if price > up_band else "바닥 지지력을 테스트 중입니다."
            st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {in_name}은(는) {sum_msg}<br>RSI {round(rsi,1)}는 {'과열 상태' if rsi>70 else '바닥 구간' if rsi<35 else '안정권'}입니다.</div>", unsafe_allow_html=True)

            # 4. 상세 지표 표
            st.table(pd.DataFrame({
                "핵심 지표": ["볼린저 밴드", "RSI (심리)", "적정가 대비"],
                "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(price/in_target*100,1) if in_target > 0 else 0}%"],
                "진단": ["과열" if price > up_band else "바닥" if price < dn_band else "정상", "주의" if rsi>70 else "바닥" if rsi<30 else "보통", "고평가" if price > in_target else "저평가"]
            }))
        else:
            st.error("데이터를 가져올 수 없습니다. 코드나 티커를 확인해 주세요.")
else:
    st.info("종목 코드를 입력하면 AI가 분석을 시작합니다.")
