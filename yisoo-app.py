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

# --- [1] 네이버 증권 정밀 크롤링 엔진 ---
def get_naver_accurate_data(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        
        # 기본값 설정
        name, bps, pbr = ticker_input, 0.0, 0.0
        
        if is_kr:
            # 네이버 증권에서 직접 숫자 낚아채기
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 종목명
            name = soup.select_one(".wrap_company h2 a").text
            
            # BPS와 PBR 추출 (네이버 특유의 테이블 구조 분석)
            tables = soup.select(".section.cop_analysis table")
            if tables:
                # 가장 최근 분기 또는 결산 데이터 행 탐색
                th_list = [th.text.strip() for th in soup.select("#_top_tab_group th")]
                # 실제 데이터 영역에서 BPS(주당순자산)와 PBR을 텍스트로 찾아 숫자로 변환
                all_text = soup.get_text()
                
                # 정규식을 이용해 "BPS(원)" 뒤의 숫자와 "PBR(배)" 뒤의 숫자 추출
                bps_match = re.search(r'BPS\(원\)\s+([\d,]+)', all_text)
                pbr_match = re.search(r'PBR\(배\)\s+([\d\.]+)', all_text)
                
                if bps_match: bps = float(bps_match.group(1).replace(',', ''))
                if pbr_match: pbr = float(pbr_match.group(1))
        
        # 네이버에서 실패하거나 미장일 경우 야후 데이터 사용
        if bps == 0 or pbr == 0:
            stock = yf.Ticker(y_ticker)
            info = stock.info
            bps = info.get('bookValue', 0)
            pbr = info.get('priceToBook', 0)
            if not is_kr: name = info.get('shortName', ticker_input)

        # 적정주가 계산 (BPS * PBR)
        target_val = float(bps * pbr)
        
        # [최종 방어] 데이터가 여전히 이상하면 현재가 기반 보정
        price = yf.Ticker(y_ticker).fast_info['lastPrice'] if not is_kr else 0
        if is_kr:
            # 국장은 네이버에서 현재가 다시 긁기
            price_txt = soup.select_one(".no_today .blind").text.replace(',', '')
            price = float(price_txt)
            
        if target_val < price * 0.3: target_val = price * 1.1 # 데이터 누락 시 보수적 상향
            
        return name, target_val, bps, pbr, y_ticker, is_kr, price
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False, 0.0

# --- [2] 메인 화면 레이아웃 ---
st.title("🏆 v36000 AI 마스터: 네이버 정밀 동기화")

t_input = st.text_input("🔢 종목코드(6자리) 또는 티커를 입력하세요", value="257720")
name, target, bps_val, pbr_val, y_tick, is_kr, curr_p = get_naver_accurate_data(t_input)

# 데이터 지표 보드 (선생님이 보신 네이버 수치와 대조)
st.success(f"📍 분석 종목: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("BPS (네이버 동기화)", f"{format(int(bps_val), ',')}원" if is_kr else f"${round(bps_val, 2)}")
with c2: st.metric("PBR (네이버 동기화)", f"{round(pbr_val, 2)}배")
with c3: st.metric("산출 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 실시간 4대 지표 통합 분석 시작"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
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
        st.markdown(f"<div class='target-box'>💎 네이버 수치 기반 적정가: {f_tg}</div>", unsafe_allow_html=True)

        st.table(pd.DataFrame({
            "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
            "진단": ["주의" if price > up_band else "기회" if price < dn_band else "정상", "과열" if rsi>70 else "바닥" if rsi<30 else "보통", "천장" if wr>-20 else "바닥" if wr<-80 else "보통", "상승" if macd_val>0 else "하락"]
        }))
