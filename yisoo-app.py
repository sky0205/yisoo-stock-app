import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# [1. 스타일 설정: 시인성 강화 및 적정가 박스 추가]
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 20px 20px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 30px; }
    .price-text { font-size: 38px; color: #1E3A8A !important; font-weight: 900; }
    .report-main-box { background-color: #F8FAFC; border: 3px solid #1E3A8A; padding: 25px; border-radius: 20px; margin-bottom: 20px; border-left: 15px solid #1E3A8A; color: #1E3A8A !important; }
    .analysis-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; margin-bottom: 10px; color: #334155 !important; }
    .fair-price-box { background-color: #1E3A8A; color: #FFFFFF !important; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: 900; margin-top: 20px; }
    h1, h2, h3 { color: #1E3A8A !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# [중략: get_stock_name 함수 및 기본 로직 동일]

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(150)
        if not df.empty:
            # 지수 계산 (20/2, 14/6, 14/9)
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2)); lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_m = 100 - (100 / (1 + (gain / loss))); rsi_v = float(rsi_m.iloc[-1]); rsi_s = float(rsi_m.rolling(6).mean().iloc[-1])
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr_m = ((h14 - df['close']) / (h14 - l14)) * -100; wr_v = float(wr_m.iloc[-1]); wr_s = float(wr_m.rolling(9).mean().iloc[-1])
            curr_p = float(df['close'].iloc[-1])

            # 1. 상단 신호/가격 출력
            is_buy = (wr_v < -80 and wr_v > wr_s) or (rsi_v < 35 and rsi_v > rsi_s) or (curr_p <= lo_b)
            is_sell = (wr_v > -20 and wr_v < wr_s) or (rsi_v > 65 and rsi_v < rsi_s) or (curr_p >= up_b)
            sig_text = "🔴 매수 적기" if is_buy else "🟢 매도 검토" if is_sell else "🟡 관망 유지"
            st.markdown(f"<div class='signal-box {'buy' if is_buy else 'sell' if is_sell else 'wait'}'>{sig_text}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {curr_p:,.0f}원</div></div>", unsafe_allow_html=True)

            # 2. 지수 상세분석 섹션 추가
            st.subheader("📊 지수 상세분석")
            st.markdown(f"""
            <div class='analysis-card'>
                <b>① 심리 지수 (RSI 14, 6):</b> 현재 지수 {rsi_v:.1f}가 시그널 {rsi_s:.1f}를 {'상향 돌파하며 심리가 개선 중' if rsi_v > rsi_s else '하회하며 심리가 위축 중'}입니다.
            </div>
            <div class='analysis-card'>
                <b>② 수급 지수 (Will %R 14, 9):</b> 현재 {wr_v:.1f} 수치로 볼 때 {'단기 자금이 유입' if wr_v > wr_s else '단기 자금이 이탈'}되는 국면입니다.
            </div>
            <div class='analysis-card'>
                <b>③ 변동성 (BB 20, 2):</b> 주가가 밴드 {'상단 부근' if curr_p > ma20.iloc[-1] else '하단 부근'}에 위치하여 {'조정' if curr_p > ma20.iloc[-1] else '반등'} 가능성이 높습니다.
            </div>
            """, unsafe_allow_html=True)

            # 3. 적정가 계산 및 출력 (밴드 중심 및 목표가 반영)
            fair_p = (up_b + lo_b) / 2 # 볼린저 중심선을 1차 적정가로 설정
            target_p = curr_p * 1.15 # 15% 목표가
            st.markdown(f"<div class='fair-price-box'>💎 예상 적정가 : {fair_p:,.0f}원 / 목표가 : {target_p:,.0f}원</div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"오류: {e}")
