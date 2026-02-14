import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v76", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 시각적 효과를 위한 스타일 설정
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 20px; border-radius: 12px; border: 1px solid #D1D5DB; }
    .big-font { font-size:40px !important; font-weight: bold; color: #111827; margin-bottom: 10px; }
    .buy-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; margin: 25px 0; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .sell-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; margin: 25px 0; border: 6px solid #0059FF; background-color: #EEF2FF; color: #0059FF; }
    .wait-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; margin: 25px 0; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 가져오기 (가장 안정적인 v70 로직 유지)
@st.cache_data(ttl=60)
def get_final_data_v76(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        if 'close' not in df.columns: df['close'] = df.iloc[:, 1]
        return df.sort_values('Date').ffill().dropna()
    except:
        return None

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v76")
st.write("---")

sel_name = st.selectbox("📋 분석할 종목 선택", options=list(st.session_state.name_map.keys()), index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_final_data_v76(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_final_data_v76(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close); vol = df.get('volume', 0)
        
        # 1. RSI / 윌리엄 %R / MACD / 볼린저
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        curr_p = close.iloc[-1]; last_rsi = rsi.iloc[-1]; last_wr = w_r.iloc[-1]

        # 3. [핵심] 매수/매도/관망 신호 박스
        st.write("### 📢 실시간 투자 전략 판정")
        if last_rsi <= 35 or last_wr <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        elif last_rsi >= 70 or last_wr >= -20:
            st.markdown("<div class='sell-box'>⚠️ 분할 매도 (고점 과열) ⚠️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 보유 (추세 대기) 🟡</div>", unsafe_allow_html=True)

        # 4. 분석 보고서 지표
        st.markdown(f"<p class='big-font'>{sel_name} 상세 지표</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{last_rsi:.1f}")
        m3.metric("윌리엄 %R", f"{last_wr:.1f}")
        m4.metric("20일 이동평균", f"{ma20.iloc[-1]:,.0f}" if ".K" in t_ticker else f"{ma20.iloc[-1]:,.2f}")

        # 5. 그래프 섹션: 볼린저 밴드
        st.write("---")
        st.write("### 📊 주가 흐름 및 볼린저 밴드 (회색: 주가 통로)")
        chart_df = df.tail(100).copy()
        chart_df['Upper'] = upper.tail(100); chart_df['Lower'] = lower.tail(100); chart_df['MA20'] = ma20.tail(100)
        
        base = alt.Chart(chart_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.15, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=400), use_container_width=True)

        # 6. 하단 그래프: MACD & 거래량
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write("### 📉 MACD 추세")
            m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100), 'Signal': signal.tail(100)})
            m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
            st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
        with c2:
            st.write("### 📈 거래량 (Volume)")
            v_df = pd.DataFrame({'Date': chart_df['Date'], 'Volume': vol.tail(100)})
            st.altair_chart(alt.Chart(v_df).mark_bar(color='#9CA3AF').encode(x='Date:T', y='Volume:Q').properties(height=200), use_container_width=True)
            
    else:
        st.error("데이터 수신 대기 중... (F5를 눌러주세요)")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
