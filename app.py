import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식앱 v147", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 12px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; font-size: 18px; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면
st.title("👨‍💻 이수할아버지의 주식분석기 v147")
st.write("---")

u_input = st.text_input("🔍 종목 번호 6자리 입력 (예: 005930)", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (차단 방지 하이브리드)
@st.cache_data(ttl=60)
def fetch_v147(t):
    try:
        # [방법 1] 국내 서버 직통 (FinanceDataReader)
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "국내 서버 연결 성공"
    except: pass

    try:
        # [방법 2] 해외 서버 우회 (yfinance - MultiIndex 방어)
        yt = t + ".KS" if t.isdigit() else t
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "해외 서버 우회 성공"
    except: pass
    
    return None, "데이터를 가져올 수 없습니다. 잠시 후 시도해 주세요."

if ticker:
    df, msg = fetch_v147(ticker)
    
    if isinstance(df, pd.DataFrame):
        close = df['close']
        ma20 = close.rolling(20).mean()
        
        # RSI 지표 계산
        # $$RSI = 100 - \frac{100}{1 + \frac{Average Gain}{Average Loss}}$$
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]

        # 결론 표시
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 대기 🟡</div>", unsafe_allow_html=True)

        # 투자 지침 메모
        m_txt = "✅ 주가가 20일선 위에서 힘차게 움직입니다." if close.iloc[-1] > ma20.iloc[-1] else "❌ 아직 20일선 아래에 머물러 있습니다."
        st.markdown(f"<div class='memo-box'>🚩 **분석 정보**: {msg}<br>{m_txt}</div>", unsafe_allow_html=True)

        # 차트 그리기
        chart = alt.Chart(df.tail(100)).mark_line(color='#111827', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=450), use_container_width=True)
