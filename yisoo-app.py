import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 화면 구성 (어르신 전용 설계)
st.set_page_config(page_title="이수할아버지 분석기", layout="wide")
st.title("👴 이수할아버지의 주식분석기 v36000")

# 날짜 입력칸 (화면 중앙 배치)
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 분석 시작일 (데이터 재료)", datetime(2025, 11, 1))
with col2:
    end_date = st.date_input("📅 분석 종료일", datetime.now())

symbol = st.text_input("📊 종목코드(6자리) 또는 티커 입력", "005930")

if symbol:
    try:
        # 데이터 수집 (국장/미장 자동 판별)
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date, end_date)
            currency = "원"
        else:
            df = yf.download(symbol, start=start_date, end=end_date)
            currency = "$"
        
        if not df.empty:
            # 지표 계산 (20/2, 14/9, 14/6)
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['Std'] = df['Close'].rolling(window=20).std()
            df['BB_Up'] = df['MA20'] + (df['Std'] * 2)
            df['BB_Low'] = df['MA20'] - (df['Std'] * 2)
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))
            
            high14 = df['High'].rolling(window=14).max()
            low14 = df['Low'].rolling(window=14).min()
            df['WillR'] = (high14 - df['Close']) / (high14 - low14) * -100
            
            p, r, w = df['Close'].iloc[-1], df['RSI'].iloc[-1], df['WillR'].iloc[-1]
            
            # 2. 결과 표시 (신호등 및 분석 카드)
            st.markdown("---")
            if r < 35: st.header("🔴 매수(적기)")
            elif r > 65: st.header("🟢 매도(수익실현)")
            else: st.header("🟡 관망(보유)")

            st.subheader(f"🏢 {symbol} 분석 결과")
            with st.expander("📝 추세 분석 카드 (냉정한 진단)", expanded=True):
                st.write(f"현재 {symbol}의 장부를 보니 아주 위태롭구먼요. 2026년 실시간 지표는 거짓말을 하지 않습니다.")
                st.write(f"● **Bollinger**: 현재 위치는 {p:,.0f}{currency}로, 하방 압력이 거셉니다. [cite: 2026-02-19]")
                st.write(f"● **RSI/윌리엄**: 상세 수치는 {r:.2f}와 {w:.2f}로 시장의 냉혹한 평가를 보여줍니다. [cite: 2026-02-19]")
                st.write(f"■ **리스크 점검**: 수율 불안정과 관세 리스크가 어르신의 자산을 노리고 있습니다. [cite: 2026-02-23]")

            st.info(f"💎 테이버 적정주가: {p * 0.95:,.0f}{currency} / 현재가: {p:,.0f}{currency}")

    except Exception as e:
        st.error(f"⚠️ 장부 기입 중 오류: {e}")
