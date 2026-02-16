import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정 (부드러운 디자인)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div.stButton > button { background-color: white !important; color: #1E3A8A !important; border: 2px solid #1E3A8A !important; font-weight: bold !important; width: 100%; border-radius: 8px; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B !important; padding: 20px; background: #F8FAFC; border-left: 10px solid #1E3A8A; border-radius: 10px; }
    h1, h2, h3 { color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '부드러운' 분석기 v2300")

# 2. 종목 입력
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            if symbol not in st.session_state['history']: st.session_state['history'].insert(0, symbol)
            
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                match = krx[krx['Code'] == symbol]
                if not match.empty: stock_name = match.iloc[0]['Name']
            except: pass

            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            
            # 지표 계산
            ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            
            curr_p = close.iloc[-1]
            is_buy = curr_p <= lo_b.iloc[-1] or wr < -80
            is_sell = curr_p >= up_b.iloc[-1] or wr > -20

            st.header(f"🏢 {stock_name} ({symbol})")
            st.write(f"### 현재가: {curr_p:,.0f}원")

            if is_buy:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif is_sell:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 3. 부드러운 추세 분석
            st.write("### 📉 오늘의 추세 정밀 진단")
            if is_buy:
                if macd.iloc[-1] < signal.iloc[-1]:
                    trend_msg = "현재 가격은 충분히 매력적이지만, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다. 서두르지 말고 천천히 모아가세요."
                else: trend_msg = "바닥 확인 후 **강력한 반등 신호**를 보내고 있습니다. 긍정적인 접근이 가능합니다."
            elif is_sell: trend_msg = "단기 고점에 도달하여 **수익 실현의 기쁨**을 누릴 준비가 필요한 시점입니다."
            else: trend_msg = "방향성을 탐색하며 **숨 고르기** 중입니다. 다음 신호를 기다려 보세요."

            st.markdown(f"<div class='trend-card'><b>종합 의견:</b> {trend_msg}</div>", unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

# 4. 검색 기록 버튼
st.write("---")
st.subheader("📜 최근 검색 종목")
cols = st.columns(5)
for i, h_sym in enumerate(st.session_state['history'][:10]):
    with cols[i % 5]:
        if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
            st.session_state['target'] = h_sym
            st.rerun()
