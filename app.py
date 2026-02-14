import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 시력 보호 및 고대비 설정
st.set_page_config(page_title="이수 주식 v210", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .traffic-light { padding: 40px; border-radius: 25px; text-align: center; font-size: 50px; font-weight: bold; border: 12px solid; margin-bottom: 30px; }
    .buy { border-color: #FF0000; background-color: #FFF5F5; color: #FF0000; } /* 매수: 빨강 */
    .wait { border-color: #FFD700; background-color: #FFFFF0; color: #B8860B; } /* 관망: 노랑 */
    .sell { border-color: #008000; background-color: #F0FFF0; color: #008000; } /* 매도: 초록 */
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 마스터 분석기 v210")

# 2. 검색 기록 (History) 저장
if 'history' not in st.session_state: st.session_state.history = []
with st.sidebar:
    st.header("📜 검색 기록")
    for h in reversed(st.session_state.history):
        if st.button(f"🔍 {h}"): st.session_state.t_input = h

# 3. 종목 입력
ticker_input = st.text_input("📊 종목 번호(6자리)나 심볼을 입력하세요", value=st.session_state.get('t_input', '005930')).strip().upper()

@st.cache_data(ttl=60)
def fetch_data(t):
    try:
        if t.isdigit(): df = fdr.DataReader(t, '2024')
        else: df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        return df if (df is not None and not df.empty) else None
    except: return None

if ticker_input:
    df = fetch_data(ticker_input)
    if df is not None:
        df = df.reset_index()
        df.columns = [str(c).lower().strip() for c in df.columns]
        if ticker_input not in st.session_state.history:
            st.session_state.history.append(ticker_input)

        # 4. 기술적 지표 계산 (선생님의 요청 4대 지표)
        df['ma20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['lower'] = df['ma20'] - (df['std'] * 2)
        # RSI / Williams %R / MACD 간단 계산
        diff = df['close'].diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); w_r = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100

        # 5. 신호등 판정 및 종목명 표시
        st.write("---")
        if rsi < 35 or w_r < -80:
            st.markdown(f"<div class='traffic-light buy'>🔴 {ticker_input} : 지금 매수 타이밍!</div>", unsafe_allow_html=True)
        elif rsi > 70 or w_r > -20:
            st.markdown(f"<div class='traffic-light sell'>🟢 {ticker_input} : 매도 검토 구간</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='traffic-light wait'>🟡 {ticker_input} : 관망 및 대기</div>", unsafe_allow_html=True)

        # 6. 기술적 분석 요약 표
        st.write("#### 📋 4대 전문 지표 요약")
        summary = pd.DataFrame({
            "지표": ["RSI", "Williams %R", "Bollinger Band", "현재가"],
            "수치": [f"{rsi:.1f}", f"{w_r:.1f}", f"{df['lower'].iloc[-1]:,.0f}", f"{df['close'].iloc[-1]:,.0f}"],
            "판단": ["저점" if rsi < 30 else "고점" if rsi > 70 else "보통", "매수" if w_r < -80 else "매도" if w_r > -20 else "중립", "하단근접" if df['close'].iloc[-1] < df['ma20'].iloc[-1] else "상단근접", "-"]
        })
        st.table(summary) # 탭 구분 마크다운 표 형식
        
        # 7. 차트
        base = alt.Chart(df.tail(100)).encode(x='date:T')
        line = base.mark_line(color='#1E40AF').encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        st.altair_chart(line.properties(height=400), use_container_width=True)
    else:
        st.error("⚠️ 데이터를 가져올 수 없습니다. 종목 번호를 확인하세요.")
