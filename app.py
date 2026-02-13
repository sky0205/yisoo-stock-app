import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="주식분석기 v40", layout="wide")

# [체크] 번역기가 작동하는지 확인하기 위한 장치
# 만약 화면에 '이것은 테스트입니다'가 다른 말로 보이면 번역기가 켜진 것입니다.
st.sidebar.write("System Check: This is a test.")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

# 데이터 가져오기 (가장 단순하고 튼튼한 방식)
@st.cache_data(ttl=60)
def get_data_v40(ticker):
    try:
        # 데이터를 가져올 때 아예 단순화 옵션을 강제로 넣었습니다.
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df.empty: return None
        
        # 이름표가 복잡하면 강제로 1층으로 합침
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        
        # 모든 열 이름을 소문자로 통일
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df.dropna()
    except:
        return None

st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

# 종목 선택
h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    with st.spinner('데이터를 찾는 중...'):
        df = get_data_v40(t_ticker)
        if (df is None or df.empty) and ".KS" in t_ticker:
            df = get_data_v40(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 종가(Close) 찾기
        close = df['close']
        
        # 지표 계산: $RSI$, $MACD$
        # $RSI = 100 - \frac{100}{1 + RS}$
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # $MACD = EMA_{12} - EMA_{26}$
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        
        curr_p = close.iloc[-1]
        
        # 결과 출력
        st.subheader(f"📈 {sel_name} 분석 결과")
        c1, c2 = st.columns(2)
        c1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        c2.metric("RSI (과열도)", f"{rsi.iloc[-1]:.1f}")

        # 그래프
        st.line_chart(close.tail(100))
        st.write("최근 100일 주가 흐름입니다.")
    else:
        st.error("데이터를 가져오지 못했습니다. 잠시 후 다시 시도하거나 다른 종목을 골라보세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
