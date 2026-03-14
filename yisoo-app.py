import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 환경 설정 및 어르신 전용 까칠한 양식
st.set_page_config(page_title="이수 할배의 냉정 진단기 v36056", layout="wide")

st.markdown(f"<h1 style='color: #FF4B4B;'>👴 이수 할아버지의 냉정 진단기 v36056</h1>", unsafe_allow_html=True)
st.info("📢 [냉정 진단 모드] RSI 65↑ 불지옥, 윌리엄 -75↓ 개미항복 - 정중하지만 까칠하게 보고드립니다.")

# 2. 종목 입력
symbol = st.text_input("📊 종목번호 또는 티커 입력", value="005930")

if symbol:
    try:
        # 2026년 실시간 위주 데이터
        df = fdr.DataReader(symbol)
        curr_price = df['Close'].iloc[-1]
        
        # 어르신 지정 지표 기준: 20/2, 14/6, 14/9
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

        # 3. 상단 신호등 (v36028 냉정 진단 로직)
        st.subheader(f"📍 {symbol} 현재가: {curr_price:,.0f}원 / $")
        
        if rsi > 65 or will_r > -20:
            st.error("🟢 매도(수익실현) - 지금 불지옥/광기 상태구먼! 당장 나오시게!")
        elif rsi < 35 or will_r < -75:
            st.success("🔴 매수(적기) - 개미들 다 항복했으니 이제 슬슬 담아보시게.")
        else:
            st.warning("🟡 관망(보유) - 안개 정국이니 괜히 힘 빼지 마시게.")

        st.divider()

        # 4. 네 기둥 지수란 (■ 기호 사용, 까칠한 진단 문구)
        i1, i2, i3, i4 = st.columns(4)
        
        with i1:
            st.markdown("### **Bollinger**")
            pos = "🔥 폭주" if curr_price >= upper_b.iloc[-1] else "📉 추락" if curr_price <= lower_b.iloc[-1] else "⚖️ 중도"
            st.write(f"■ 위치: {pos}")
            
        with i2:
            st.markdown("### **RSI**")
            r_stat = "👺 불지옥" if rsi > 65 else "🧊 빙하기" if rsi < 35 else "정상"
            st.write(f"■ 수치: {rsi:.1f} ({r_stat})")
            
        with i3:
            st.markdown("### **Williams %R**")
            w_stat = "🧨 광기폭발" if will_r > -20 else "🏳️ 개미항복" if will_r < -75 else "보통"
            st.write(f"■ 수치: {will_r:.1f} ({w_stat})")
            
        with i4:
            st.markdown("### **MACD**")
            change = df['Close'].diff().iloc[-1]
            st.write(f"■ 추세: {'▲ 상승' if change > 0 else '▼ 하락'}")

    except Exception as e:
        st.error(f"⚠️ 기계가 또 딴소리를 하네: {e}")
