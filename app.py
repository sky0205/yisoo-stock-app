import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 - 제목을 v149로 확실히 변경
st.set_page_config(page_title="이수 주식앱 v149", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F9FF; } /* 화면이 바뀌었는지 알 수 있게 배경색을 연한 파란색으로 바꿨습니다 */
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면 제목
st.title("👨‍💻 이수할아버지의 주식분석기 v149")
st.success("🎉 축하합니다! 드디어 최신형 버전으로 접속하셨습니다.")

u_input = st.text_input("🔍 종목 번호 6자리 입력 (예: 005930)", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (클라우드 전용)
@st.cache_data(ttl=60)
def fetch_v149(t):
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "국내 서버 연결 성공"
    except:
        try:
            yt = t + ".KS" if t.isdigit() else t
            df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
            if df is not None and not df.empty:
                df.columns = [str(c).lower().strip() for c in df.columns]
                df = df.reset_index()
                return df, "해외 서버 연결 성공"
        except: return None, "데이터 통로 확인 필요"
    return None, "데이터 없음"

if ticker:
    df, msg = fetch_v149(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close']
        # RSI 지표 계산
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]

        # [신호등 표시]
        st.write("---")
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 대기 🟡</div>", unsafe_allow_html=True)

        st.info(f"🚩 현재 상태: {msg} / 주가가 안정적으로 표시되고 있습니다.")

        # 차트 그리기
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=400), use_container_width=True)
