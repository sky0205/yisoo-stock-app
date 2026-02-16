import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import time

# 1. 화면 스타일 및 신호등 설정
st.set_page_config(page_title="이수 주식 마스터 v240", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .traffic-light { padding: 30px; border-radius: 20px; text-align: center; font-size: 35px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { border-color: #E63946; background-color: #FEE2E2; color: #E63946; }
    .wait { border-color: #F59E0B; background-color: #FEF3C7; color: #92400E; }
    .sell { border-color: #10B981; background-color: #D1FAE5; color: #065F46; }
    .stock-header { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 통합 매매 분석기")

# 2. 데이터 가져오기 엔진 (IP 차단 방지)
@st.cache_data(ttl=600)
def get_data(t):
    try:
        time.sleep(1)
        df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        if df.empty: return None
        # yfinance 데이터 구조 정리
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except: return None

# 3. 입력창
t_input = st.text_input("📊 분석할 종목코드를 입력하세요 (예: 005930.KS, NVDA, IONQ)", value="005930.KS").strip().upper()

if t_input:
    df = get_data(t_input)
    if df is not None:
        df = df.reset_index()
        
        # 4. 지표 계산 (RSI, Williams %R, MACD)
        # RSI
        diff = df['close'].diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        # Williams %R
        h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
        # MACD
        df['e12'] = df['close'].ewm(span=12).mean(); df['e26'] = df['close'].ewm(span=26).mean()
        macd = (df['e12'] - df['e26']).iloc[-1]; sig = (df['e12'] - df['e26']).ewm(span=9).mean().iloc[-1]

        # 5. [출력 1] 종목명 및 신호등
        st.markdown(f"<div class='stock-header'>🏷️ 종목: {t_input}</div>", unsafe_allow_html=True)
        
        # 사정권 로직 포함
        is_target = (t_input == "IONQ" and df['close'].iloc[-1] <= 30) or (t_input == "NVDA" and df['close'].iloc[-1] <= 170)
        
        if rsi < 35 or wr < -80 or is_target:
            msg = "🔴 사정권 진입! 적극 매수" if is_target else "🔴 매수 신호 발생"
            st.markdown(f"<div class='traffic-light buy'>{msg}</div>", unsafe_allow_html=True)
        elif rsi > 65 or wr > -20:
            st.markdown(f"<div class='traffic-light sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='traffic-light wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

        # 6. [출력 2] 4대 지표 상세 표 (유한양행 분석 양식 반영)
        st.write("### 📋 핵심 지표 정밀 진단")
        summary_data = {
            "지표 항목": ["현재가", "RSI (강도)", "Williams %R", "MACD (추세)"],
            "수치": [f"{df['close'].iloc[-1]:,.2f}", f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd > sig else "하락"],
            "판단": ["-", "바닥권" if rsi < 30 else "고점권" if rsi > 70 else "보통", "매수적기" if wr < -80 else "보통", "골든크로스" if macd > sig else "데드크로스"]
        }
        st.table(pd.DataFrame(summary_data))

        # 7. [출력 3] 주가 그래프
        st.write("### 📈 주가 추세 차트")
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x='date:T', y=alt.Y('close:Q', scale=alt.Scale(zero=False))
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("데이터를 가져오지 못했습니다. 종목코드를 확인해 주세요 (예: 삼성전자는 005930.KS)")
