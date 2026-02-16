import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import datetime

# 1. 시인성 극대화 설정 (글자 크기 및 색상 강제 지정)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .trend-card { font-size: 22px; line-height: 1.8; color: #000000 !important; padding: 25px; background: #F0F7FF; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 25px; }
    h1, h2, h3, b, span { color: #1E3A8A !important; font-weight: bold !important; }
    .metric-text { font-size: 24px; font-weight: bold; color: #E63946; }
    </style>
    """, unsafe_allow_html=True)

# [세션 상태] 검색 기록 및 대상 설정
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '정밀 수치' 분석기 v9000")

# [데이터 로드] 환율 및 종목명 리스트
@st.cache_data(ttl=3600)
def get_base_info():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame(columns=['Code', 'Name'])
    return rate, krx

usd_krw, krx_list = get_base_info()

# [입력창] 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 IONQ)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        # 최근 120일 데이터 수집
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()
            
            # [종목명 강제 매칭]
            stock_name = symbol
            if not is_us and not krx_list.empty:
                match = krx_list[krx_list['Code'] == symbol]
                if not match.empty: stock_name = match['Name'].values[0]

            # --- [4대 지표 정밀 계산] ---
            # 1. Bollinger Bands
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20.iloc[-1] - (std20.iloc[-1] * 2); up_b = ma20.iloc[-1] + (std20.iloc[-1] * 2)
            # 2. RSI (14)
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); rsi_val = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            # 3. MACD
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_series = exp12 - exp26; macd_val = macd_series.iloc[-1]; signal_val = macd_series.ewm(span=9, adjust=False).mean().
        
