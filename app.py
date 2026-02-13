import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 화면 설정
st.set_page_config(page_title="이수 투자비책 v7", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아", "유한양행"]

# 스타일 설정 (글자 크기 대폭 확대)
st.markdown("""
    <style>
    .stMetric { background-color: #F0F2F6; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 45px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

st.title("📈 이수 할아버지의 '완전체' 주식 분석기")

selected_stock = st.selectbox("분석할 종목을 선택하세요", options=st.session_state.history)

if selected_stock:
    ticker = selected_stock.upper() if selected_stock != "삼성전자" else "005930.KS"
    df = get_stock_data(ticker)
    
    if df is not None:
        close = df['close']
        high = df['high']
        low = df['low']
        
        # 1. RSI 계산
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 2. 윌리엄 %R 계산
        high_14 = high.rolling(14).max()
        low_14 = low.rolling(14).min()
        w_r = (high_14 - close) / (high_14 - low_14) * -100
        
        # 3. MACD 계산
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        sig = macd.ewm(span=9, adjust=False).mean()

        # 4. 볼린저 밴드
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        lower = ma20 - (std20 * 2)

        # 결과 표시
        curr_p = close.iloc[-1]
        curr_rsi = rsi.iloc[-1]
        curr_wr = w_r.iloc[-1]
        macd_up = macd.iloc[-1] > macd.iloc[-2]

        st.markdown(f"<p class='big-font'>{selected_stock}: {curr_p:,.2f}</p>", unsafe_allow_html=True)
        
        # [지수 전광판]
        col1, col2, col3 = st.columns(3)
        col1.metric("RSI (상대강도)", f"{curr_rsi:.1f}")
        col2.metric("윌리엄 %R", f"{curr_wr:.1f}")
        col3.metric("MACD 에너지", "상승세" if macd_up else "하락세")

        # [종합 신호등]
        st.write("---")
        # 윌리엄 지수가 -80 이하이거나 RSI가 35 이하이면 '싸다'고 판단
        is_cheap = curr_rsi <= 35 or curr_wr <= -80
        
        if is_cheap:
            if macd_up:
                st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출!) 🚨</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (추가 하락 중)</div>", unsafe_allow_html=True)
        elif curr_rsi >= 70 or curr_wr >= -20:
            st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;' class='status-box'>💰 익절 권장 (과열 구간) 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F0F2F6; color:#31333F; border-color:#D1D5DB;' class='status-box'>🟡 관망 (보통 상태) 🟡</div>", unsafe_allow_html=True)

        # 차트
        st.write("### 📊 주가 및 볼린저 하단")
        st.line_chart(pd.DataFrame({'주가': close, '밴드하단': lower}).tail(80))
        
        st.write("### 📉 MACD 추세 차트")
        st.line_chart(pd.DataFrame({'MACD': macd, '시그널': sig}).tail(80))

    else:
        st.error("데이터를 가져올 수 없습니다.")
