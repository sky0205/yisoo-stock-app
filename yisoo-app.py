import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 및 글자 시인성 강화 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .trend-card { font-size: 22px; line-height: 1.8; color: #000000 !important; padding: 25px; background: #F1F5F9; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 25px; }
    h1, h2, h3, b, span, th, td { color: #1E3A8A !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# [세션 상태] 검색 기록 보존
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '무결점' 분석기 v10000")

# [기능 1] 환율 및 종목 리스트 로드
@st.cache_data(ttl=3600)
def load_all_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame(columns=['Code', 'Name'])
    return float(rate), krx

usd_krw, krx_list = load_all_base_data()

# [입력창] 종목코드
symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 IONQ)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()
            
            # [종목명 강제 확인]
            stock_name = symbol
            if not is_us and not krx_list.empty:
                match = krx_list[krx_list['Code'] == symbol]
                if not match.empty: stock_name = str(match['Name'].values[0])

            # --- [4대 지수 정밀 계산] ---
            # 1. Bollinger Bands
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            # 2. RSI (14)
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); rsi_val = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            # 3. MACD
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_val = float((exp12 - exp26).iloc[-1]); sig_val = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            # 4. Williams %R
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr_val = float(((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100)

            # [출력 1] 종목명 및 가격
            st.header(f"🏢 {stock_name} ({symbol})")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # [출력 2] 신호등 (매수/매도 시점)
            is_buy = curr_p <= lo_b or rsi_val < 35 or wr_val < -80
            is_sell = curr_p >= up_b or rsi_val > 65 or wr_val > -20
            
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 (적기)</div>", unsafe_allow_html=True)
                msg = "현재 가격은 충분히 저렴하며, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            elif is_sell:
                st.markdown("<div class='signal-box sell'>🟢 매도 검토 (수익실현)</div>", unsafe_allow_html=True)
                msg = "단기 고점에 도달했습니다. **수익을 챙길 준비**를 하세요."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기 (보유)</div>", unsafe_allow_html=True)
                msg = "방향성을 탐색하며 숨을 고르는 구간입니다. 기존 추세를 유지하세요."

            st.markdown(f"<div class='trend-card'><b>종합 추세 분석:</b> {msg}</div>", unsafe_allow_html=True)

            # [출력 3] 상세 수치 (LargeUtf8 에러 방지를 위해 문자열로 강제 변환)
            st.write("### 📋 핵심 지수 상세 수치 리포트")
            summary_dict = {
                "지수 항목": ["현재가(Bollinger)", "RSI (투자심리)", "MACD (추세에너지)", "Williams %R (바닥지표)"],
                "정밀 수치": [f"{curr_p:,.2f}", f"{rsi_val:.2f}", f"{macd_val:.2f}", f"{wr_val:.2f}"],
                "상태 진단": [
                    "하단 지지선 근처" if curr_p < lo_b else "밴드 중심 위치",
                    "과매도(바닥권)" if rsi_val < 30 else "정상 범위",
                    "에너지 상승중" if macd_val > sig_val else "에너지 하락중",
                    "단기 바닥 확인" if wr_val < -80 else "심리 안정"
                ]
            }
            st.table(pd.DataFrame(summary_dict))

    except Exception as e:
        st.error(f"분석기 실행 중 오류 발생: {e}")

# [기능 2] 오늘 검색한 종목 기록
st.write("---")
st.subheader("📜 오늘 검색한 종목 기록")
if st.session_state['history']:
    cols = st.columns(5)
    for i, h_sym in enumerate(st.session_state['history'][:10]):
        with cols[i % 5]:
            if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
                st.session_state['target'] = h_sym
                st.rerun()
