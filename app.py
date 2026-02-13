
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수할아버지 주식분석기 v56", layout="wide")

# [진단 장치] 번역기가 켜져 있으면 이 글자가 한글로 변합니다.
st.sidebar.title("🛠️ 분석기 상태 진단")
st.sidebar.write("Translation Check: **OK (English)**")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

# 2. 데이터 가져오기 (가장 독한 수리 로직 적용)
@st.cache_data(ttl=60)
def get_ironclad_data_v56(ticker):
    try:
        # 데이터를 가져올 때 이름표가 겹치지 않도록 강제 설정
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        
        if df.empty: return None
        
        # [핵심 수리] 이름표가 몇 층이든 상관없이 강제로 1층으로 합침
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
            
        # 모든 이름표에서 빈칸을 없애고 영어 소문자로 통일
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        
        # 'close' 이름표가 없으면 첫 번째 열을 강제로 가격으로 지정
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
        return df.sort_index().ffill().bfill().dropna()
    except Exception as e:
        st.sidebar.error(f"데이터 연결 실패: {e}")
        return None

# 3. UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v56")
st.write("---")

h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 분석할 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_ironclad_data_v56(t_ticker)
    
    # 한국 주식 재시도
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_ironclad_data_v56(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty and 'close' in df.columns:
        st.sidebar.success("✅ 데이터 수신 성공!")
        
        close = df['close']
        high = df.get('high', close)
        low = df.get('low', close)
        
        # 지표 계산: RSI, 윌리엄 %R
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        # 볼린저 밴드
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        y_high = close.max(); curr_p = close.iloc[-1]

        # 4. 분석 보고서 출력
        st.markdown(f"### 📈 {sel_name} 분석 보고서")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 5. 신호등 섹션
        st.write("---")
        if rsi_val.iloc[-1] <= 35 or w_r.iloc[-1] <= -80:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; padding:25px; border-radius:15px; text-align:center; font-size:30px; font-weight:bold; border: 3px solid #FF4B4B;'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; padding:25px; border-radius:15px; text-align:center; font-size:30px; font-weight:bold; border: 3px solid #2E7D32;'>📈 추세 상승 중 (보유) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; padding:25px; border-radius:15px; text-align:center; font-size:30px; font-weight:bold; border: 3px solid #9E9E9E;'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 6. 차트 섹션
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(100).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        price_line = base.mark_line(color='#1E1E1E', strokeWidth=2.5).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF5350', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + price_line + ma_line).properties(height=450), use_container_width=True)
        
    else:
        st.sidebar.error("❌ 데이터를 가져왔으나 가격표가 없습니다.")
        st.error("데이터 이름표(Close 등)를 찾는 데 실패했습니다. 영문 원본 상태인지 다시 확인해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
