
import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v79", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 선생님 취향 저격 스타일링
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .big-font { font-size:35px !important; font-weight: bold; color: #111827; }
    /* 신호등 및 메모 스타일 */
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .sell-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #0059FF; background-color: #EEF2FF; color: #0059FF; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #424242; font-size: 20px; font-weight: bold; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 가져오기 (가장 안정적인 방식 유지)
@st.cache_data(ttl=60)
def get_final_data_v79(ticker):
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
st.title("👨‍💻 이수할아버지의 주식분석기 v79")
st.write("---")

sel_name = st.selectbox("📋 종목 선택", options=list(st.session_state.name_map.keys()), index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_final_data_v79(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_final_data_v79(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        rsi = (100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean().replace(0, 0.001))))).iloc[-1]
        w_r = ((high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100).iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()

        # 3. 신호등 섹션 (상단)
        if rsi <= 35 or w_r <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 신호 (바닥권) 🚨</div>", unsafe_allow_html=True)
        elif rsi >= 75:
            st.markdown("<div class='sell-box'>⚠️ 분할 매도 신호 (과열권) ⚠️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # 4. 전문가 메모 (신호등 바로 아래로 이동)
        dist_to_high = ((y_high - curr_p) / y_high) * 100
        macd_hold = macd.iloc[-1] > signal.iloc[-1]
        ma20_break = curr_p > ma20.iloc[-1]
        
        memo_text = f"🚩 **{sel_name} 투자 지침**<br>"
        if ma20_break: memo_text += "✅ 주가가 <b>빨간색 중간선(20일선)을 돌파</b>했습니다. 매수를 적극 고려하세요!<br>"
        if macd_hold: memo_text += "✅ <b>파란선(MACD)이 주황선 위에 위치</b>합니다. 상승 기세가 좋으니 '보유' 관점입니다.<br>"
        if curr_p >= y_high * 0.98: memo_text += "🔥 <b>신고가 돌파 임박!</b> 돌파 시 추가 매수(불타기) 전략이 유효합니다.<br>"
        else: memo_text += f"ℹ️ 전고점까지 약 {dist_to_high:.1f}% 남았습니다."

        st.markdown(f"<div class='memo-box'>{memo_text}</div>", unsafe_allow_html=True)

        # 5. 상세 지표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI 지수", f"{rsi:.1f}")
        m3.metric("윌리엄 %R", f"{w_r:.1f}")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 6. 볼린저 밴드 그래프 (거래량 삭제)
        st.write("---")
        st.write("### 📊 주가 흐름 및 볼린저 밴드 (빨간색 중간선 돌파 여부 확인)")
        chart_df = df.tail(100).copy()
        chart_df['Upper'] = upper.tail(100); chart_df['Lower'] = lower.tail(100); chart_df['MA20'] = ma20.tail(100)
        base = alt.Chart(chart_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.15, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간색 중간선
        st.altair_chart((band + line + ma_line).properties(height=450), use_container_width=True)

        # 7. MACD 그래프
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있으면 보유!)")
        
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100), 'Signal': signal.tail(100)})
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        macd_chart = m_base.mark_line(color='#2563EB', strokeWidth=2).encode(y='MACD:Q') # 파란선
        sig_chart = m_base.mark_line(color='#F59E0B', strokeWidth=2).encode(y='Signal:Q') # 주황선
        st.altair_chart((macd_chart + sig_chart).properties(height=250), use_container_width=True)
            
    else:
        st.error("데이터를 불러올 수 없습니다. F5를 눌러주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
