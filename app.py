import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import requests
from bs4 import BeautifulSoup

# 1. 화면 설정 및 세션 기억(Memory) 설정
st.set_page_config(page_title="이수 Stock Analyzer v86", layout="wide")

# 종목 리스트 기억 장치 (오늘 검색한 것들을 저장합니다)
if 'stock_list' not in st.session_state:
    st.session_state.stock_list = {
        "아이온큐": "IONQ", "삼성전자": "005930.KS", "현대차": "005380.KS", 
        "엔비디아": "NVDA", "유한양행": "000100.KS", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 2. 사이드바 - 선생님이 좋아하시던 종목 관리창
with st.sidebar:
    st.title("📂 내 종목 기억창")
    new_name = st.text_input("새 종목 이름 (예: 테슬라)")
    new_code = st.text_input("종목 코드 (예: TSLA)")
    if st.button("➕ 종목 추가하기"):
        if new_name and new_code:
            st.session_state.stock_list[new_name] = new_code
            st.success(f"'{new_name}' 추가 완료!")
            st.rerun()
    
    st.write("---")
    if st.button("🗑️ 오늘 기록 싹 지우기"):
        st.session_state.clear()
        st.rerun()

# 스타일 설정
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #424242; font-size: 19px; font-weight: bold; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 엔진 (미장 스크립트 에러 완벽 차단)
@st.cache_data(ttl=60)
def get_ironclad_data_v86(ticker):
    try:
        # 야후 서버를 속이기 위한 보안 세션
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        
        # 이름표 평탄화 및 소문자화
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        
        # 날짜 수리 (스크립트 에러의 주원인)
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        # 'close' 이름표 강제 고정
        if 'close' not in df.columns:
            for c in ['adjclose', 'price']:
                if c in df.columns: df['close'] = df[c]; break
        
        return df.sort_values('Date').ffill().dropna()
    except: return None

# 4. 메인 화면 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v86")
st.write("---")

# 종목 선택창 (기억된 리스트가 나옵니다)
sel_name = st.selectbox("📋 분석할 종목을 골라주세요", options=list(st.session_state.stock_list.keys()))
code = st.session_state.stock_list[sel_name]

if code:
    with st.spinner(f'{sel_name} 데이터를 분석 중...'):
        df = get_ironclad_data_v86(code)

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        rsi = (100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean().replace(0, 0.001))))).iloc[-1]
        w_r = ((high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100).iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()

        # 1. 신호등 박스
        if rsi <= 35 or w_r <= -80: st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥 기회) 🚨</div>", unsafe_allow_html=True)
        else: st.markdown("<div class='wait-box' style='padding:25px; border-radius:12px; text-align:center; font-size:32px; font-weight:bold; border:5px solid #6B7280; background-color:#F9FAFB; color:#6B7280;'>🟡 관망 및 보유 🟡</div>", unsafe_allow_html=True)

        # 2. 전문가 메모 (신호등 아래)
        macd_up = macd.iloc[-1] > signal.iloc[-1]
        ma20_up = curr_p > ma20.iloc[-1]
        memo = f"🚩 **{sel_name} 투자 지침**<br>"
        if ma20_up: memo += "✅ **매수 고려**: 주가가 <b>빨간색 중간선(20일선)</b> 위로 올라왔습니다.<br>"
        else: memo += "❌ **대기**: 아직 주가가 중간선 아래에 있습니다.<br>"
        if macd_up: memo += "✅ **보유**: <b>파란선(MACD)이 주황선 위</b>에 있어 기세가 좋습니다.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가 돌파**: 전고점 돌파 임박! 강한 상승이 예상됩니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # 3. 상세 지표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".KS" in code else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".KS" in code else f"${y_high:,.2f}")

        # 4. 그래프
        st.write("---")
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=450), use_container_width=True)

        st.write("### 📉 MACD 추세")
        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else:
        st.error("⚠️ 데이터를 가져오지 못했습니다. 미장 종목 코드가 맞는지 확인해 주세요.")
