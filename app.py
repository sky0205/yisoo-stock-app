import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

# 2. 입력창
col_in, _ = st.columns([4, 1])
with col_in:
    h_list = list(st.session_state.name_map.keys())
    sel_name = st.selectbox("📋 나의 종목 수첩", options=h_list, index=None)
    new_sym = st.text_input("➕ 새 종목 추가", placeholder="예: 000660")

# 3. 분석 대상 결정
t_name = ""; t_ticker = ""
if new_sym:
    s = new_sym.upper().strip()
    if s.isdigit() and len(s) == 6:
        try:
            r = requests.get(f"https://finance.naver.com/item/main.naver?code={s}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            n = BeautifulSoup(r.text, 'html.parser').select_one(".wrap_company h2 a").text
            t_name, t_ticker = n, s + ".KS"
        except: t_name, t_ticker = s, s + ".KS"
    else: t_name, t_ticker = s, s
    
    if t_name and t_name not in st.session_state.name_map:
        st.session_state.name_map[t_name] = t_ticker
        st.rerun()
elif sel_name:
    t_name = sel_name
    t_ticker = st.session_state.name_map[sel_name]

# 4. 데이터 분석 및 출력
if t_ticker:
    try:
        df = yf.download(t_ticker, period="1y", interval="1d", auto_adjust=True)
        if (df is None or df.empty) and ".KS" in t_ticker:
            df = yf.download(t_ticker.replace(".KS", ".KQ"), period="1y", interval="1d", auto_adjust=True)
        
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [str(c).lower() for c in df.columns]
            
            close = df['close']; high = df['high']; low = df['low']
            
            # 지표 계산
            diff = close.diff()
            gain = diff.where(diff > 0, 0).rolling(14).mean()
            loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = 100 - (100 / (1 + (gain / loss)))
            macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
            sig = macd.ewm(span=9, adjust=False).mean()
            ma20 = close.rolling(20).mean()

            # 결과 화면
            st.subheader(f"📈 {t_name} 분석 결과")
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{close.iloc[-1]:,.2f}")
            c2.metric("RSI (과열도)", f"{rsi.iloc[-1]:.1f}")
            c3.metric("최고가 (1년)", f"{close.max():,.2f}")
            
            # 차트
            st.write("### 주가 흐름 (빨간선: 20일선)")
            st.line_chart(pd.DataFrame({'Price': close, 'MA20': ma20}).tail(80))
            
            st.write("### MACD 추세")
            st.line_chart(pd.DataFrame({'MACD': macd, 'Signal': sig}).tail(80))
            
        else:
            st.error("Data loading failed.")
    except Exception as e:
        st.error(f"Error: {e}. 브라우저 번역 기능을 꺼주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
    st.rerun()
