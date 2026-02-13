import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수할아버지 주식분석기 v51", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

# 2. 데이터 가져오기 (가장 강력한 이름표 수리 로직)
@st.cache_data(ttl=60)
def get_ironclad_data_v51(ticker):
    try:
        # 최신 yfinance 구조 강제 대응
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df.empty: return None
        
        # [핵심 수리] 이름표가 2층(MultiIndex)이면 무조건 1층으로 합침
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        
        # 모든 이름표를 소문자로 정리 (Close -> close)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # 'close' 이름표가 없으면 첫 번째 칸을 종가로 강제 지정
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
        return df.sort_index().ffill().bfill().dropna()
    except:
        return None

# 3. UI 디자인
st.title("👨‍💻 이수할아버지의 주식분석기 v51")
st.write("---")

h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_ironclad_data_v51(t_ticker)
    # 국장 재시도
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_ironclad_data_v51(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty and 'close' in df.columns:
        # 데이터 추출
        close = df['close']
        
        # 지표 계산: RSI
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # 볼린저 밴드
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2)
        lower = ma20 - (std20 * 2)
        
        y_high = close.max()
        curr_p = close.iloc[-1]

        # 결과 화면 출력
        st.subheader(f"📈 {sel_name} 분석 보고서")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 신호등
        st.write("---")
        if rsi_val.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; padding:20px; border-radius:10px; text-align:center; font-size:25px; font-weight:bold;'>🚨 강력 매수 신호 (바닥권) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; padding:20px; border-radius:10px; text-align:center; font-size:25px; font-weight:bold;'>📈 추세 상승 중 (수익 보유) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; padding:20px; border-radius:10px; text-align:center; font-size:25px; font-weight:bold;'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 볼린저 밴드 차트
        st.write("### 📊 주가 흐름 및 통로(볼린저 밴드)")
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(100).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF5350', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=400), use_container_width=True)
        
    else:
        st.error("데이터 이름표를 강제로 수리하는 중입니다. 잠시만 기다려 주시거나 새로고침(F5) 해주세요.")

if st.sidebar.button("🗑️ 설정 초기화"):
    st.session_state.clear()
    st.rerun()
