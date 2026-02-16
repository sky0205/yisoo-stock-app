import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정 (시인성 극대화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .trend-card { font-size: 22px; line-height: 1.8; color: #000000 !important; padding: 25px; background: #F1F5F9; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 25px; }
    h1, h2, h3, b, span, div { color: #1E3A8A !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #333 !important; }
    </style>
    """, unsafe_allow_html=True)

# [세션 관리] 기록 및 대상 보존
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '정밀 지수' 분석기 v24000")

# 데이터 로드
@st.cache_data(ttl=3600)
def load_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame(columns=['Code', 'Name'])
    return float(rate), krx

usd_krw, krx_list = load_base_data()

# [입력창]
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            if symbol in st.session_state['history']: st.session_state['history'].remove(symbol)
            st.session_state['history'].insert(0, symbol)
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()
            
            # 종목명 확인
            stock_name = symbol
            if not is_us and not krx_list.empty:
                match = krx_list[krx_list['Code'] == symbol]
                if not match.empty: stock_name = str(match['Name'].values[0])

            # --- [지표 정밀 계산] ---
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = float((exp12 - exp26).iloc[-1]); sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = float(((h14.iloc[-1] - curr_p) / (h14.iloc[-1] - l14.iloc[-1])) * -100)

            # [출력 1] 종목 및 가격
            st.header(f"🏢 {stock_name} ({symbol})")
            if is_us: st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
            else: st.subheader(f"현재가: {curr_p:,.0f}원")

            # [출력 2] 신호등
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 (적기)</div>", unsafe_allow_html=True)
                msg = "현재 가격은 매력적인 바닥권입니다. 분할 매수로 대응하기 좋은 시점입니다."
            elif is_sell:
                st.markdown("<div class='signal-box sell'>🟢 매도 검토 (수익실현)</div>", unsafe_allow_html=True)
                msg = "단기 고점에 도달했습니다. 수익을 챙길 준비를 하세요."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 보유</div>", unsafe_allow_html=True)
                msg = "추세를 탐색하는 구간입니다. 현재 포지션을 유지하며 지켜보세요."

            st.markdown(f"<div class='trend-card'><b>종합 분석:</b> {msg}</div>", unsafe_allow_html=True)

            # [출력 3] 상세 지수 (선생님 요청 규칙 적용)
            st.write("### 📋 핵심 지수 정밀 분석")
            c1, c2 = st.columns(2)
            # 볼린저: 현위치 설명
            bb_pos = "▲ 하단 지지선 근처" if curr_p < lo_b else "▼ 상단 저항선 근처" if curr_p > up_b else "밴드 내 안정 구간"
            c1.metric("Bollinger Band (위치)", bb_pos, delta=f"하단가: {lo_b:,.0f}")
            # RSI
