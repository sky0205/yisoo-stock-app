import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 및 부드러운 디자인 설정
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
    </style>
    """, unsafe_allow_html=True)

if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 정밀 주식 분석기 v5000")

# [기능] 환율 및 종목 리스트 로드
@st.cache_data(ttl=3600)
def load_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame()
    return rate, krx

usd_krw, krx_list = load_base_data()

symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 NVDA)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = df['close'].iloc[-1]
            is_us = not symbol.isdigit()
            
            # 종목명 찾기
            stock_name = symbol
            if not is_us and not krx_list.empty:
                match = krx_list[krx_list['Code'] == symbol]
                if not match.empty: stock_name = match['Name'].values[0]

            # --- [4대 지표 계산] ---
            # 1. Bollinger Bands
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            # 2. RSI (14)
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            # 3. MACD (12, 26, 9)
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal_macd = macd.ewm(span=9, adjust=False).mean()
            # 4. Williams %R (14)
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100

            # [출력 1] 종목 정보 및 가격
            st.header(f"🏢 {stock_name} ({symbol})")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
                st.caption(f"환율: 1달러당 {usd_krw:,.1f}원 적용")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # [출력 2] 신호등 (매수/매도 시점)
            is_buy = curr_p <= lo_b.iloc[-1] or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b.iloc[-1] or rsi > 65 or wr > -20
            
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 (적기)</div>", unsafe_allow_html=True)
                msg = "현재 가격은 충분히 매력적인 바닥권이며, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            elif is_sell:
                st.markdown("<div class='signal-box sell'>🟢 매도 검토 (수익실현)</div>", unsafe_allow_html=True)
                msg = "단기 고점에 도달하여 에너지가 과열되었습니다. **수익을 챙길 준비**를 하세요."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기 (보유)</div>", unsafe_allow_html=True)
                msg = "현재는 추세가 결정되지 않은 상태로, 다음 신호를 기다리며 숨을 고르는 구간입니다."

            st.markdown(f"<div class='trend-card'><b>종합 추세 분석:</b> {msg}</div>", unsafe_allow_html=True)

            # [출력 3] 4대 지표 분석 결과 (숫자 포함)
            st.write("### 📋 핵심 지표 및 수치 요약")
            summary_table = pd.DataFrame({
                "분석 지표": ["Bollinger Band", "RSI (심리)", "MACD (추세)", "Williams %R"],
                "현재 수치": [f"{curr_p:,.0f}", f"{rsi:.2f}", "상승" if macd.iloc[-1] > signal_macd.iloc[-1] else "하락", f"{wr:.2f}"],
                "상태 진단": [
                    "안전마진 확보" if curr_p < lo_b.iloc[-1] else "밴드 내 위치",
                    "과매도(바닥)" if rsi < 30 else "정상",
                    "추세 반전 대기" if macd.iloc[-1] < signal_macd.iloc[-1] else "추세 우상향",
                    "단기 바닥 확인" if wr < -80 else "심리 안정"
                ]
            })
            st.table(summary_table)

        else: st.warning("데이터를 가져오는 데 실패했습니다.")
    except Exception as e:
        st.error(f"분석 실행 중 오류가 발생했습니다: {e}")
