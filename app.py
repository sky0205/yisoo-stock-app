import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import time

# 1. 화면 설정 및 종목 기억장치
st.set_page_config(page_title="Stock Analyzer v120", layout="wide")

if 'my_stocks' not in st.session_state:
    st.session_state.my_stocks = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "현대차": "005380.KS", "엔비디아": "NVDA"}
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "005930.KS"

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-top: 20px; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면 상단
st.title("📊 주식 분석기 v120 (최종 정비판)")

# [긴급 조치] 기억 지우기 버튼을 아예 위로 올렸습니다.
if st.button("🔄 [필살기] 데이터 기억 싹 지우고 다시 부르기"):
    st.cache_data.clear()
    st.rerun()

st.write("---")
u_input = st.text_input("🔍 종목 번호(6자리)나 티커 입력 후 엔터", key="main_search")

if u_input:
    code = u_input.upper().strip()
    full_code = code + ".KS" if (code.isdigit() and len(code) == 6) else code
    st.session_state.my_stocks[full_code] = full_code
    st.session_state.active_ticker = full_code
    st.rerun()

# 3. 리스트 선택
opts = list(st.session_state.my_stocks.keys())
sel_name = st.selectbox("📋 분석 리스트", options=opts, index=opts.index(st.session_state.active_ticker) if st.session_state.active_ticker in opts else 0)
st.session_state.active_ticker = sel_name
ticker = st.session_state.my_stocks[sel_name]

# 4. 데이터 엔진 (가장 원초적이고 강력한 방식)
@st.cache_data(ttl=30)
def fetch_safe_v120(t):
    try:
        # 최신 야후 서버 에러를 막기 위해 threads=False와 multi_level_index=False를 강제합니다.
        df = yf.download(t, period="1y", interval="1d", auto_adjust=True, multi_level_index=False, threads=False)
        if df is not None and not df.empty:
            # 번역 기능이 방해하지 못하도록 열 이름을 무조건 영어로 고정합니다.
            df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            return df.sort_values('Date').ffill().dropna()
    except: return None
    return None

if ticker:
    df = fetch_safe_v120(ticker)
    if df is not None:
        close = df['close']
        # 지표 계산 ($RSI = 100 - \frac{100}{1+RS}$)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # MACD: $MACD = EMA_{12} - EMA_{26}$
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        up = ma20 + (std20 * 2); lo = ma20 - (std20 * 2)

        # [A] 결론 신호등 (선생님이 좋아하시는 명당자리)
        st.write("---")
        if rsi.iloc[-1] <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {sel_name}: 강력 매수 (바닥권) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {sel_name}: 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침 메모
        m_up = macd.iloc[-1] > sig.iloc[-1]; a_up = close.iloc[-1] > ma20.iloc[-1]
        memo = f"🚩 **대응 지침**: 주가가 20일선(빨간선) {'위로 올라와 긍정적' if a_up else '아래에 있어 조심'}입니다. 기세는 {'상승 중' if m_up else '하락 중'}입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 수치 및 차트
        st.metric("현재가", f"{close.iloc[-1]:,.0f}원" if ".K" in ticker else f"${close.iloc[-1]:,.2f}")
        c_df = df.tail(100).reset_index(); c_df['MA20'] = ma20.tail(100).values; c_df['Upper'] = up.tail(100).values; c_df['Lower'] = lo.tail(100).values
        base = alt.Chart(c_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간 중간선
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)
    else:
        st.error(f"⚠️ '{sel_name}' 데이터를 아직 못 찾았습니다. 상단의 [데이터 기억 싹 지우기] 버튼을 누르고 5초만 기다려 보세요.")

with st.sidebar:
    if st.button("🗑️ 모든 기록 리셋"):
        st.session_state.clear()
        st.rerun()
