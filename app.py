import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치 (세션 유지)
st.set_page_config(page_title="이수 Stock Analyzer v92", layout="wide")

# [핵심] 선생님이 오늘 검색한 종목들을 저장하는 '기억 바구니'입니다.
if 'favorites' not in st.session_state:
    st.session_state.favorites = {
        "아이온큐": "IONQ", "삼성전자": "005930.KS", "현대차": "005380.KS", 
        "엔비디아": "NVDA", "유한양행": "000100.KS"
    }

# 스타일 설정 (선생님 전용 대형 폰트)
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .sell-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 6px solid #0059FF; background-color: #EEF2FF; color: #0059FF; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단: 자유 검색창 (입력 즉시 리스트에 기억됨)
st.title("👨‍💻 이수할아버지의 주식분석기 v92")

st.subheader("🔍 종목 빠른 검색 (입력 시 자동 저장)")
col_in, col_btn = st.columns([3, 1])

with col_in:
    search_input = st.text_input("종목 코드나 티커를 입력하고 엔터를 치세요", placeholder="예: TSLA 또는 000660.KS", key="search_bar")

# [자동 기억 로직] 검색창에 값이 들어오면 즉시 단골 리스트에 추가
if search_input:
    s_code = search_input.upper()
    if s_code.isdigit() and len(s_code) == 6: s_code += ".KS"
    if s_code not in st.session_state.favorites.values():
        # 이름은 코드로 일단 저장하고, 나중에 분석 시 업데이트
        st.session_state.favorites[s_code] = s_code

st.write("---")

# 3. 분석 종목 선택 (오늘 검색한 것들이 여기에 다 들어있습니다)
sel_name = st.selectbox("📋 오늘 분석 중인 종목 리스트", options=list(st.session_state.favorites.keys()), index=0)
target_code = st.session_state.favorites[sel_name]

# 4. 데이터 엔진
@st.cache_data(ttl=60)
def get_ironclad_data_v92(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except: return None

if target_code:
    df = get_ironclad_data_v92(target_code)
    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        rsi = (100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean().replace(0, 0.001))))).iloc[-1]
        w_r = ((high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100).iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [1] 결론 신호등
        if rsi <= 35 or w_r <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        elif rsi >= 75:
            st.markdown("<div class='sell-box'>⚠️ 분할 매도 (고점 과열) ⚠️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [2] 투자 지침 메모 (신호등 바로 아래)
        memo = f"🚩 **{sel_name} 투자 전략 지침**<br>"
        if rsi <= 35 and not macd_up:
            memo += "💡 **주의**: 가격은 바닥이지만, 아직 하강 기세가 강합니다. <b>'분할 매수'</b>로 천천히 모아가세요.<br>"
        elif rsi <= 35 and macd_up:
            memo += "✅ **추천**: 바닥 확인 후 기세가 살아났습니다. <b>'적극 매수'</b>가 가능한 구간입니다.<br>"
        
        if ma20_up: memo += "✅ **이평선**: 주가가 빨간 중간선 위로 올라와 안정적입니다. 매수를 고려하세요.<br>"
        else: memo += "❌ **이평선**: 아직 중간선 아래에 있습니다. 반등을 더 기다리시는 게 안전합니다.<br>"
        
        if macd_up: memo += "✅ **기세**: 파란선(MACD)이 주황선 위에 있으니 <b>보유</b> 관점이 유리합니다.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가**: 전고점 돌파 임박! 돌파 시 <b>추가 매수(불타기)</b> 전략이 좋습니다."
        
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [3] 상세 지표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".KS" in target_code else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥신호)", f"{rsi:.1f}")
        m3.metric("MACD 상태", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".KS" in target_code else f"${y_high:,.2f}")

        # [4] 주가 차트
        st.write("---")
        st.write(f"### 📊 {sel_name} 주가 흐름 및 볼린저 밴드")
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간 중간선
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        # [5] MACD 차트
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있으면 보유!)")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB', strokeWidth=2).encode(y='MACD:Q') + 
                         m_base.mark_line(color='#F59E0B', strokeWidth=2).encode(y='Signal:Q')).properties(height=250), use_container_width=True)
    else:
        st.error(f"'{target_code}' 데이터를 찾을 수 없습니다. 코드를 다시 확인해 주세요.")

with st.sidebar:
    st.write("### ⚙️ 시스템 도구")
    if st.button("🗑️ 오늘 검색 기록 싹 지우기"):
        st.session_state.clear()
        st.rerun()
