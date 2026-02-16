import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import altair as alt
import time

# 1. 시력 보호 및 고대비 스타일 설정
st.set_page_config(page_title="이수 주식 마스터 v400", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .traffic-light { padding: 35px; border-radius: 20px; text-align: center; font-size: 40px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    .stock-label { font-size: 30px; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 '절대 멈추지 않는' 분석기")

# 2. 데이터 엔진: 실시간 차단 시 '데모 모드' 자동 전환
@st.cache_data(ttl=600)
def get_invincible_data(symbol):
    try:
        # KRX 혹은 미국 주식 시도
        clean_s = symbol.replace('.KS', '').replace('.KQ', '')
        df = fdr.DataReader(clean_s, '2025-01-01')
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, False
        return None, True
    except:
        return None, True

# 가짜 데이터 생성 (비상용)
def get_demo_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    prices = np.random.normal(0, 1, 100).cumsum() + 100
    df = pd.DataFrame({'close': prices, 'high': prices*1.02, 'low': prices*0.98}, index=dates)
    return df

# 3. 메인 로직
t_input = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", value="005930").strip().upper()

if t_input:
    df, is_demo = get_invincible_data(t_input)
    
    if is_demo:
        st.warning("⚠️ 실시간 데이터 차단됨: '비상용 분석 모드'로 전환합니다.")
        df = get_demo_data()
        df = df.reset_index().rename(columns={'index': 'date'})
    else:
        df = df.reset_index()
        df.columns = [str(c).lower().strip() for c in df.columns]

    # 4. 4대 핵심 지표 계산
    # RSI: $RSI = 100 - \frac{100}{1 + RS}$
    close = df['close']
    diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
    rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
    # Williams %R
    h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
    # MACD
    df['e12'] = close.ewm(span=12).mean(); df['e26'] = close.ewm(span=26).mean()
    macd = (df['e12'] - df['e26']).iloc[-1]; sig = (df['e12'] - df['e26']).ewm(span=9).mean().iloc[-1]

    # 5. [신호등 출력]
    st.markdown(f"<div class='stock-label'>🏷️ 분석 종목: {t_input}</div>", unsafe_allow_html=True)
    
    # 사정권 로직
    is_target = (t_input == "IONQ" and close.iloc[-1] <= 30) or (t_input == "NVDA" and close.iloc[-1] <= 170)
    
    if rsi < 35 or wr < -80 or is_target:
        msg = "🔴 사정권 진입! 적극 매수" if is_target else "🔴 매수 신호 (저점)"
        st.markdown(f"<div class='traffic-light buy'>{msg}</div>", unsafe_allow_html=True)
    elif rsi > 65 or wr > -20:
        st.markdown(f"<div class='traffic-light sell'>🟢 매도 검토 (고점)</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='traffic-light wait'>🟡 관망 및 대기 (중립)</div>", unsafe_allow_html=True)

    # 6. [지표 분석 표] (유한양행 양식 반영)
    st.write("### 📋 4대 전문 지표 분석")
    summary = pd.DataFrame({
        "지표 항목": ["현재가", "RSI 강도", "Williams %R", "MACD 추세"],
        "현재 수치": [f"{close.iloc[-1]:,.0f}", f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd > sig else "하락"],
        "기술적 진단": ["-", "바닥권" if rsi < 30 else "고점권" if rsi > 70 else "보통", "과매도" if wr < -80 else "과매수" if wr > -20 else "보통", "골든크로스" if macd > sig else "데드크로스"]
    })
    st.table(summary)

    # 7. [차트 출력]
    chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
        x='date:T', y=alt.Y('close:Q', scale=alt.Scale(zero=False))
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
