import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치 (세션 유지)
st.set_page_config(page_title="이수 Stock Analyzer v97", layout="wide")

# 오늘 검색한 종목들을 저장하는 바구니
if 'favorites' not in st.session_state:
    st.session_state.favorites = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "아이온큐": "IONQ", "엔비디아": "NVDA"
    }
# 현재 화면에 보여줄 종목 추적
if 'current_sel' not in st.session_state:
    st.session_state.current_sel = "삼성전자"

# 선생님 전용 대형 스타일 설정
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 21px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 가져오기 엔진 (이름까지 한 번에 처리)
def fetch_data_and_name(input_code):
    code = input_code.upper().strip()
    # 한국 주식 번호 6자리 처리
    if code.isdigit() and len(code) == 6:
        tickers = [code + ".KS", code + ".KQ"]
    else:
        tickers = [code]
    
    for t_code in tickers:
        try:
            # 데이터를 먼저 가져옵니다 (이게 가장 확실한 방법입니다)
            df = yf.download(t_code, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
            if df is not None and not df.empty:
                # 데이터가 있으면 이름을 찾습니다
                ticker_obj = yf.Ticker(t_code)
                name = ticker_obj.info.get('shortName') or ticker_obj.info.get('longName') or t_code
                return name, t_code, df
        except: continue
    return None, None, None

# 3. 상단: 자유 검색창 (즉시 반응)
st.title("👨‍💻 이수할아버지의 주식분석기 v97")
st.write("---")

# 검색창을 더 큼직하게 배치
st.subheader("🔍 새로운 종목 번호나 티커를 입력하세요")
search_input = st.text_input("여기에 입력 후 엔터 (예: 000660 또는 TSLA)", key="search_bar")

if search_input:
    with st.spinner('데이터를 번개처럼 불러오는 중...'):
        name, full_code, df_search = fetch_data_and_name(search_input)
        if full_code:
            st.session_state.favorites[name] = full_code
            st.session_state.current_sel = name
            # 새로운 종목을 찾으면 화면을 즉시 갱신
            st.rerun()
        else:
            st.error("❌ 종목을 찾을 수 없습니다. 번호나 티커를 다시 확인해 주세요.")

st.write("---")

# 4. 분석 대상 선택 (오늘 검색한 종목들이 여기에 다 남습니다)
options = list(st.session_state.favorites.keys())
try:
    def_idx = options.index(st.session_state.current_sel)
except:
    def_idx = 0

sel_name = st.selectbox("📋 오늘 분석 중인 종목 리스트", options=options, index=def_idx)
st.session_state.current_sel = sel_name
target_ticker = st.session_state.favorites[sel_name]

# 5. 분석 화면 출력
@st.cache_data(ttl=60)
def get_analysis_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        # 이름표 평탄화 (에러 방지 핵심)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except: return None

if target_ticker:
    df = get_analysis_data(target_ticker)
    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        rsi = (100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean().replace(0, 0.001))))).iloc[-1]
        w_r = ((high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100).iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [A] 결론 신호등
        if rsi <= 35 or w_r <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침 메모 (선생님 요청 반영)
        memo = f"🚩 **{sel_name} ({target_ticker}) 투자 대응 지침**<br>"
        if rsi <= 35 and not macd_up:
            memo += "💡 **알림**: 가격은 바닥이지만 기세는 하락 중입니다. 분할 매수하세요.<br>"
        if ma20_up: memo += "✅ **20일선**: 주가가 중간선(빨간선) 위로 올라왔습니다. 매수가 유리합니다.<br>"
        else: memo += "❌ **20일선**: 아직 중간선 아래에 있으니 반등을 확인하세요.<br>"
        if macd_up: memo += "✅ **보유**: 파란선(MACD)이 주황선 위에 있어 기세가 좋습니다.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가**: 전고점 돌파 임박! 불타기 가능 자리입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 상세 수치 보고서
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".K" in target_ticker else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in target_ticker else f"${y_high:,.2f}")

        # [D] 그래프
        st.write("---")
        
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        st.write("### 📉 MACD 추세")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)

with st.sidebar:
    if st.button("🗑️ 전체 리셋"):
        st.session_state.clear()
        st.rerun()
