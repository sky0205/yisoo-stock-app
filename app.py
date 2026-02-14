import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt
import requests

# 1. 화면 설정
st.set_page_config(page_title="Stock Analyzer v134", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단: 종목 입력
st.title("👨‍💻 이수할아버지의 주식분석기 v134")

# [필살기] 데이터 기억 초기화
if st.button("🔄 [긴급] 데이터 기억 싹 지우고 다시 부르기"):
    st.cache_data.clear()
    st.rerun()

st.write("---")
u_input = st.text_input("🔍 종목 번호(6자리)나 티커 입력 후 엔터", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (IP 차단을 피하기 위한 위장 장치)
@st.cache_data(ttl=60)
def fetch_iron_v134(t):
    # 길 1: 한국 전용 서버(FinanceDataReader) 시도
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "국내 서버 직통 성공"
    except: pass

    # 길 2: 야후 서버 우회 (사람인 척 위장하는 기능 추가)
    try:
        yt = t + ".KS" if t.isdigit() else t
        # 서버에게 브라우저인 척 속이는 헤더 정보
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        session = requests.Session()
        session.headers.update(headers)
        
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False, session=session)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "해외 서버 우회 성공"
    except: pass
    
    return None, "현재 IP가 차단되어 모든 서버가 응답하지 않습니다."

if ticker:
    with st.spinner('서버의 문지기를 통과하는 중...'):
        df, msg = fetch_iron_v134(ticker)
        
    if isinstance(df, pd.DataFrame):
        close = df['close']
        ma20 = close.rolling(20).mean()
        curr_p = close.iloc[-1]
        
        # 지표 계산
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]

        st.write("---")
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        memo = f"🚩 **{ticker} 투자 대응 지침** ({msg})<br>"
        if curr_p > ma20.iloc[-1]: memo += "✅ **이평선**: 주가가 빨간 20일선 위에 있어 기세가 좋습니다.<br>"
        else: memo += "❌ **이평선**: 아직 20일선 아래에 있습니다. 반등을 더 기다리세요."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # 차트 출력
        chart = alt.Chart(df.tail(100)).mark_line(color='#111827', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'), 
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=400), use_container_width=True)
    else:
        st.error(f"⚠️ {msg}")
        st.info("💡 **IP 차단 해결법**: 휴대폰 핫스팟을 연결하시거나, 30분 뒤에 다시 시도해 보세요.")

with st.sidebar:
    st.write("### 🛠️ 도구함")
    if st.button("🗑️ 모든 기록 리셋"):
        st.session_state.clear()
        st.rerun()
