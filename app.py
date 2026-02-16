import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import altair as alt
import time

# 1. 화면 스타일 (고대비 및 시력 보호)
st.set_page_config(page_title="이수 주식 v450", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .traffic-light { padding: 30px; border-radius: 20px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; color: black; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    .stock-label { font-size: 28px; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 '불사조' 통합 분석기")

# 2. 비상용 가짜 데이터 (서버 차단 시 사용)
def get_fake_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    prices = np.random.normal(0, 1.5, 100).cumsum() + 100
    return pd.DataFrame({'close': prices, 'high': prices*1.02, 'low': prices*0.98, 'open': prices*0.99}, index=dates)

# 3. 데이터 엔진 (차단 시 자동 감지)
@st.cache_data(ttl=600)
def get_stock_data(symbol):
    try:
        clean_s = symbol.replace('.KS', '').replace('.KQ', '')
        df = fdr.DataReader(clean_s, '2024-01-01')
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, False # 정상 데이터
        return get_fake_data(), True # 가짜 데이터
    except:
        return get_fake_data(), True # 에러 시 가짜 데이터

# 4. 입력창
t_input = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", value="005930").strip().upper()

if t_input:
    df, is_fake = get_stock_data(t_input)
    df = df.reset_index().rename(columns={'index': 'date', 'Date': 'date'})
    
    # 5. 지표 계산 (무조건 실행)
    close = df['close']
    # RSI
    diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
    rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
    # Williams %R
    h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
    # MACD
    df['e12'] = close.ewm(span=12).mean(); df['e26'] = close.ewm(span=26).mean()
    macd = (df['e12'] - df['e26']).iloc[-1]; sig = (df['e12'] - df['e26']).ewm(span=9).mean().iloc[-1]

    # 6. [화면 구성] 여기서부터 원하시던 자료들이 나옵니다!
    st.markdown(f"<div class='stock-label'>🏷️ 분석 종목: {t_input}</div>", unsafe_allow_html=True)
    
    if is_fake:
        st.warning("⚠️ 현재 서버 차단으로 인해 '분석용 데모 데이터'를 표시 중입니다.")

    # [신호등]
    if rsi < 35 or wr < -80:
        st.markdown(f"<div class='traffic-light buy'>🔴 매수 적기 (저점 신호)</div>", unsafe_allow_html=True)
    elif rsi > 65 or wr > -20:
        st.markdown(f"<div class='traffic-light sell'>🟢 매도 검토 (과열 신호)</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='traffic-light wait'>🟡 관망 및 대기 (중립)</div>", unsafe_allow_html=True)

    # [분석 표] (유한양행 양식 반영)
    st.write("### 📋 4대 전문 지표 분석")
    summary = pd.DataFrame({
        "지표 항목": ["현재가", "RSI 강도", "Williams %R", "MACD 추세"],
        "현재 수치": [f"{close.iloc[-1]:,.0f}", f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd > sig else "하락"],
        "기술적 진단": ["-", "저점" if rsi < 30 else "고점" if rsi > 70 else "보통", "매수권" if wr < -80 else "보통", "골든크로스" if macd > sig else "데드크로스"]
    })
    st.table(summary)

    # [그래프]
    st.write("### 📈 주가 흐름 차트")
    chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
        x='date:T', y=alt.Y('close:Q', scale=alt.Scale(zero=False))
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
