import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (4대 지수 분석 시인성 극대화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .name-box { background-color: #1E3A8A; color: #FFFFFF !important; padding: 15px; text-align: center; font-size: 28px; font-weight: 900; border-radius: 15px 15px 0px 0px; margin-bottom: -10px; }
    .signal-box { padding: 25px; border-radius: 0px 0px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 30px; }
    .price-text { font-size: 38px; color: #1E3A8A !important; font-weight: 900; }
    
    .analysis-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; margin-bottom: 12px; color: #334155 !important; font-weight: 600; line-height: 1.6; border-left: 10px solid #1E3A8A; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .trend-box { background-color: #F8FAFC; border: 2px dashed #1E3A8A; padding: 15px; border-radius: 12px; margin-bottom: 20px; color: #1E3A8A !important; font-weight: 700; }
    
    .fair-price-box { background-color: #1E3A8A; color: #FFFFFF !important; padding: 25px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: 900; margin-top: 20px; }
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

st.title("👴 이수할아버지의 주식분석기 v36000")
target_symbol = st.text_input("📊 종목코드(6자리) 또는 티커 입력", value="058610").strip().upper()

if target_symbol:
    try:
        df = fdr.DataReader(target_symbol).tail(150)
        if not df.empty:
            stock_name = get_stock_name(target_symbol)
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not target_symbol.isdigit()
            
            # --- [데이터 계산] ---
            # 1. 이동평균선
            ma5 = df['close'].rolling(5).mean().iloc[-1]
            ma20 = df['close'].rolling(20).mean().iloc[-1]
            ma60 = df['close'].rolling(60).mean().iloc[-1]
            # 2. 볼린저 밴드
            std20 = df['close'].rolling(20).std().iloc[-1]
            up_b = float(ma20 + (std20 * 2)); lo_b = float(ma20 - (std20 * 2))
            # 3. RSI (14, 6)
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_m = 100 - (100 / (1 + (gain / loss))); rsi_v = float(rsi_m.iloc[-1]); rsi_s = float(rsi_m.rolling(6).mean().iloc[-1])
            # 4. Will %R (14, 9)
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr_m = ((h14 - df['close']) / (h14 - l14)) * -100; wr_v = float(wr_m.iloc[-1]); wr_s = float(wr_m.rolling(9).mean().iloc[-1])
            # 5. MACD (12, 26, 9)
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_v = float((exp12 - exp26).iloc[-1]); macd_s = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])

            # [1] 상단 신호 정보
            st.markdown(f"<div class='name-box'>🏢 {stock_name} ({target_symbol})</div>", unsafe_allow_html=True)
            is_buy = (wr_v < -80 and wr_v > wr_s) or (rsi_v < 35 and rsi_v > rsi_s) or (curr_p <= lo_b)
            is_sell = (wr_v > -20 and wr_v < wr_s) or (rsi_v > 65 and rsi_v < rsi_s) or (curr_p >= up_b)
            sig_class = "buy" if is_buy else "sell" if is_sell else "wait"
            sig_text = "🔴 매수 적기" if is_buy else "🟢 매도 검토" if is_sell else "🟡 관망 유지"
            st.markdown(f"<div class='signal-box {sig_class}'>{sig_text}</div>", unsafe_allow_html=True)
            curr_val = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {curr_val}</div></div>", unsafe_allow_html=True)

            # [2] 📈 추세 상세분석
            st.subheader("📈 추세 상세분석")
            trend_status = "정배열 (상승 추세)" if ma5 > ma20 > ma60 else "역배열 (하락 추세)" if ma5 < ma20 < ma60 else "혼조세 (횡보 구간)"
            st.markdown(f"<div class='trend-box'>🚩 현재 추세 : {trend_status}<br>📏 위치 : 5일선 대비 {((curr_p/ma5-1)*100):.1f}% {'상회' if curr_p > ma5 else '하회'}</div>", unsafe_allow_html=True)

            # [3] 📊 4대 핵심 지수 상세분석
            st.subheader("📊 4대 핵심 지수 상세분석")
            st.markdown(f"""
            <div class='analysis-card'><b>① 심리 (RSI 14, 6):</b> {rsi_v:.1f} (시그널 {rsi_s:.1f}) - {'심리 개선 중' if rsi_v > rsi_s else '심리 위축 중'}입니다.</div>
            <div class='analysis-card'><b>② 수급 (Will %R 14, 9):</b> {wr_v:.1f} (시그널 {wr_s:.1f}) - {'자금 유입 중' if wr_v > wr_s else '자금 이탈 중'}입니다.</div>
            <div class='analysis-card'><b>③ 변동성 (BB 20, 2):</b> 밴드 범위 {lo_b:,.1f} ~ {up_b:,.1f} 사이 {'하단 지지력' if curr_p < ma20 else '상단 저항력'} 테스트 중입니다.</div>
            <div class='analysis-card'><b>④ 추세 강도 (MACD):</b> {macd_v:.2f} (시그널 {macd_s:.2f}) - {'상승 에너지 강화 (골든크로스)' if macd_v > macd_s else '하락 압력 지속 (데드크로스)'} 구간입니다.</div>
            """, unsafe_allow_html=True)

            # [4] 적정가 및 목표가
            fair_p = (up_b + lo_b) / 2; target_p = curr_p * 1.15
            f_txt = f"${fair_p:,.2f}" if is_us else f"{fair_p:,.0f}원"; t_txt = f"${target_p:,.2f}" if is_us else f"{target_p:,.0f}원"
            st.markdown(f"<div class='fair-price-box'>💎 예상 적정가 : {f_txt} / 목표가 : {t_txt}</div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"데이터 분석 오류: {e}")
