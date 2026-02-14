import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v105", layout="wide")

# 오늘 본 종목들을 기억하는 바구니
if 'my_stocks' not in st.session_state:
    st.session_state.my_stocks = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
if 'now_view' not in st.session_state:
    st.session_state.now_view = "005930.KS"

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #37474F; font-size: 20px; font-weight: bold; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면 구성
st.title("👨‍💻 이수할아버지의 주식분석기 v105")
st.write("---")

# 검색창 영역
st.subheader("🔍 종목 번호(6자리)나 티커를 입력하세요")
col_in, col_btn = st.columns([3, 1])

with col_in:
    user_input = st.text_input("숫자만 입력해도 됩니다 (예: 000660)", key="search_bar")

if user_input:
    code = user_input.upper().strip()
    # 한국 주식 번호 6자리 자동 완성
    full_code = code + ".KS" if (code.isdigit() and len(code) == 6) else code
    # 일단 리스트에 넣고 화면 전환
    st.session_state.my_stocks[full_code] = full_code
    st.session_state.now_view = full_code
    st.rerun()

st.write("---")

# 3. 리스트에서 고르기
opts = list(st.session_state.my_stocks.keys())
sel_ticker = st.selectbox("📋 오늘 분석 중인 리스트 (방금 검색한 것도 여기 들어있습니다)", 
                          options=opts, 
                          index=opts.index(st.session_state.now_view) if st.session_view in opts else 0)
st.session_state.now_view = sel_ticker

# 4. 데이터 로드 및 분석
@st.cache_data(ttl=60)
def load_data_final(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "") for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except: return None

if sel_ticker:
    df = load_data_final(sel_ticker)
    if df is not None:
        close = df['close']; high = df['high']; low = df['low']
        # RSI 계산
        diff = close.diff()
        rsi = 100 - (100 / (1 + (diff.where(diff > 0, 0).rolling(14).mean() / -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001))))
        # MACD 및 이평선
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        signal = macd.ewm(span=9).mean()
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        
        last_rsi = rsi.iloc[-1]; curr_p = close.iloc[-1]; macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # 결론 출력
        if last_rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {sel_ticker}: 강력 매수 (바닥권) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {sel_ticker}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        memo = f"🚩 **투자 지침**: "
        memo += "주가가 20일선 위로 올라와 안정적입니다. " if ma20_up else "아직 20일선 아래이니 조심하세요. "
        memo += "MACD 기세가 상승 중입니다." if macd_up else "기세가 아직 하락 중입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # 지표 칸
        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in sel_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (바닥여부)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")

        # 그래프
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((line + ma_line).properties(height=400), use_container_width=True)
    else:
        st.error("데이터를 불러올 수 없습니다. 번호를 다시 확인해주세요.")
