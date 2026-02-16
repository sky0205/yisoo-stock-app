import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 및 글자 시인성 강화
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #000000 !important; padding: 25px; background: #F0F4F8; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 25px; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold !important; }
    .stTable { background-color: #F8FAFC !important; }
    </style>
    """, unsafe_allow_html=True)

if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '직관적' 분석기 v4100")

# [기능 1] 환율 및 종목 정보 로드
@st.cache_data(ttl=3600)
def load_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame()
    return rate, krx

usd_krw, krx_list = load_base_data()

# [기능 2] 종목명 반환 함수 (강제 노출)
def get_name(sym, krx_df):
    if not sym.isdigit(): return sym
    if not krx_df.empty:
        match = krx_df[krx_df['Code'] == sym]
        if not match.empty: return match['Name'].values[0]
    return f"종목({sym})"

symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 IONQ)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = df['close'].iloc[-1]
            is_us = not symbol.isdigit()
            stock_name = get_name(symbol, krx_list)
            
            # [출력 1] 종목명 및 가격 (원화 환산 포함)
            st.header(f"🏢 {stock_name} ({symbol})")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
                st.caption(f"기준 환율: 1달러당 {usd_krw:,.1f}원 적용")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # --- [4대 지수 계산] ---
            # 1. 볼린저 밴드
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            # 2. MACD
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            # 3. Williams %R
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
            # 4. RSI
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss; rsi = 100 - (100 / (1 + rs)).iloc[-1]

            # [출력 2] 신호등 (매수/매도 시점)
            is_buy = curr_p <= lo_b.iloc[-1] or wr < -80 or rsi < 30
            is_sell = curr_p >= up_b.iloc[-1] or wr > -20 or rsi > 70
            
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
                msg = "현재 가격은 충분히 저렴하며, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            elif is_sell:
                st.markdown("<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
                msg = "단기 고점에 도달했습니다. 수익 실현을 준비할 시점입니다."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)
                msg = "현재는 방향성을 탐색하며 숨을 고르는 구간입니다."

            # 종합 분석 카드 강제 출력
            st.markdown(f"<div class='trend-card'><b>종합 분석:</b> {msg}</div>", unsafe_allow_html=True)

            # [출력 3] 4대 지수 상세 테이블 (숫자 및 판정 포함)
            st.write("### 📋 핵심 지수 분석 결과")
            index_data = {
                "지수 항목": ["Bollinger Band", "RSI (심리)", "MACD (추세)", "Williams %R"],
                "현재 수치": [f"{curr_p:,.0f}", f"{rsi:.2f}", "상승" if macd.iloc[-1] > signal.iloc[-1] else "하락", f"{wr:.2f}"],
                "상태 판정": [
                    "안전마진 확보" if
