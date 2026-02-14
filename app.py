import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 초기 상태 저장
st.set_page_config(page_title="이수 Stock Analyzer v95", layout="wide")

# 오늘 본 종목을 기억하는 바구니
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = "005930.KS" # 기본값: 삼성전자
if 'search_history' not in st.session_state:
    st.session_state.search_history = ["005930.KS", "IONQ", "NVDA"]

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 21px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 검색창 (입력 즉시 작동)
st.title("👨‍💻 이수할아버지의 주식분석기 v95")
st.write("---")

col1, col2 = st.columns([3, 1])
with col1:
    # [핵심] 여기에 입력하고 엔터를 치면 즉시 분석 시작
    user_input = st.text_input("🔍 종목 번호(6자리)나 티커를 입력하세요", placeholder="예: 000660 또는 TSLA", key="search_input")
with col2:
    # 그동안 검색한 리스트에서 골라보기
    selected_hist = st.selectbox("📋 오늘 본 종목 다시보기", options=st.session_state.search_history)

# 입력값 처리 로직
final_ticker = st.session_state.current_ticker
if user_input:
    temp_ticker = user_input.upper().strip()
    if temp_ticker.isdigit() and len(temp_ticker) == 6:
        temp_ticker += ".KS" # 한국 주식 자동 완성
    final_ticker = temp_ticker
    # 히스토리에 추가
    if final_ticker not in st.session_state.search_history:
        st.session_state.search_history.insert(0, final_ticker)
    st.session_state.current_ticker = final_ticker
elif selected_hist:
    final_ticker = selected_hist

# 3. 데이터 엔진
@st.cache_data(ttl=60)
def fetch_data_v95(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if data is None or data.empty: return None
        data.columns = [str(c).lower().replace(" ", "").strip() for c in data.columns]
        data = data.reset_index()
        data.rename(columns={data.columns[0]: 'Date'}, inplace=True)
        data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
        return data.sort_values('Date').ffill().dropna()
    except: return None

# 4. 분석 결과 출력
if final_ticker:
    df = fetch_data_v95(final_ticker)
    if df is not None and not df.empty:
        # 지표 계산 ($RSI$, $W\%R$, $MACD$)
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss))); last_rsi = rsi.iloc[-1]
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100; last_wr = w_r.iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [1] 결론 신호등
        if last_rsi <= 35 or last_wr <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [2] 투자 지침 메모
        memo = f"🚩 **{final_ticker} 분석 및 대응 전략**<br>"
        if ma20_up: memo += "✅ **이동평균**: 주가가 빨간 중간선(20일선) 위로 올라와 안정적입니다.<br>"
        else: memo += "❌ **이동평균**: 아직 중간선 아래에 있으니 반등을 더 확인하세요.<br>"
        if macd_up: memo += "✅ **기세**: 파란선(MACD)이 주황선 위에 있어 보유가 유리합니다.<br>"
        else: memo += "⚠️ **주의**: 기세가 아직 하락 중입니다. 바닥 신호가 나와도 조금 더 기다리세요.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가**: 전고점 돌파 임박! 돌파 시 추가 매수 자립입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [3] 상세 보고서
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in final_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in final_ticker else f"{y_high:,.2f}")

        # [4] 주가 차트 (볼린저 밴드)
        st.write("---")
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간 중간선
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        # [5] MACD 차트
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있어야 보유!)")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else:
        st.error(f"⚠️ '{final_ticker}' 데이터를 가져올 수 없습니다. 인터넷 연결이나 코드를 확인해 주세요.")

with st.sidebar:
    if st.button("🗑️ 전체 초기화"):
        st.session_state.clear()
        st.rerun()
