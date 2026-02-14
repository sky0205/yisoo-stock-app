import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 세션 유지
st.set_page_config(page_title="이수 Stock Analyzer v87", layout="wide")

if 'stock_list' not in st.session_state:
    st.session_state.stock_list = {
        "아이온큐": "IONQ", "삼성전자": "005930.KS", "현대차": "005380.KS", 
        "엔비디아": "NVDA", "유한양행": "000100.KS", "쿠팡": "CPNG"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 20px; border: 5px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 20px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #424242; font-size: 19px; font-weight: bold; line-height: 1.7; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 엔진
@st.cache_data(ttl=60)
def get_pro_data_v87(ticker):
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
st.title("👨‍💻 이수할아버지의 주식분석기 v87")
st.write("---")

# 사이드바 종목 추가 (선생님이 좋아하시던 형태)
with st.sidebar:
    st.title("📂 종목 관리")
    n_name = st.text_input("종목명"); n_code = st.text_input("코드")
    if st.button("➕ 추가"):
        if n_name and n_code: st.session_state.stock_list[n_name] = n_code; st.rerun()

sel_name = st.selectbox("📋 분석 종목 선택", options=list(st.session_state.stock_list.keys()))
code = st.session_state.stock_list[sel_name]

if code:
    df = get_pro_data_v87(code)
    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        rsi = (100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean().replace(0, 0.001))))).iloc[-1]
        w_r = ((high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100).iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]
        ma20_up = curr_p > ma20.iloc[-1]

        # 1. 상단 신호등 (가장 먼저 확인)
        if rsi <= 35 or w_r <= -80: st.markdown("<div class='buy-box'>🚨 강력 매수 (가격 바닥권) 🚨</div>", unsafe_allow_html=True)
        elif rsi >= 75: st.markdown("<div class='sell-box' style='padding:25px; border-radius:12px; text-align:center; font-size:32px; font-weight:bold; border:5px solid #0059FF; background-color:#EEF2FF; color:#0059FF;'>⚠️ 분할 매도 (고점 과열) ⚠️</div>", unsafe_allow_html=True)
        else: st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # 2. 상세 지표 (4칸)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".KS" in code else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥여부)", f"{rsi:.1f}")
        m3.metric("MACD 기세", "상승세" if macd_up else "하락세")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".KS" in code else f"${y_high:,.2f}")

        # 3. 메인 섹션: 그래프(좌) + 투자지침 메모(우)
        st.write("---")
        col_chart, col_memo = st.columns([2.2, 1])
        
        with col_chart:
            st.write("### 📊 주가 흐름 (볼린저 밴드)")
            chart_df = df.tail(100).reset_index()
            chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
            base = alt.Chart(chart_df).encode(x='Date:T')
            band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
            line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
            ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간 중간선
            st.altair_chart((band + line + ma_line).properties(height=450), use_container_width=True)

        with col_memo:
            st.write("### 📝 투자 지침 메모")
            memo_text = f"🚩 **{sel_name} 분석 결과**<br><br>"
            
            # 아이온큐 같은 상황(바닥인데 MACD 하락)을 위한 정밀 지침
            if rsi <= 35 and not macd_up:
                memo_text += "💡 **주의**: 현재 가격은 바닥이지만, MACD 파란선이 아래에 있어 기세는 아직 하락 중입니다. <b>'분할 매수'</b>로 대응하세요.<br><br>"
            elif rsi <= 35 and macd_up:
                memo_text += "✅ **매수 적기**: 바닥 신호와 MACD 상승 전환이 동시에 포착되었습니다. <b>'적극 매수'</b> 가능 구간입니다.<br><br>"
            
            if ma20_up: memo_text += "✅ **20일선**: 주가가 빨간색 중간선을 <b>돌파</b>했습니다. 매수를 적극 고려하세요.<br><br>"
            else: memo_text += "❌ **20일선**: 아직 중간선 아래에 있습니다. 반등을 좀 더 확인해야 합니다.<br><br>"
            
            if macd_up: memo_text += "✅ **보유**: <b>파란선이 주황선 위</b>에 있습니다. 기세가 좋으니 보유 관점입니다.<br><br>"
            else: memo_text += "❌ **대기**: 파란선이 아래에 있으니 서두르지 마세요.<br><br>"
            
            if curr_p >= y_high * 0.98: memo_text += "🔥 **신고가 돌파**: 전고점 돌파 임박! 돌파 시 <b>불타기 매수</b> 자리입니다."
            
            st.markdown(f"<div class='memo-box'>{memo_text}</div>", unsafe_allow_html=True)

        # 4. 하단 MACD
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있어야 보유!)")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
