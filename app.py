import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import time

# 1. 화면 스타일 (시력 보호 및 고대비)
st.set_page_config(page_title="이수 주식 v230", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .traffic-light { padding: 40px; border-radius: 25px; text-align: center; font-size: 45px; font-weight: bold; border: 12px solid; margin-bottom: 25px; }
    .buy { border-color: #E63946; background-color: #FEE2E2; color: #E63946; }
    .wait { border-color: #F59E0B; background-color: #FEF3C7; color: #92400E; }
    .sell { border-color: #10B981; background-color: #D1FAE5; color: #065F46; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 마스터 분석기 v230")

# 2. 검색 기록 기능
if 'history' not in st.session_state: st.session_state.history = []
with st.sidebar:
    st.header("📜 검색 기록")
    if st.button("기록 삭제"): st.session_state.history = []
    for h in reversed(st.session_state.history):
        if st.button(f"🔍 {h}", use_container_width=True): st.session_state.t_input = h

# 3. 입력창 (삼성전자는 005930.KS)
t_input = st.text_input("📊 종목코드 (삼성전자: 005930.KS, 아이온큐: IONQ)", 
                       value=st.session_state.get('t_input', '005930.KS')).strip().upper()

# 4. 데이터 엔진 (차단 방지용)
@st.cache_data(ttl=600)
def get_stock_data(t):
    try:
        time.sleep(1) # IP 차단 방지
        df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        return df if not df.empty else None
    except: return None

if t_input:
    df = get_stock_data(t_input)
    if df is not None:
        df = df.reset_index()
        df.columns = [str(c).lower().strip() for c in df.columns]
        if t_input not in st.session_state.history:
            st.session_state.history.append(t_input)

        # 5. 4대 지표 계산
        diff = df['close'].diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
        df['e12'] = df['close'].ewm(span=12).mean(); df['e26'] = df['close'].ewm(span=26).mean()
        macd = (df['e12'] - df['e26']).iloc[-1]; sig = (df['e12'] - df['e26']).ewm(span=9).mean().iloc[-1]

        # 6. 신호등 출력
        st.write("---")
        if rsi < 35 or wr < -80:
            st.markdown(f"<div class='traffic-light buy'>🔴 {t_input} : 적극 매수 구간</div>", unsafe_allow_html=True)
        elif rsi > 65 or wr > -20:
            st.markdown(f"<div class='traffic-light sell'>🟢 {t_input} : 매도 검토 구간</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='traffic-light wait'>🟡 {t_input} : 관망 및 대기</div>", unsafe_allow_html=True)

        # 7. 기술적 분석 요약 (유한양행 양식)
        summary = pd.DataFrame({
            "항목": ["현재가", "RSI 지수", "Williams %R", "MACD 추세"],
            "수치": [f"{df['close'].iloc[-1]:,.2f}", f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd > sig else "하락"],
            "진단": ["-" , "저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "골든크로스" if macd > sig else "데드크로스"]
        })
        st.table(summary)

        # 8. 차트
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(x='date:T', y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        st.altair_chart(chart, use_container_width=True)
