import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치
st.set_page_config(page_title="이수 Stock Analyzer v98", layout="wide")

if 'favorites' not in st.session_state:
    st.session_state.favorites = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "아이온큐": "IONQ", "엔비디아": "NVDA"
    }
if 'current_sel' not in st.session_state:
    st.session_state.current_sel = "삼성전자"

# 선생님 눈이 편안하시도록 크게 스타일 설정
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 번호만 쳐도 찾아내는 스마트 엔진
def quick_fetch_v98(input_val):
    val = input_val.upper().strip()
    # 숫자만 입력된 경우 (한국 주식)
    if val.isdigit():
        for suffix in [".KS", ".KQ"]:
            code = val + suffix
            df = yf.download(code, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
            if df is not None and not df.empty:
                name = yf.Ticker(code).info.get('shortName', val)
                return name, code, df
    else:
        # 영문 티커 (미국 주식)
        df = yf.download(val, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is not None and not df.empty:
            name = yf.Ticker(val).info.get('shortName', val)
            return name, val, df
    return None, None, None

# 3. 상단: 통합 검색 및 기록
st.title("👨‍💻 이수할아버지의 주식분석기 v98")
st.subheader("🔍 종목 번호(6자리)만 입력하고 엔터를 치세요")

search_col, list_col = st.columns([2, 2])

with search_col:
    user_num = st.text_input("번호 입력 (예: 000660)", key="num_search")
    if user_num:
        with st.spinner('번호로 종목을 찾는 중...'):
            name, code, df_raw = quick_fetch_v98(user_num)
            if code:
                st.session_state.favorites[name] = code
                st.session_state.current_sel = name
                st.rerun()
            else:
                st.error("❌ 해당 번호의 종목을 찾을 수 없습니다.")

with list_col:
    # 오늘 본 종목들 다시 고르기
    options = list(st.session_state.favorites.keys())
    try: idx = options.index(st.session_state.current_sel)
    except: idx = 0
    sel_name = st.selectbox("📋 오늘 분석한 종목 리스트", options=options, index=idx)
    st.session_state.current_sel = sel_name

st.write("---")

# 4. 데이터 분석 및 출력
target_ticker = st.session_state.favorites[sel_name]

@st.cache_data(ttl=60)
def get_data_v98(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except: return None

if target_ticker:
    df = get_data_v98(target_ticker)
    if df is not None and not df.empty:
        # 지표 계산 ($RSI$, $Williams \%R$, $MACD$)
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss))); last_rsi = rsi.iloc[-1]
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100; last_wr = w_r.iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [A] 결론 신호등
        if last_rsi <= 35 or last_wr <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥 확인) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침 메모
        memo = f"🚩 **{sel_name} ({target_ticker}) 투자 전략**<br>"
        if ma20_up: memo += "✅ **이평선**: 주가가 빨간 중간선 위로 올라왔습니다. 매수 시점입니다.<br>"
        else: memo += "❌ **이평선**: 아직 중간선 아래에 있습니다. 반등을 더 기다리세요.<br>"
        if macd_up: memo += "✅ **기세**: 파란선(MACD)이 주황선 위에 있어 보유가 유리합니다.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가**: 전고점 돌파 임박! 추가 매수가 가능한 자리입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 상세 수표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".K" in target_ticker else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in target_ticker else f"${y_high:,.2f}")

        # [D] 차트
        st.write("---")
        
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)

with st.sidebar:
    if st.button("🗑️ 오늘 기록 싹 지우기"):
        st.session_state.clear()
        st.rerun()
