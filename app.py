import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치
st.set_page_config(page_title="이수 Stock Analyzer v88", layout="wide")

if 'stock_list' not in st.session_state:
    st.session_state.stock_list = {
        "아이온큐": "IONQ", "삼성전자": "005930.KS", "현대차": "005380.KS", 
        "엔비디아": "NVDA", "유한양행": "000100.KS", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 선생님이 좋아하시는 시원시원한 스타일
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .sell-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 6px solid #0059FF; background-color: #EEF2FF; color: #0059FF; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 21px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; box-shadow: 3px 3px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. 왼쪽 사이드바: 종목 추가 및 관리 (선생님 요청 사항)
with st.sidebar:
    st.title("🔎 새로운 종목 검색/추가")
    st.write("분석하고 싶은 새 종목을 입력하세요.")
    add_name = st.text_input("종목 이름 (예: 테슬라)")
    add_code = st.text_input("종목 코드 (예: TSLA)")
    
    if st.button("✨ 리스트에 추가하기"):
        if add_name and add_code:
            st.session_state.stock_list[add_name] = add_code
            st.success(f"'{add_name}' 추가되었습니다!")
            st.rerun()
    
    st.write("---")
    if st.button("🗑️ 전체 초기화 (기본 종목만 남기기)"):
        st.session_state.clear()
        st.rerun()

# 3. 데이터 로딩 엔진 (미장/국장 통합)
@st.cache_data(ttl=60)
def get_advanced_data_v88(ticker):
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

# 4. 메인 화면 구성
st.title("👨‍💻 이수할아버지의 주식분석기 v88")
st.write("---")

# 종목 선택Dropdown
sel_name = st.selectbox("📋 분석할 종목을 선택하세요", options=list(st.session_state.stock_list.keys()))
code = st.session_state.stock_list[sel_name]

if code:
    df = get_advanced_data_v88(code)
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

        # [레이아웃 1순위] 신호등 박스
        if rsi <= 35 or w_r <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        elif rsi >= 75:
            st.markdown("<div class='sell-box'>⚠️ 분할 매도 (고점 과열) ⚠️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [레이아웃 2순위] 투자 지침 메모 (신호등 바로 아래로 이동)
        memo_content = f"🚩 **{sel_name} 핵심 투자 전략**<br>"
        if rsi <= 35 and not macd_up:
            memo_content += "💡 **알림**: 가격은 싸지만(바닥), 아직 기세는 하락 중입니다. <b>'분할 매수'</b>가 안전합니다.<br>"
        elif rsi <= 35 and macd_up:
            memo_content += "✅ **추천**: 바닥 확인 후 기세가 살아났습니다. <b>'적극 매수'</b> 가능 구간입니다.<br>"
        
        if ma20_up: memo_content += "✅ **20일선**: 주가가 빨간 중간선을 <b>돌파</b>했습니다. 매수하기 좋은 시점입니다.<br>"
        else: memo_content += "❌ **20일선**: 아직 중간선 아래에 있습니다. 반등을 더 기다리세요.<br>"
        
        if macd_up: memo_content += "✅ **기세**: 파란선(MACD)이 주황선 위에 있으니 <b>보유</b> 관점 유지하세요.<br>"
        if curr_p >= y_high * 0.98: memo_content += "🔥 **신고가**: 전고점 돌파 임박! 돌파 시 <b>추가 매수(불타기)</b> 전략입니다."
        
        st.markdown(f"<div class='memo-box'>{memo_content}</div>", unsafe_allow_html=True)

        # 5. 상세 수치 보고서
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".KS" in code else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥신호)", f"{rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".KS" in code else f"${y_high:,.2f}")

        # 6. 볼린저 밴드 그래프 (크게)
        st.write("---")
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        # 7. MACD 그래프
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있어야 보유!)")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB', strokeWidth=2).encode(y='MACD:Q') + 
                         m_base.mark_line(color='#F59E0B', strokeWidth=2).encode(y='Signal:Q')).properties(height=250), use_container_width=True)
