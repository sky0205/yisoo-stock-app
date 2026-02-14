import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v78", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 선생님이 좋아하시는 시원한 스타일 설정
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 20px; border-radius: 12px; border: 1px solid #D1D5DB; }
    .big-font { font-size:40px !important; font-weight: bold; color: #111827; margin-bottom: 10px; }
    /* 신호등 박스 */
    .buy-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; margin: 20px 0; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .sell-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; margin: 20px 0; border: 6px solid #0059FF; background-color: #EEF2FF; color: #0059FF; }
    .wait-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; margin: 20px 0; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    /* 메모 박스 */
    .memo-box { padding: 25px; border-radius: 15px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #5D4037; font-size: 20px; font-weight: bold; line-height: 1.8; box-shadow: 3px 3px 10px rgba(0,0,0,0.1); }
    .breakout-signal { color: #D32F2F; font-size: 26px; border-bottom: 3px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 가져오기 (가장 안정적인 방식 유지)
@st.cache_data(ttl=60)
def get_pro_data_v78(ticker):
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

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v78")
st.write("---")

sel_name = st.selectbox("📋 분석할 종목 선택", options=list(st.session_state.name_map.keys()), index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_pro_data_v78(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_pro_data_v78(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss))); last_rsi = rsi.iloc[-1]
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100; last_wr = w_r.iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()

        # 3. 매수/매도/관망 신호등 (가장 상단)
        if last_rsi <= 35 or last_wr <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (저점 기회) 🚨</div>", unsafe_allow_html=True)
        elif last_rsi >= 75:
            st.markdown("<div class='sell-box'>⚠️ 이익 실현 (고점 과열) ⚠️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 보유 (추세 대기) 🟡</div>", unsafe_allow_html=True)

        # 4. 상세 보고서 지표
        st.markdown(f"<p class='big-font'>{sel_name} 상세 보고서</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI 지수", f"{last_rsi:.1f}")
        m3.metric("윌리엄 %R", f"{last_wr:.1f}")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 5. 그래프 및 고정 전문가 메모 섹션
        st.write("---")
        col_chart, col_memo = st.columns([2.5, 1])
        
        with col_chart:
            st.write("### 📊 주가 흐름 (볼린저 밴드)")
            chart_df = df.tail(100).copy()
            chart_df['Upper'] = upper.tail(100); chart_df['Lower'] = lower.tail(100); chart_df['MA20'] = ma20.tail(100)
            base = alt.Chart(chart_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
            band = base.mark_area(opacity=0.15, color='gray').encode(y='Lower:Q', y2='Upper:Q')
            line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
            ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
            st.altair_chart((band + line + ma_line).properties(height=450), use_container_width=True)

        with col_memo:
            st.write("### 📝 전문가 메모")
            
            # 신고가 돌파 분석
            dist_to_high = ((y_high - curr_p) / y_high) * 100
            
            if curr_p >= y_high * 0.98:
                memo_content = f"""
                <div class='memo-box'>
                <span class='breakout-signal'>🔥 신고가 돌파 임박!</span><br><br>
                현재 주가가 최고가({y_high:,.0f})에 거의 다다랐습니다. <br><br>
                이 자리를 강력하게 뚫어내면 저항이 없는 <b>'폭발적 상승'</b>이 가능하므로, 돌파 시 적극 매수하는 전략이 유효합니다.
                </div>
                """
            else:
                memo_content = f"""
                <div class='memo-box'>
                🚩 현재 추세 분석<br><br>
                1년 최고가까지 <b>{dist_to_high:.1f}%</b> 남았습니다.<br><br>
                아직 신고가 돌파까지는 여유가 있으니, 하단의 볼린저 밴드 바닥에 닿을 때까지 기다려 저점 매수하는 것이 유리합니다.
                </div>
                """
            st.markdown(memo_content, unsafe_allow_html=True)
            
            st.write("")
            st.info(f"💡 팁: RSI가 35 이하일 때 사서, 신고가 돌파 시 불타기 하는 것이 선생님의 필승법입니다!")

        # 6. 하단 MACD
        st.write("### 📉 MACD 추세선")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100), 'Signal': signal.tail(100)})
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
            
    else:
        st.error("데이터 수신 대기 중... (F5를 눌러주세요)")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
