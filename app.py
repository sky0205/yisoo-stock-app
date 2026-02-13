import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정 및 시스템 체크
st.set_page_config(page_title="이수할아버지 주식분석기 v52", layout="wide")
st.sidebar.info("STATUS: System Online (English Mode)")

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

# 2. 데이터 가져오기 (가장 강력한 복구 로직)
@st.cache_data(ttl=60)
def get_ironclad_data_v52(ticker):
    try:
        # 최신 yfinance 구조 강제 대응
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        
        # 이름표가 2층이면 1층으로 합침
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        
        # 모든 이름표를 소문자로 정리 (번역기 방어)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # 'close' 이름표가 없으면 첫 번째 칸을 종가로 강제 지정
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
            
        return df.sort_index().ffill().bfill().dropna()
    except:
        return None

# 3. UI 디자인 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v52")
st.write("---")

h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_ironclad_data_v52(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_ironclad_data_v52(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty and 'close' in df.columns:
        # 데이터 추출
        close = df['close']
        high = df.get('high', close)
        low = df.get('low', close)
        
        # [복구] 윌리엄 %R 계산 공식
        # $Williams \%R = \frac{Highest High - Close}{Highest High - Lowest Low} \times -100$
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        # RSI 계산
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # 볼린저 밴드
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        y_high = close.max(); curr_p = close.iloc[-1]

        # 4. 분석 보고서 출력 (윌리엄 지수 포함)
        st.markdown(f"<p class='big-font'>{sel_name} 분석 보고서</p>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}") # 다시 나타난 윌리엄 지수!
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 5. 신호등
        st.write("---")
        last_w_r = w_r.iloc[-1]
        if last_w_r <= -80:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출 구간) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 (수익 보유) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 6. [복구] 그래프 섹션 (볼린저 밴드 포함)
        st.write("### 📊 주가 흐름 및 볼린저 밴드 (최근 100일)")
        # 날짜 순서가 뒤섞이지 않게 리셋 인덱스
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(100).reset_index(drop=True)
        c_df['Date'] = df.index[-100:]
        
        # 차트 그리기
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#1E1E1E', strokeWidth=2.5).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF5350', strokeWidth=2).encode(y='MA20:Q')
        
        st.altair_chart((band + line + ma_line).properties(height=450), use_container_width=True)
        
    else:
        st.error("데이터 이름표를 찾는 데 실패했습니다. 영문 원본 상태인지 다시 한번 확인해 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
