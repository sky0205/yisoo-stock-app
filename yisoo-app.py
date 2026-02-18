import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (이수할아버지 전용 테마)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* 신호등 스타일 */
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; font-size: 45px !important; font-weight: 900; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 4대 지표 박스 스타일 */
    .indicator-card { background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .indicator-title { font-size: 18px; color: #64748B; font-weight: bold; margin-bottom: 5px; }
    .indicator-value { font-size: 26px; color: #1E3A8A; font-weight: 900; }
    
    /* 분석 리포트 카드 */
    .trend-card { font-size: 22px; line-height: 1.6; color: #1E293B !important; padding: 25px; background: #F1F5F9; border-left: 15px solid #1E3A8A; border-radius: 12px; margin-bottom: 20px; }
    .value-card { font-size: 28px; font-weight: 900; color: #FFFFFF !important; padding: 25px; background: #1E3A8A; border-radius: 15px; text-align: center; margin-bottom: 30px; }
    
    h1, h2, h3 { color: #1E3A8A !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# 종목명 가져오기 함수
def get_stock_name(symbol):
    try:
        if symbol.isdigit():
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text
        return symbol
    except:
        return symbol

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

# 제목 변경 적용
st.title("👴 이수할아버지의 주식분석기 v36000")

symbol = st.text_input("📊 종목코드(6자리) 또는 미장 티커 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            stock_name = get_stock_name(symbol)
            if symbol in st.session_state['history']: st.session_state['history'].remove(symbol)
            st.session_state['history'].insert(0, symbol)
            st.session_state['target'] = symbol
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()

            # 지표 계산
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = float((exp12 - exp26).iloc[-1]); sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr = float(((h14.iloc[-1] - curr_p) / (h14.iloc[-1] - l14.iloc[-1])) * -100)

            # [1] 종목명 및 현재가
            st.header(f"🏢 {stock_name} ({symbol})")
            price_txt = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.subheader(f"현재 시세: {price_txt}")

            # [2] 대형 신호등
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)

            # [3] 4대 핵심 지수 박스 정리
            st.write("### 📋 4대 핵심 지표 박스")
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            
            with col1:
                st.markdown(f"<div class='indicator-card'><div class='indicator-title'>볼린저 밴드</div><div class='indicator-value'>{'하단 지지' if curr_p < lo_b else '상단 저항' if curr_p > up_b else '안정권'}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='indicator-card'><div class='indicator-title'>RSI 심리도</div><div class='indicator-value'>{rsi:.1f} ({'공포' if rsi < 35 else '탐욕' if rsi > 65 else '정상'})</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='indicator-card'><div class='indicator-title'>MACD 추세</div><div class='indicator-value'>{'상승 전환' if macd > sig else '하락 압력'}</div></div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='indicator-card'><div class='indicator-title'>Williams %R</div><div class='indicator-value'>{wr:.1f} ({'바닥' if wr < -80 else '고점' if wr > -20 else '중간'})</div></div>", unsafe_allow_html=True)

            # [4] 상세 현상 분석
            st.write("### 🔍 이수할아버지의 정밀 분석")
            analysis = []
            if rsi < 35: analysis.append("현재 시장 참여자들이 겁을 먹고 던지는 '과매도' 상태입니다. 심리적 저점에 가깝습니다.")
            if curr_p < lo_b: analysis.append("주가가 통계적 하한선을 이탈했습니다. 특별한 악재가 없다면 기술적 반등이 나올 자리입니다.")
            if macd > sig: analysis.append("차트상의 에너지가 위로 향하기 시작했습니다. 단기 매수세가 유입되고 있습니다.")
            if not analysis: analysis.append("현재 주가는 큰 파도 없이 잔잔한 흐름입니다. 방향성이 결정될 때까지 기다림이 필요합니다.")
            
            st.markdown(f"<div class='trend-card'><b>📋 현 상황 진단:</b> {' '.join(analysis)}</div>", unsafe_allow_html=True)

            # [5] 1차 목표가
            fair_v = curr_p * 1.15
            target_txt = f"${fair_v:,.2f}" if is_us else f"{fair_v:,.0f}원"
            st.markdown(f"<div class='value-card'>💎 1차 목표가 제안: {target_txt}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다. 코드 번호를 확인해 주세요! (에러: {e})")
