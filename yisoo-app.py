import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 환경 설정
st.set_page_config(page_title="이수 할배의 냉정 진단기 v36056", layout="wide")

# 상단 신호등 표시
def set_signal(rsi, will_r):
    if rsi > 65 or will_r > -20:
        return "🟢 매도(수익실현)", "지금 불지옥/광기 상태구먼! 당장 나오시게!", "error"
    elif rsi < 35 or will_r < -75:
        return "🔴 매수(적기)", "개미들 다 항복했으니 이제 슬슬 담아보시게.", "success"
    else:
        return "🟡 관망(보유)", "안개 정국이니 괜히 힘 빼지 마시게.", "warning"

st.markdown(f"<h1 style='color: #FF4B4B;'>👴 이수 할아버지의 냉정 진단기 v36056</h1>", unsafe_allow_html=True)

# 2. 종목 입력
symbol = st.text_input("📊 종목번호 또는 티커 입력", value="005930")

if symbol:
    try:
        df = fdr.DataReader(symbol)
        curr_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        volume = df['Volume'].iloc[-1]
        vol_change = ((volume - df['Volume'].iloc[-2]) / df['Volume'].iloc[-2]) * 100

        # 지표 계산 (20/2, 14/6, 14/9)
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

        # 3. 신호등 및 추세 분석 카드
        sig_title, sig_msg, sig_type = set_signal(rsi, will_r)
        
        if sig_type == "error": st.error(f"### {sig_title}")
        elif sig_type == "success": st.success(f"### {sig_title}")
        else: st.warning(f"### {sig_title}")
            
        st.info(f"**[추세 분석 카드]**\n\n{sig_msg} 현재 거래량은 전일 대비 {vol_change:.1f}% 변동 중이며, 장부상 흐름이 아주 정밀하게 관측되고 있구먼요.")

        st.divider()

        # 4. 네 기둥 지수란 (v36056 정밀 지표)
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
            st.markdown("### **Volume/MACD**")
            st.write(f"■ 거래량: {volume:,.0f}")
            st.write(f"■ 추세: {'▲ 상승' if curr_price > prev_price else '▼ 하락'}")

    except Exception as e:
        st.error(f"⚠️ 기계가 또 딴소리를 하네: {e}")
