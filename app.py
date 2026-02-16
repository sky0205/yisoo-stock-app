import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import altair as alt

# 1. 화면 스타일 (글자가 안 보일 수 없게 진한 색으로 강제 지정)
st.set_page_config(page_title="이수 주식 마스터", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; color: black; margin-bottom: 20px; border: 8px solid; }
    .buy { background-color: #FFCCCC; border-color: #FF0000; }
    .wait { background-color: #FFFFCC; border-color: #FFCC00; }
    .sell { background-color: #CCFFCC; border-color: #00FF00; }
    h1, h2, h3, p { color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 통합 매매 분석기 (v500)")

# 2. 데이터 가져오기 (가장 튼튼한 방식)
@st.cache_data(ttl=600)
def get_data(symbol):
    try:
        # 한국 주식은 숫자만 입력해도 되게 처리
        target = symbol.replace('.KS', '').replace('.KQ', '')
        df = fdr.DataReader(target, '2024-01-01')
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return None
    except:
        return None

# 3. 입력창
t_input = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", value="005930").strip().upper()

if t_input:
    df = get_data(t_input)
    
    if df is not None:
        df = df.reset_index()
        # 컬럼명을 'date'로 통일
        df.rename(columns={df.columns[0]: 'date'}, inplace=True)
        
        # 4. 지표 계산 (RSI, Williams %R, MACD)
        close = df['close']
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
        df['e12'] = close.ewm(span=12).mean(); df['e26'] = close.ewm(span=26).mean()
        macd = (df['e12'] - df['e26']).iloc[-1]; sig = (df['e12'] - df['e26']).ewm(span=9).mean().iloc[-1]

        # 5. [신호등] - 이제 맨 위로 올라왔습니다!
        st.write("---")
        st.subheader(f"🏷️ 분석 결과: {t_input}")
        
        if rsi < 35 or wr < -80:
            st.markdown(f"<div class='signal-box buy'>🔴 매수 적기 (저점 신호)</div>", unsafe_allow_html=True)
        elif rsi > 65 or wr > -20:
            st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 (고점 과열)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기 (중립)</div>", unsafe_allow_html=True)

        # 6. [분석 표] (유한양행 양식 반영)
        st.write("### 📋 4대 전문 지표 요약")
        summary = pd.DataFrame({
            "지표": ["현재가", "RSI 강도", "Williams %R", "MACD 추세"],
            "수치": [f"{close.iloc[-1]:,.0f}", f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd > sig else "하락"],
            "진단": ["-", "저점" if rsi < 30 else "고점" if rsi > 70 else "보통", "과매도" if wr < -80 else "보통", "골든크로스" if macd > sig else "데드크로스"]
        })
        st.table(summary)

        # 7. [차트]
        st.write("### 📈 주가 추세 그래프")
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x='date:T', y=alt.Y('close:Q', scale=alt.Scale(zero=False))
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("⚠️ 데이터를 가져오지 못했습니다. 종목코드를 확인하시거나 잠시 후 새로고침(F5) 해주세요.")
