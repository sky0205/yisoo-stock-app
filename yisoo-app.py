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
    /* 요약 박스: 글자색을 검정색(#000000)으로 강제 고정 */
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #000000 !important; }
    .summary-box b { color: #000000 !important; font-weight: 800; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 지능형 데이터 엔진 (9% 고정 및 에러 방지) ---
@st.cache_data(ttl=3600)
def fetch_refined_info(user_input):
    try:
        is_kr = bool(re.match(r'^\d{6}$', user_input))
        y_ticker = user_input + (".KS" if is_kr else "")
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # 이름 검색 (국장은 네이버, 미장은 야후)
        if is_kr:
            url = f"https://finance.naver.com/item/main.naver?code={user_input}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
        else:
            name = info.get('shortName') or info.get('longName') or user_input

        # AI 적정주가 (S-RIM 9% 기준)
        r = 0.09 # 요구수익률 9% 고정
        bps = info.get('bookValue') or (info.get('currentPrice', 1) / info.get('priceToBook', 1))
        roe = info.get('returnOnEquity') or 0.10
        
        if roe > 1: roe = roe / 100 # ROE 단위 보정
        
        target_val = float(bps * (roe / r)) if bps > 0 else 0.0
        
        # [중요] 1원/0원 방지 로직: 적정가가 너무 낮으면 현재가의 80%를 가이드라인으로 설정
        curr_p = info.get('currentPrice') or info.get('previousClose') or 1.0
        if target_val < curr_p * 0.5: target_val = curr_p * 0.8
            
        return {"name": name, "target": target_val, "ticker": y_ticker, "is_kr": is_kr, "curr": curr_p}
    except:
        return None

# --- [2] 메인 화면 및 입력부 ---
st.title("🏆 이수할아버지 v36000 AI 마스터")

t_input = st.text_input("🔢 종목코드(6자리) 또는 미장티커를 입력하세요", value="005930")
ai_data = fetch_refined_info(t_input)

if ai_data:
    c1, c2 = st.columns(2)
    with c1: st.text_input("📍 분석 종목명", value=ai_data['name'], disabled=True)
    with c2: in_target = st.number_input("💎 AI 산출 적정주가 (r=9%)", value=ai_data['target'], step=0.1)
    
    if st.button("🚀 실시간 4대 지표 통합 분석 시작"):
        # 기술적 데이터 호출
        df = yf.download(ai_data['ticker'], period="6mo", interval="1d", progress=False)
        if df.empty and ai_data['is_kr']: 
            df = yf.download(t_input + ".KQ", period="6mo", interval="1d", progress=False)

        if not df.empty:
            # [ValueError 해결] 모든 지표를 스칼라(Scalar) 숫자로 변환
            close = df['Close']
            price = float(close.iloc[-1])
            ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
            up_band = float((ma20 + std * 2).iloc[-1])
            dn_band = float((ma20 - std * 2).iloc[-1])
            
            # RSI
            delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = float((100 - (100 / (1 + (g/l)))).iloc[-1])
            
            # Williams %R
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            wr = float(((h14 - close) / (h14 - l14) * -100).iloc[-1])
            
            # MACD
            exp1 = close.ewm(span=12, adjust=False).mean(); exp2 = close.ewm(span=26, adjust=False).mean()
            macd_val = float((exp1 - exp2).iloc[-1])

            st.markdown("---")
            cur = "원" if ai_data['is_kr'] else "$"
            f_p = f"{format(int(price), ',')} {cur}" if ai_data['is_kr'] else f"{cur}{price:,.2f}"
            f_tg = f"{format(int(in_target), ',')} {cur}" if ai_data['is_kr'] else f"{cur}{in_target:,.2f}"

            # 결과 헤더
            st.markdown(f"<p class='big-price'>🔍 {ai_data['name']} 현재가: {f_p}</p>", unsafe_allow_html=True)
            
            # 신호등 로직 (이제 ValueError가 발생하지 않습니다)
            if rsi > 70 or price > up_band:
                bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
            elif price < in_target * 0.95:
                bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
            else:
                bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
            
            st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='target-box'>💎 적정주가 기준: {f_tg}</div>", unsafe_allow_html=True)

            # 요약 (검정 글씨 고정)
            st.markdown("### 📝 AI 추세 분석 요약")
            sum_msg = "상승 에너지가 강해 밴드 상단을 넘보고 있습니다." if price > up_band else "바닥 지지력을 테스트 중입니다."
            st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {ai_data['name']}은(는) {sum_msg}<br>RSI {round(rsi,1)}는 {'과열 상태' if rsi>70 else '바닥 구간' if rsi<35 else '안정권'}입니다.</div>", unsafe_allow_html=True)

            # 4대 지표 상세 표
            st.table(pd.DataFrame({
                "4대 핵심 지표": ["볼린저 밴드", "RSI (심리)", "Williams %R", "MACD Osc"],
                "실시간 수치": [f"{round(up_band,2)} / {round(dn_band,2)}", f"{round(rsi,1)}", f"{round(wr,1)}", f"{round(macd_val,3)}"],
                "진단": ["상단 돌파(주의)" if price > up_band else "하단 지입(기회)" if price < dn_band else "정상", "심리 과열" if rsi>70 else "심리 바닥" if rsi<30 else "보통", "단기천장" if wr>-20 else "단기바닥" if wr<-80 else "보통", "상승세" if macd_val>0 else "하락세"]
            }))
        else:
            st.error("데이터 로딩 실패! 코드를 확인해 주세요.")
else:
    st.info("종목 코드를 입력하면 AI가 가장 정확한 공식을 찾아 분석을 시작합니다.")
