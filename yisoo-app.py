import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (이수할아버지 정밀 분석 테마)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; font-size: 45px !important; font-weight: 900; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 4대 지표 상세 박스 스타일 */
    .indicator-card { background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 15px; padding: 25px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .indicator-title { font-size: 20px; color: #1E3A8A; font-weight: 900; margin-bottom: 8px; border-bottom: 2px solid #CBD5E1; padding-bottom: 5px; }
    .indicator-value { font-size: 24px; color: #1E293B; font-weight: 800; margin-bottom: 5px; }
    .indicator-desc { font-size: 18px; color: #475569; font-weight: 500; line-height: 1.5; }
    
    .trend-card { font-size: 22px; line-height: 1.6; color: #1E293B !important; padding: 25px; background: #F1F5F9; border-left: 15px solid #1E3A8A; border-radius: 12px; margin-bottom: 20px; }
    .value-card { font-size: 28px; font-weight: 900; color: #FFFFFF !important; padding: 25px; background: #1E3A8A; border-radius: 15px; text-align: center; margin-bottom: 30px; }
    
    h1, h2, h3 { color: #1E3A8A !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

def get_stock_name(symbol):
    try:
        if symbol.isdigit():
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text
        return symbol
    except: return symbol

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

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

            # [1] 기본 정보
            st.header(f"🏢 {stock_name} ({symbol})")
            price_txt = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.subheader(f"현재 시세: {price_txt}")

            # [2] 대형 신호등
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)

            # [3] 4대 핵심 지수 상세 박스 (설명 강화)
            st.write("### 📋 4대 핵심 지표 상세 분석")
            
            # 볼린저 밴드
            bb_msg = "주가가 밴드 하단을 이탈했습니다. 과매도 상태로 기술적 반등이 임박했습니다." if curr_p < lo_b else \
                     "주가가 밴드 상단을 돌파했습니다. 단기 과열로 조정 가능성이 큽니다." if curr_p > up_b else \
                     "밴드 내에서 안정적인 흐름을 보이고 있습니다."
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>① 볼린저 밴드 (변동성 지표)</div><div class='indicator-value'>수치: {lo_b:,.0f} ~ {up_b:,.0f}</div><div class='indicator-desc'>{bb_msg}</div></div>", unsafe_allow_html=True)

            # RSI
            rsi_msg = "RSI 35 미만: 시장이 공포에 질려 던지고 있습니다. 곧 저점이 형성됩니다." if rsi < 35 else \
                      "RSI 65 초과: 시장이 흥분 상태입니다. 추격 매수는 위험한 구간입니다." if rsi > 65 else \
                      "투자 심리가 치우치지 않은 평온한 상태입니다."
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>② RSI (투자 심리도)</div><div class='indicator-value'>현재 심리: {rsi:.1f}%</div><div class='indicator-desc'>{rsi_msg}</div></div>", unsafe_allow_html=True)

            # MACD
            macd_msg = "상승 골든크로스: 세력의 자금이 유입되며 추세가 위로 꺾였습니다." if macd > sig else \
                       "하락 데드크로스: 매수세가 약해지며 힘이 빠지고 있는 구간입니다."
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>③ MACD (추세 강도)</div><div class='indicator-value'>수치: {macd:.2f} (시그널 대비 {'우위' if macd > sig else '열세'})</div><div class='indicator-desc'>{macd_msg}</div></div>", unsafe_allow_html=True)

            # Williams %R
            wr_msg = "바닥권 탈출 대기: 에너지가 응축되어 튀어오를 준비를 하고 있습니다." if wr < -80 else \
                     "천장권 진입: 단기적으로 먹을 구간보다 떨어질 위험이 큽니다." if wr > -20 else \
                     "적당한 에너지를 유지하며 추세를 탐색 중입니다."
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>④ Williams %R (단기 수급)</div><div class='indicator-value'>에너지: {wr:.1f}</div><div class='indicator-desc'>{wr_msg}</div></div>", unsafe_allow_html=True)

            # [4] 최종 목표가
            fair_v = curr_p * 1.15
            target_txt = f"${fair_v:,.2f}" if is_us else f"{fair_v:,.0f}원"
            st.markdown(f"<div class='value-card'>💎 이수할아버지의 1차 목표가 제안: {target_txt}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류 발생! (에러: {e})")
