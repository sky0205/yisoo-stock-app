import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수할아버지 주식분석기 v45", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

# [특수 수리] 어떤 형태의 데이터가 와도 강제로 1층으로 펴주는 함수
@st.cache_data(ttl=60)
def get_bulletproof_data(ticker):
    try:
        # 최신 yfinance 버전에 대응하여 multi_level_index를 꺼버립니다.
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        
        # 만약 컬럼이 여전히 복잡하다면 강제로 1층 이름만 추출
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 모든 컬럼 이름을 영어 소문자로 고정 (번역기 방어)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # 'close' 이름표가 없으면 첫 번째 열을 종가로 강제 지정
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
        return df.dropna()
    except Exception as e:
        st.error(f"데이터 로딩 중 기술적 오류: {e}")
        return None

st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

# 종목 선택
h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 종목을 골라주세요", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_bulletproof_data(t_ticker)
    
    # 한국 주식 (KOSPI/KOSDAQ) 재시도 로직
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_bulletproof_data(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty and 'close' in df.columns:
        close = df['close']
        
        # 1. 지표 계산 ($RSI$, $MACD$)
        # RSI 공식: $RSI = 100 - \frac{100}{1 + RS}$
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # MACD 공식: $MACD = EMA_{12} - EMA_{26}$
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2)
        lower = ma20 - (std20 * 2)
        
        y_high = close.max()
        curr_p = close.iloc[-1]

        # 2. 결과 출력
        st.markdown(f"<p class='big-font'>{sel_name} 분석 결과</p>", unsafe_allow_html=True)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        col_m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        col_m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 3. 신호등 섹션
        st.write("---")
        if rsi_val.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 (바닥) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 (보유) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 4. 차트 섹션 (Altair를 사용한 볼린저 밴드)
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        c_df = pd.DataFrame({
            'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20
        }).tail(100).reset_index()
        
        chart_base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band_area = chart_base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        price_line = chart_base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        ma_line = chart_base.mark_line(color='#EF5350', strokeWidth=1.5).encode(y='MA20:Q')
        
        st.altair_chart((band_area + price_line + ma_line).properties(height=400), use_container_width=True)

        # 5. MACD 차트
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있으면 긍정)")
        m_df = pd.DataFrame({'Date': df.index, 'MACD': macd, 'Signal': signal}).tail(100).reset_index()
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart((m_base.mark_line(color='#0059FF').encode(y='MACD:Q') + m_base.mark_line(color='#FF8000').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
        
    else:
        st.error("데이터 이름표를 찾는 데 실패했습니다. 화면 상단 주소창 옆의 '번역 기능'을 반드시 끄고 [영문 원본]으로 새로고침해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
