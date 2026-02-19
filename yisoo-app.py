import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (시인성 극대화 및 리포트 레이아웃)
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
    .analysis-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; margin-bottom: 10px; color: #334155 !important; font-weight: 600; }
    .fair-price-box { background-color: #1E3A8A; color: #FFFFFF !important; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: 900; margin-top: 20px; }
    .detail-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; margin-bottom: 12px; color: #1E3A8A !important; }
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

# 2. 메인 입력창
st.title("👴 이수할아버지의 주식분석기 v36000")
symbol = st.text_input("📊 종목코드(6자리) 또는 티커 입력", value="058610").strip().upper()

if symbol:
    try:
        # 데이터 로드 (충분한 기간)
        df = fdr.DataReader(symbol).tail(150)
        if not df.empty:
            stock_name = get_stock_name(symbol)
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            
            # --- [선생님 전용 지수 계산: 20/2, 14/6, 14/9] ---
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2)); lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_m = 100 - (100 / (1 + (gain / loss))); rsi_v = float(rsi_m.iloc[-1]); rsi_s = float(rsi_m.rolling(6).mean().iloc[-1])
            
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr_m = ((h14 - df['close']) / (h14 - l14)) * -100; wr_v = float(wr_m.iloc[-1]); wr_s = float(wr_m.rolling(9).mean().iloc[-1])
            
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_v = float((exp12 - exp26).iloc[-1]); macd_s = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])

            # [3] 화면 출력: 신호등 및 현재가
            is_buy = (wr_v < -80 and wr_v > wr_s) or (rsi_v < 35 and rsi_v > rsi_s) or (curr_p <= lo_b)
            is_sell = (wr_v > -20 and wr_v < wr_s) or (rsi_v > 65 and rsi_v < rsi_s) or (curr_p >= up_b)
            sig_class = "buy" if is_buy else "sell" if is_sell else "wait"
            sig_text = "🔴 매수 적기" if is_buy else "🟢 매도 검토" if is_sell else "🟡 관망 유지"
            
            st.markdown(f"<div class='signal-box {sig_class}'>{sig_text}</div>", unsafe_allow_html=True)
            p_val = f"${curr_p:,.2f}" if not symbol.isdigit() else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {p_val}</div></div>", unsafe_allow_html=True)

            # [4] 종합 분석 리포트 박스 (image_001b70 스타일)
            st.markdown(f"""<div class='report-main-box'>
                <h3 style='margin-top:0;'>🔍 이수할아버지 종합 분석</h3>
                <div style='font-size:18px; margin-bottom:10px;'>📈 <b>수급 추세:</b> {'상승 돌파 시도 중' if wr_v > wr_s else '하락 압력 우세'} (시그널 확인)</div>
                <div style='font-size:18px; margin-bottom:10px;'>⚖️ <b>투자 심리:</b> {'심리 회복세' if rsi_v > rsi_s else '심리 위축세'} (시그널 확인)</div>
                <div style='font-size:18px;'>💎 <b>최종 결론:</b> {sig_text} 전략이 유효합니다.</div>
            </div>""", unsafe_allow_html=True)

            # [5] 지수 상세분석 섹션
            st.subheader("📊 지수 상세분석")
            st.markdown(f"""
            <div class='analysis-card'>
                <b>① 심리 지수 (RSI 14, 6):</b> 현재 지수 {rsi_v:.1f}가 시그널 {rsi_s:.1f}를 {'상향 돌파하며 심리가 개선 중' if rsi_v > rsi_s else '하회하며 심리가 위축 중'}입니다.
            </div>
            <div class='analysis-card'>
                <b>② 수급 지수 (Will %R 14, 9):</b> 현재 {wr_v:.1f} 수치로 볼 때 {'단기 자금이 유입' if wr_v > wr_s else '단기 자금이 이탈'}되는 국면입니다.
            </div>
            <div style='background-color:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:15px; color:#334
