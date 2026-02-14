import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import altair as alt
import time

# 1. 화면 설정
st.set_page_config(page_title="Stock Analyzer v135", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면 상단
st.title("👨‍💻 주식 분석기 v135 (데이터 수신 최종 보강판)")

# [필살기] 데이터 기억 초기화 버튼
if st.button("🔄 [필살기] 데이터 기억 싹 지우고 다시 부르기"):
    st.cache_data.clear()
    st.rerun()

st.write("---")
u_input = st.text_input("🔍 종목 번호(6자리)나 티커 입력 후 엔터 (예: 005930)", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (3단계 우회로 확보)
@st.cache_data(ttl=60)
def fetch_iron_v135(t):
    # 길 1: 한국 전용 서버(FinanceDataReader)
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "국내 서버 직통 성공"
    except: pass

    # 길 2: 야후 서버 (다중 인덱스 방지 모드)
    try:
        yt = t + ".KS" if t.isdigit() else t
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False, threads=False)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "해외 서버 우회 성공"
    except: pass
    
    return None, "모든 통로가 차단되었습니다. 잠시 후 시도하거나 핫스팟을 연결해 보세요."

if ticker:
    with st.spinner('서버의 문지기를 통과하는 중...'):
        df, msg = fetch_iron_v135(ticker)
        
    if isinstance(df, pd.DataFrame):
        close = df['close']
        # 지표 계산 ($RSI$, $MACD$)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        up_b, lo_b = ma20 + (std20 * 2), ma20 - (std20 * 2)

        # [A] 결론 신호등
        st.write("---")
        if rsi_val <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침
        m_up = macd.iloc[-1] > sig.iloc[-1]; a_up = close.iloc[-1] > ma20.iloc[-1]
        memo = f"🚩 **{ticker} 투자 대응 지침** ({msg})<br>"
        if a_up: memo += "✅ **이평선**: 주가가 빨간 20일선 위에 있어 기세가 좋습니다.<br>"
        else: memo += "❌ **이평선**: 아직 20일선 아래에 있습니다. 반등을 더 기다리세요.<br>"
        if m_up: memo += "✅ **기세**: 상승 동력이 살아있습니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 차트 출력
        st.metric("현재가", f"{close.iloc[-1]:,.0f}원" if ticker.isdigit() else f"${close.iloc[-1]:,.2f}")
        
        
        
        c_df = df.tail(100).reset_index(); c_df['MA20'] = ma20.tail(100).values; c_df['Upper'] = up_b.tail(100).values; c_df['Lower'] = lo_b.tail(100).values
        base = alt.Chart(c_df).encode(x=alt.X(df.columns[0]+':T', title='날짜'))
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간 20일선
        st.altair_chart((line + ma_line).properties(height=500), use_container_width=True)
    else:
        st.error(f"⚠️ {msg}")
        st.info("💡 **IP 차단 해결법**: 휴대폰 핫스팟을 연결하시거나, 30분 뒤에 다시 시도해 보세요.")

with st.sidebar:
    if st.button("🗑️ 모든 기록 리셋"):
        st.session_state.clear()
        st.rerun()
