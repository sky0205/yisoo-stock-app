import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (어르신 전용 고대비 및 가독성 최적화)
st.set_page_config(page_title="이수할아버지 분석기", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .stock-name { font-size: 35px !important; color: #1565C0 !important; margin: 0; }
    .stock-price { font-size: 38px !important; color: #D32F2F !important; margin: 0; }
    .signal-box { padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .signal-text { font-size: 55px !important; color: #FFFFFF !important; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .val-main { font-size: 32px !important; line-height: 1.1; color: #333; }
    .trend-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 4px solid #1565C0; margin: 15px 0; }
    .ind-box { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 2px solid #90A4AE; min-height: 400px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👴 이수할아버지의 냉정 진단기 v36042")
symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency = "원"; fmt = ",.0f" # 국장은 정수
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol)
            currency = "$"; fmt = ",.2f" # [수선] 미장은 소수점 두 자리
        
        if not df.empty:
            p = df['Close'].iloc[-1]; peak_p = df['Close'].iloc[-20:].max(); defense_line = peak_p * 0.93
            fair_price = p * 0.90; target_price = p * 1.15

            # 1. 상단 정보 (소수점 적용)
            st.markdown(f"<div class='stock-header'><p class='stock-name'>{name} ({symbol})</p><p class='stock-price'>{format(p, fmt)} {currency}</p></div>", unsafe_allow_html=True)

            # 2. 가격 전략 카드 (소수점 적용)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 적정가</p><p class='val-main' style='color:#388E3C;'>{format(fair_price, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 목표가</p><p class='val-main' style='color:#D32F2F;'>{format(target_price, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            # ... (이하 전황 및 지수란 로직 동일)
            st.info("어르신, 소수점 두 자리까지 정밀하게 수선했습니다.")

    except Exception as e: st.error(f"오류: {e}")
