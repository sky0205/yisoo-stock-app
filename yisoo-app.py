import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 환경 설정 및 어르신 전용 스타일
st.set_page_config(page_title="이수 할배의 냉정 진단기 v36056", layout="wide")

st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>👴 이수 할아버지의 냉정 진단기 v36056</h1>", unsafe_allow_html=True)

# 2. 종목 입력
symbol = st.text_input("📊 종목번호 또는 티커 입력 (예: 005930, NVDA)", value="005930")

if symbol:
    try:
        # 데이터 호출 (2026년 실시간 반영)
        df = fdr.DataReader(symbol)
        curr_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        high_price = df['High'].iloc[-1]
        low_price = df['Low'].iloc[-1]
        volume = df['Volume'].iloc[-1]
        vol_prev = df['Volume'].iloc[-2]
        vol_change = ((volume - vol_prev) / vol_prev) * 100
        
        # 지표 계산 (어르신 기준: 20/2, 14/6, 14/9)
        ma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        upper_b = ma20 + (std20 * 2)
        lower_b = ma20 - (std20 * 2)
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        high_14 = df['High'].rolling(window=14).max()
        low_14 = df['Low'].rolling(window=14).min()
        will_r = ((high_14 - df['Close']) / (high_14 - low_14) * -100).iloc[-1]

        # [복구 1] 종목명 및 현재가 정보 (성벽 가격 포함)
        st.markdown(f"### 🏢 종목: {symbol} | 현재가: {curr_price:,.0f}원/$")
        c1, c2 = st.columns(2)
        with c1:
            st.success(f"🏰 상단 성벽(저항): {upper_b.iloc[-1]:,.0f}")
        with c2:
            st.error(f"🛡️ 하단 성벽(지지): {lower_b.iloc[-1]:,.0f}")

        # [복구 2] 상단 신호등
        if rsi > 65 or will_r > -20:
            st.error("🟢 매도(수익실현 적기) - 불지옥/광기 진입!")
        elif rsi < 35 or will_r < -75:
            st.success("🔴 매수(진입 적기) - 개미항복 지점!")
        else:
            st.warning("🟡 관망(보유 유지) - 안개 정국")

        # [보완] 추세 분석 카드 및 실대응 방안
        st.info(f"""
        **[🕵️ 이수 할배의 추세 분석 및 실대응]**
        * **현재 흐름:** 거래량이 전일 대비 {vol_change:.1f}% 변동하며 {'기세가 살아나고' if vol_change > 0 else '숨을 죽이고'} 있구먼요.
        * **실대응 방안:** - { 'RSI가 높으니 욕심 버리고 분할 매도 시작하시게.' if rsi > 60 else '지표가 바닥이니 공포를 이기고 조금씩 담아볼 때야.' if rsi < 40 else '지금은 관망하며 성벽(지지선) 깨지는지 확인이 우선일세.' }
            - 특히 윌리엄 지수가 {will_r:.1f}이니 {'뇌동매매 금지!' if will_r > -20 else '조금 더 기다려보시게.'}
        """)

        # [복구 3] 네 기둥 상세 분석 및 거래량표
        st.divider()
        i1, i2, i3, i4 = st.columns(4)
        with i1:
            st.markdown("#### **Bollinger**")
            pos = "🔥 폭주" if curr_price >= upper_b.iloc[-1] else "📉 추락" if curr_price <= lower_b.iloc[-1] else "⚖️ 중도"
            st.write(f"■ 위치: {pos}")
            st.caption(f"상단: {upper_b.iloc[-1]:,.0f}\n하단: {lower_b.iloc[-1]:,.0f}")
        with i2:
            st.markdown("#### **RSI (14/9)**")
            r_stat = "👺 불지옥" if rsi > 65 else "🧊 빙하기" if rsi < 35 else "정상"
            st.write(f"■ 수치: {rsi:.1f} ({r_stat})")
            st.caption("65↑ 과열 / 35↓ 과매도")
        with i3:
            st.markdown("#### **William %R**")
            w_stat = "🧨 광기폭발" if will_r > -20 else "🏳️ 개미항복" if will_r < -75 else "보통"
            st.write(f"■ 수치: {will_r:.1f} ({w_stat})")
            st.caption("-20↑ 과매수 / -75↓ 매수적기")
        with i4:
            st.markdown("#### **Volume/MACD**")
            st.write(f"■ 거래량: {volume:,.0f}")
            st.write(f"■ 추세: {'▲ 상승' if curr_price > prev_price else '▼ 하락'}")
            st.caption(f"전일비: {vol_change:+.1f}%")

    except Exception as e:
        st.error(f"⚠️ 아이구, 기계가 또 헛소리를 하네: {e}")
