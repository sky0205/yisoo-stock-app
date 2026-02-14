import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v80", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "아이온큐": "IONQ", "삼성전자": "005930.KS", "현대차": "005380.KS", 
        "엔비디아": "NVDA", "유한양행": "000100.KS", "쿠팡": "CPNG"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #424242; font-size: 19px; font-weight: bold; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_pro_data_v80(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except: return None

st.title("👨‍💻 이수할아버지의 주식분석기 v80")
st.write("---")

sel_name = st.selectbox("📋 종목 선택", options=list(st.session_state.name_map.keys()), index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_pro_data_v80(t_ticker)
    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        rsi = (100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean().replace(0, 0.001))))).iloc[-1]
        w_r = ((high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100).iloc[-1]
        ma20 = close.rolling(20).mean()
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()

        # 1. 상단 신호등
        is_bottom = rsi <= 35 or w_r <= -80
        if is_bottom:
            st.markdown("<div class='buy-box'>🚨 가격 바닥권 (선취매 검토) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 추세 관망 구간 🟡</div>", unsafe_allow_html=True)

        # 2. [오늘의 핵심] 전문가 메모 보강
        macd_up = macd.iloc[-1] > signal.iloc[-1]
        ma20_up = curr_p > ma20.iloc[-1]
        
        memo = f"🚩 **{sel_name} 투자 전략 메모**<br>"
        if is_bottom and not macd_up:
            memo += "⚠️ **알림**: 현재 주가는 '바닥'이지만 아직 '상승세'로 돌아서지는 않았습니다. <br>&nbsp;&nbsp;&nbsp;&nbsp;조금 더 안전하게 하시려면 MACD 파란선이 위로 꺾일 때까지 분할로 접근하세요.<br>"
        elif is_bottom and macd_up:
            memo += "✅ **절호의 기회**: 바닥 확인 후 MACD까지 상승으로 돌아섰습니다. 공격적 매수 가능!<br>"
        
        if ma20_up: memo += "✅ **이동평균**: 빨간색 중간선 위에 있어 안정적입니다.<br>"
        else: memo += "❌ **이동평균**: 아직 중간선 아래에 있으니 반등 시 저항을 조심하세요.<br>"
        
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # 3. 지표 및 그래프
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (바닥여부)", f"{rsi:.1f}")
        m3.metric("MACD 상태", "상승세" if macd_up else "하락세")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        st.write("---")
        chart_df = df.tail(100).copy()
        chart_df['MA20'] = ma20.tail(100)
        base = alt.Chart(chart_df).encode(x='Date:T')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((line + ma_line).properties(height=400), use_container_width=True)

        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있어야 보유)")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100), 'Signal': signal.tail(100)})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)

if st.sidebar.button("🗑️ 리셋"):
    st.session_state.clear()
    st.rerun()
