import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- [0] 기본 설정 및 스타일 (신호등 글자 크기 대폭 확대) ---
st.set_page_config(page_title="v36000 AI 마스터", layout="wide")

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 5px; }
    .signal-box { padding: 40px; border-radius: 25px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 25px; }
    /* 신호등 글자 크기 강화 */
    .signal-content { font-size: 60px !important; font-weight: 900; display: block; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 35px; font-weight: 800; margin-bottom: 25px; }
    .stButton>button { width: 100%; height: 70px; font-size: 26px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 미래 추정치(25-26년) 최우선 엔진 ---
def get_future_valuation(ticker_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', ticker_input))
        y_ticker = ticker_input + (".KS" if is_kr else "")
        name, eps_f, per_f = ticker_input, 0.0, 0.0
        
        # 🟢 국장: 네이버 컨센서스(25-26년) 추출
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={ticker_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            try:
                table = soup.select(".section.cop_analysis table")[0]
                # EPS/PER 행에서 25년/26년 추정치 칸(보통 마지막 두 칸) 탐색
                for row in table.select("tr"):
                    if "EPS" in row.text:
                        tds = row.select("td")
                        # 25~26년 추정치 중 데이터가 있는 가장 먼 미래 선택
                        eps_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
                    if "PER" in row.text:
                        tds = row.select("td")
                        per_f = float(tds[-2].text.replace(',','').strip()) if tds[-2].text.strip() else float(tds[-3].text.replace(',','').strip())
            except: pass

        # 🔵 미장/데이터부재시: 야후 Forward 데이터(25-26년) 추출
        if eps_f < 1 or per_f < 1:
            stock = yf.Ticker(y_ticker)
            info = stock.info
            eps_f = info.get('forwardEps') or info.get('trailingEps') or 1.0
            per_f = info.get('forwardPE') or info.get('trailingPE') or 15.0
            if not is_kr: name = info.get('shortName', ticker_input)

        target_val = float(eps_f * per_f)
        return name, target_val, eps_f, per_f, y_ticker, is_kr
    except:
        return ticker_input, 0.0, 0.0, 0.0, ticker_input, False

# --- [2] 메인 화면 ---
st.title("🏆 v36000 AI 마스터: 미래(25-26) 가치 분석")

t_input = st.text_input("🔢 종목코드 또는 티커를 입력하세요", value="005930")
name, target, eps_f, per_f, y_tick, is_kr = get_future_valuation(t_input)

st.success(f"📍 분석 대상: **{name}**")
c1, c2, c3 = st.columns(3)
with c1: st.metric("미래 추정 EPS", f"{format(int(eps_f), ',')}원" if is_kr else f"${round(eps_f, 2)}")
with c2: st.metric("예상 PER 배수", f"{round(per_f, 2)}배")
with c3: st.metric("추정 적정가", f"{format(int(target), ',')}원" if is_kr else f"${round(target, 2)}")

if st.button("🚀 4대 지수 및 신호등 실시간 분석"):
    df = yf.download(y_tick, period="6mo", interval="1d", progress=False)
    if not df.empty:
        # 지표 계산 (스칼라 변환 필수)
        price = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std = df['Close'].rolling(20).std()
        up_b = float((ma20 + std * 2).iloc[-1]); dn_b = float((ma20 - std * 2).iloc[-1])
        
        delta = df['Close'].diff()
        g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
        
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = float(((h14 - df['Close']) / (h14 - l14) * -100).iloc[-1])
        
        exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = float((exp1 - exp2).iloc[-1])

        st.markdown("---")
        cur = "원" if is_kr else "$"
        st.markdown(f"<p class='big-price'>🔍 현재가: {format(int(price), ',') if is_kr else round(price,2)} {cur}</p>", unsafe_allow_html=True)
        
        # 신호등 (글자 크기 60px 적용)
        if rsi > 70 or price > up_b:
            bg, status = "#28A745", "🟢 매도 검토"
        elif price < target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 기회"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 중립"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 25-26년 추정 적정가: {format(int(target), ',') if is_kr else round(target,2)} {cur}</div>", unsafe_allow_html=True)

        # 4대 지수 표 복구
        st.markdown("### 📊 실시간 4대 지수 분석")
        st.table(pd.DataFrame({
            "지표명": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
            "수치": [f"{round(up_b,1)} / {round(dn_b,1)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd,3)}"],
            "상태": ["과열" if price > up_b else "바닥" if price < dn_b else "정상", "주의" if rsi>70 else "바닥" if rsi<30 else "보통", "천장" if wr>-20 else "바닥" if wr<-80 else "보통", "상승" if macd>0 else "하락"]
        }))
