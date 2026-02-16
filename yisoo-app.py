import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 시인성 극대화 및 제목 강조 스타일
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .trend-card { font-size: 22px; line-height: 1.8; color: #000000 !important; padding: 25px; background: #F1F5F9; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 10px; }
    .value-card { font-size: 24px; font-weight: bold; color: #FFFFFF !important; padding: 20px; background: #1E3A8A; border-radius: 12px; text-align: center; margin-bottom: 25px; }
    h1, h2, h3, b, span, div { color: #1E3A8A !important; font-weight: bold !important; }
    /* 지표 제목 굵게 강조 */
    [data-testid="stMetricLabel"] { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; }
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #333 !important; }
    /* 자동 화살표 제거 */
    [data-testid="stMetricDelta"] svg { display: none !important; }
    [data-testid="stMetricDelta"] { font-size: 19px !important; font-weight: bold !important; margin-left: -20px !important; }
    </style>
    """, unsafe_allow_html=True)

# [세션 상태 관리]
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '황금 양식' 분석기 v33000")

# 데이터 로드
@st.cache_data(ttl=3600)
def load_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame(columns=['Code', 'Name'])
    return float(rate), krx

usd_krw, krx_list = load_base_data()

# [입력창] 세션 target을 연동하여 버튼 클릭 시 즉시 반영
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['target'], key="main_input").strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            # 기록 업데이트
            if symbol in st.session_state['history']: st.session_state['history'].remove(symbol)
            st.session_state['history'].insert(0, symbol)
            st.session_state['target'] = symbol
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()
            
            # 종목명 확인
            stock_name = symbol
            if not is_us and not krx_list.empty:
                match = krx_list[krx_list['Code'] == symbol]
                if not match.empty: stock_name = str(match['Name'].values[0])

            # 지표 계산
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            exp12 = df['close'].ewm(span=12, adjust=False
