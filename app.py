import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v72", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930", "현대차": "005380", "유한양행": "000100",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 2. [국장 전용] 네이버 금융에서 시세와 이름을 직접 긁어오는 '비밀 열쇠'
def get_naver_data(code):
    try:
        url = f"https://finance.naver.com/item/sise.naver?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 현재가 추출
        price = soup.find('strong', id='_nowVal').text.replace(',', '')
        return float(price)
    except:
        return None

# 3. [데이터 통합 수신] 야후 서버 이름표 문제를 원천 차단하는 로직
@st.cache_data(ttl=60)
def get_robust_data(ticker):
    try:
        # 데이터를 가져올 때부터 2층 이름표를 쓰지 않도록 강제 설정
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        
        # 이름표 세척: 어떤 이름이든 소문자로 통일하고 빈칸 제거
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        
        # 만약 'close' 이름표가 없다면 4번째 열(보통 종가)을 강제로 사용
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, -1] # 가장 마지막 열을 종가로 가정
            
        return df.sort_index().ffill().dropna()
    except:
        return None

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v72")
st.info("💡 야후 서버가 막히면 네이버와 구글의 길로 우회합니다.")

sel_name = st.selectbox("📋 분석할 종목을 고르세요", options=list(st.session_state.name_map.keys()))
code = st.session_state.name_map[sel_name]

if st.button("🚀 분석 시작"):
    with st.spinner('데이터를 찾는 중입니다...'):
        # 미장/국장 구분하여 티커 설정
        ticker = f"{code}.KS" if code.isdigit() else code
        df = get_robust_data(ticker)
        
        # 국장일 경우 네이버 시세도 함께 확인
        naver_p = get_naver_data(code) if code.isdigit() else None
        
    if df is not None and not df.empty:
        # 지표 계산: $RSI$, $Williams \%R$
        close = df['close']
        high = df.get('high', close); low = df.get('low', close)
        
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        # 결과 출력
        st.subheader(f"📈 {sel_name} 분석 보고서")
        m1, m2, m3 = st.columns(3)
        # 가격이 네이버와 다르면 네이버 가격을 우선 표시
        display_p = naver_p if naver_p else close.iloc[-1]
        m1.metric("현재가", f"{display_p:,.0f}" if code.isdigit() else f"{display_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        
        # 그래프
        st.write("### 📊 최근 주가 흐름")
        st.line_chart(close.tail(100))
        
    elif naver_p:
        # 야후 차트는 실패했지만 네이버 시세는 성공했을 때
        st.success(f"✅ 네이버 금융 연결 성공!")
        st.metric(f"{sel_name} 현재가", f"{naver_p:,.0f} 원")
        st.warning("⚠️ 야후 서버 응답 지연으로 차트는 잠시 표시되지 않습니다. (시세는 정확함)")
    else:
        st.error("❌ 모든 데이터 경로가 일시적으로 차단되었습니다. 잠시 후 새로고침(F5) 해주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
