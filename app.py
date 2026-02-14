import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v73", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

# 2. 데이터 가져오기 (그래프 전용 날짜 수리 로직)
@st.cache_data(ttl=60)
def get_graph_fixed_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        
        # 이름표 정리
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        
        # [핵심 수리] 날짜 형식을 그래프가 그리기 가장 쉬운 상태로 만듭니다.
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None) # 시간대 제거 (에러 방지)
        
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 1] # 종가가 없으면 첫 번째 숫자열 사용
            
        return df.sort_values('Date').ffill().dropna()
    except:
        return None

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v73")
st.write("---")

sel_name = st.selectbox("📋 분석할 종목 선택", options=list(st.session_state.name_map.keys()))
t_ticker = st.session_state.name_map[sel_name]

if st.button("🚀 분석 및 그래프 그리기"):
    with st.spinner('차트를 정밀하게 그리는 중입니다...'):
        df = get_graph_fixed_data(t_ticker)
        
        # 한국 주식 재시도
        if (df is None or df.empty) and ".KS" in t_ticker:
            df = get_graph_fixed_data(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']
        high = df.get('high', close); low = df.get('low', close)
        
        # RSI, 윌리엄 %R
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        # 1. 숫자 보고서 (이건 어제 보였던 부분)
        st.subheader(f"📈 {sel_name} 분석 지표")
        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{close.iloc[-1]:,.0f}" if ".K" in t_ticker else f"{close.iloc[-1]:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")

        # 2. [오늘의 핵심] 그래프 강제 출력
        st.write("---")
        st.subheader("📊 최근 주가 흐름 (그래프)")
        
        # 그래프 데이터 준비 (최근 100일)
        chart_data = df[['Date', 'close']].tail(100)
        
        # Streamlit 기본 차트로 안정성 강화
        st.line_chart(chart_data.set_index('Date'))
        
        # 보너스: 바닥 신호등
        if rsi_val.iloc[-1] <= 35 or w_r.iloc[-1] <= -80:
            st.error("🚨 지금은 '바닥권'입니다. 매수 관점으로 보세요!")
        elif rsi_val.iloc[-1] >= 70:
            st.warning("⚠️ 지금은 '과열권'입니다. 조심하세요!")
        else:
            st.success("🟢 현재 안정적인 흐름입니다.")
            
    else:
        st.error("❌ 데이터 수신은 성공했으나 그래프를 그리는 데 실패했습니다. 잠시 후 새로고침(F5) 해주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
