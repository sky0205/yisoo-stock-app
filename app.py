import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v107", layout="wide")

if 'stock_log' not in st.session_state:
    st.session_state.stock_log = {"삼성전자": "005930.KS", "IONQ": "IONQ", "NVDA": "NVDA"}
if 'now_ticker' not in st.session_state:
    st.session_state.now_ticker = "005930.KS"

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #37474F; font-size: 20px; font-weight: bold; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 상단 (이곳은 에러가 나도 절대 안 사라집니다)
st.title("👨‍💻 이수할아버지의 주식분석기 v107")
st.write("---")

# 검색창
st.subheader("🔍 종목 번호(6자리)나 티커를 입력하세요")
u_input = st.text_input("숫자만 입력하고 엔터 (예: 000660)", key="main_search")

if u_input:
    raw = u_input.upper().strip()
    # 숫자 6자리면 코스피(.KS)를 우선 시도
    search_code = raw + ".KS" if (raw.isdigit() and len(raw) == 6) else raw
    st.session_state.stock_log[search_code] = search_code
    st.session_state.now_ticker = search_code
    st.rerun()

# 3. 리스트 선택
st.write("---")
opts = list(st.session_state.stock_log.keys())
sel_ticker = st.selectbox("📋 오늘 분석한 종목들", options=opts, 
                          index=opts.index(st.session_state.now_ticker) if st.session_state.now_ticker in opts else 0)
st.session_state.now_ticker = sel_ticker

# 4. 데이터 엔진 (수신 성공률 강화)
@st.cache_data(ttl=60)
def load_data_v107(ticker):
    try:
        # 1차 시도: 표준 다운로드
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        # 만약 실패하면 코스닥(.KQ)으로 2차 시도 (한국 주식인 경우)
        if (df is None or df.empty) and ".KS" in ticker:
            df = yf.download(ticker.replace(".KS", ".KQ"), period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
            df.columns = [str(c).lower().replace(" ", "") for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            return df.sort_values('Date').ffill().dropna()
    except: return None
    return None

# 분석 결과 출력
if sel_ticker:
    df = load_data_v107(sel_ticker)
    if df is not None:
        close = df['close']; high = df['high']; low = df['low']
        # RSI
        diff = close.diff()
        rsi = 100 - (100 / (1 + (diff.where(diff > 0, 0).rolling(14).mean() / -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001))))
        # MACD & 20MA
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        signal = macd.ewm(span=9).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        
        last_rsi = rsi.iloc[-1]; curr_p = close.iloc[-1]
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # 결론 신호등
        if last_rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {sel_ticker}: 강력 매수 (바닥권) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {sel_ticker}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        memo = f"🚩 **{sel_ticker} 지침**: "
        memo += "주가가 20일선 위라 매수하기 좋습니다. " if ma20_up else "아직 중간선 아래라 대기하세요. "
        memo += "MACD 기세도 상승 중입니다." if macd_up else "기세가 아직 꺾여 있습니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        st.metric("현재가", f"{curr_p:,.0f}" if ".K" in sel_ticker else f"{curr_p:,.2f}")

        # 그래프
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA
        
