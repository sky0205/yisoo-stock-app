import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime

# 1. 환경 설정 및 이수 할아버지 양식
st.set_page_config(page_title="이수 할아버지의 냉정 진단기 v36056", layout="wide")

st.title("👴 이수 할아버지의 냉정 진단기 v36056")

# 2. 종목 입력
symbol = st.text_input("📊 종목번호 또는 티커 입력", value="005930")

if symbol:
    try:
        # 데이터 가져오기 (2026년 실시간 위주)
        df = fdr.DataReader(symbol)
        curr_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change = curr_price - prev_price
        
        # 지표 계산 (어르신 지정 기준: 20/2, 14/6, 14/9)
        # Bollinger
        ma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        upper_b = ma20 + (std20 * 2)
        lower_b = ma20 - (std20 * 2)
        
        # RSI (14/9)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_sig = rsi.rolling(window=9).mean()
        
        # Williams %R (14/6)
        high_14 = df['High'].rolling(window=14).max()
        low_14 = df['Low'].rolling(window=14).min()
        will_r = (high_14 - df['Close']) / (high_14 - low_14) * -100
        will_sig = will_r.rolling(window=6).mean()

        # 3. 상단 신호등 (냉정 진단 로직)
        st.subheader(f"📍 {symbol} 현재가: {curr_price:,.0f}원 / $")
        
        if rsi.iloc[-1] > 65 or will_r.iloc[-1] > -20:
            st.error("🟢 매도(수익실현 권고) - 불지옥/광기 진입")
        elif rsi.iloc[-1] < 35 or will_r.iloc[-1] < -80:
            st.success("🔴 매수(적기) - 개미항복 지점")
        else:
            st.warning("🟡 관망(보유) - 안개 정국")

        st.divider()

        # 4. 네 기둥 지수란 (냉정 진단 문구 적용)
        i1, i2, i3, i4 = st.columns(4)
        
        with i1:
            st.markdown("**Bollinger**")
            pos = "폭주" if curr_price >= upper_b.iloc[-1] else "추락" if curr_price <= lower_b.iloc[-1] else "중도"
            st.write(f"● 위치: {pos}")
            
        with i2:
            st.markdown("**RSI**")
            r_val = rsi.iloc[-1]
            r_status = "🔥 불지옥" if r_val > 65 else "🧊 빙하기" if r_val < 35 else "정상"
            st.write(f"● {r_val:.1f} ({r_status})")
            
        with i3:
            st.markdown("**Williams %R**")
            w_val = will_r.iloc[-1]
            w_status = "🧨 광기폭발" if w_val > -20 else "🏳️ 개미항복" if w_val < -80 else "보통"
            st.write(f"● {w_val:.1f} ({w_status})")
            
        with i4:
            st.markdown("**MACD**")
            # 단순 추세 표시
            st.write("● 추세: ▲ 상승" if change > 0 else "● 추세: ▼ 하락")

    except Exception as e:
        st.error(f"⚠️ 오류 발생: {e}")

# 하단 기능: 오늘 검색한 종목 나열 (단순 예시)
st.button("🔍 최근 검색 종목 보기")
