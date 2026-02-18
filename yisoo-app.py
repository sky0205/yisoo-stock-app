import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; font-size: 45px !important; font-weight: 900; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 지표 및 분석 카드 스타일 */
    .indicator-card { background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 15px; padding: 25px; margin-bottom: 15px; }
    .indicator-title { font-size: 20px; color: #1E3A8A; font-weight: 900; margin-bottom: 8px; border-bottom: 2px solid #CBD5E1; padding-bottom: 5px; }
    .indicator-value { font-size: 24px; color: #1E293B; font-weight: 800; }
    .indicator-desc { font-size: 18px; color: #475569; line-height: 1.5; }
    
    /* 종합 추세 분석 전용 스타일 */
    .trend-report { background: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 30px; border-radius: 15px; margin-top: 20px; margin-bottom: 20px; }
    .trend-title { font-size: 26px; font-weight: 900; color: #1E3A8A; margin-bottom: 15px; }
    .trend-item { font-size: 20px; color: #334155; margin-bottom: 10px; line-height: 1.6; }
    
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

            # [1] 기본 정보 및 신호등
            st.header(f"🏢 {stock_name} ({symbol})")
            price_txt = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)

            # [2] 종합 추세 분석 리포트 (선생님 요청 사항)
            st.markdown("<div class='trend-report'>", unsafe_allow_html=True)
            st.markdown("<div class='trend-title'>🔍 이수할아버지의 종합 추세 분석</div>", unsafe_allow_html=True)
            
            # 종합 분석 로직
            trend_score = 0
            if macd > sig: trend_score += 1
            if curr_p > ma20.iloc[-1]: trend_score += 1
            
            if trend_score == 2: trend_summary = "현재 강한 상승 엔진이 가동 중입니다. 조정 시 매수 관점이 유효합니다."
            elif trend_score == 1: trend_summary = "추세가 전환되려는 변곡점에 있습니다. 신중한 접근이 필요합니다."
            else: trend_summary = "전반적으로 하방 압력이 강합니다. 바닥 확인 전까지는 보수적으로 대응하십시오."
            
            st.markdown(f"<div class='trend-item'><b>📈 추세 방향:</b> {trend_summary}</div>", unsafe_allow_html=True)
            
            # 보조지표 종합 코멘트
            vol_msg = "밴드가 좁아지며 큰 변동성을 준비 중입니다." if (up_b - lo_b) / ma20.iloc[-1] < 0.1 else "현재 변동성이 충분히 확보된 상태입니다."
            st.markdown(f"<div class='trend-item'><b>⚖️ 변동성 상태:</b> {vol_msg}</div>", unsafe_allow_html=True)
            
            psych_msg = "시장이 과열되어 차익 실현 매물이 나올 수 있습니다." if rsi > 65 else "공포 심리가 우세하여 저가 매수세 유입이 기대됩니다." if rsi < 35 else "투자자들의 심리가 매우 안정적입니다."
            st.markdown(f"<div class='trend-item'><b>심리 지수:</b> {psych_msg}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # [3] 4대 핵심 지수 박스
            st.write("### 📋 4대 핵심 지표 상세 수치")
            col1, col2 = st.columns(2); col3, col4 = st.columns(2)
            with col1: st.markdown(f"<div class='indicator-card'><div class='indicator-title'>볼린저 밴드</div><div class='indicator-value'>{lo_b:,.0f} ~ {up_b:,.0f}</div></div>", unsafe_allow_html=True)
            with col2: st.markdown(f"<div class='indicator-card'><div class='indicator-title'>RSI 심리도</div><div class='indicator-value'>{rsi:.1f}%</div></div>", unsafe_allow_html=True)
            with col3: st.markdown(f"<div class='indicator-card'><div class='indicator-title'>MACD 추세</div><div class='indicator-value'>{'상승 우위' if macd > sig else '하락 우위'}</div></div>", unsafe_allow_html=True)
            with col4: st.markdown(f"<div class='indicator-card'><div class='indicator-title'>Williams %R</div><div class='indicator-value'>{wr:.1f}</div></div>", unsafe_allow_html=True)

            # [4] 목표가
            fair_v = curr_p * 1.15
            target_txt = f"${fair_v:,.2f}" if is_us else f"{fair_v:,.0f}원"
            st.markdown(f"<div class='value-card'>💎 이수할아버지의 1차 목표가 제안: {target_txt}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류 발생! 티커를 확인해 주세요. ({e})")
