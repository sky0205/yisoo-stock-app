import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 시인성 극대화 스타일 (글자 색상 및 배경 고정)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #000000 !important; padding: 25px; background: #F0F4F8; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 25px; }
    h1, h2, h3, p, span, div { color: #1E3A8A !important; font-weight: bold !important; }
    th, td { color: #000000 !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# [세션 관리] 오늘 검색 기록 및 대상 종목
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '최종 통합' 분석기 v8000")

# [기능 1] 데이터 로드 (환율 및 종목명 리스트)
@st.cache_data(ttl=3600)
def load_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame(columns=['Code', 'Name'])
    return rate, krx

usd_krw, krx_list = load_base_data()

# [입력창]
symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 IONQ)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        # 최근 120일 데이터 수집
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            # 검색 기록 업데이트
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()
            
            # [종목명 추출]
            stock_name = symbol
            if not is_us and not krx_list.empty:
                match = krx_list[krx_list['Code'] == symbol]
                if not match.empty: stock_name = match['Name'].values[0]

            # --- [4대 지수 정밀 계산] ---
            # 1. 볼린저 밴드
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20.iloc[-1] - (std20.iloc[-1] * 2); up_b = ma20.iloc[-1] + (std20.iloc[-1] * 2)
            # 2. RSI (14)
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); rs = gain / loss
            rsi_val = 100 - (100 / (1 + rs)).iloc[-1]
            # 3. MACD
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_val = (exp12 - exp26).iloc[-1]; signal_val = (exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1]
            # 4. Williams %R
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr_val = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100

            # [출력 1] 종목명 및 가격 (강제 표시)
            st.header(f"🏢 {stock_name} ({symbol})")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
                st.caption(f"적용 환율: 1달러당 {usd_krw:,.1f}원")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # [출력 2] 신호등 (매수/매도 적기)
            is_buy = curr_p <= lo_b or rsi_val < 35 or wr_val < -80
            is_sell = curr_p >= up_b or rsi_val > 65 or wr_val > -20
            
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
                msg = "가격이 매우 매력적인 바닥권이며, 현재 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            elif is_sell:
                st.markdown("<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
                msg = "단기 고점에 도달하여 에너지가 과열되었습니다. 수익 실현을 준비하세요."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)
                msg = "방향성을 탐색하며 숨을 고르는 구간입니다. 기존 추세를 유지하세요."

            st.markdown(f"<div class='trend-card'><b>종합 추세 분석:</b> {msg}</div>", unsafe_allow_html=True)

            # [출력 3] 상세 수치 표 (숫자 강제 노출)
            st.write("### 📋 핵심 지수 상세 수치 리포트")
            index_df = pd.DataFrame({
                "지수 항목": ["현재가(Bollinger)", "RSI (투자심리)", "MACD (추세에너지)", "Williams %R (바닥지표)"],
                "정밀 수치": [f"{curr_p:,.2f}", f"{rsi_val:.2f}", f"{macd_val:.2f}", f"{wr_val:.2f}"],
                "상태 진단": [
                    "하단 지지선 근처" if curr_p < lo_b else "밴드 중심 위치",
                    "과매도(바닥권)" if rsi_val < 30 else "정상 범위",
                    "상승 에너지 우위" if macd_val > signal_val else "하락 에너지 잔존",
                    "단기 바닥 확인" if wr_val < -80 else "심리 안정"
                ]
            })
            st.table(index_df) # 표를 통해 수치를 확실히 보여줌

        else: st.warning("데이터를 가져오지 못했습니다. 종목코드를 다시 확인해 주세요.")
    except Exception as e:
        st.error(f"분석기 실행 중 오류 발생: {e}")

# [기능 2] 오늘 검색한 종목 기록 (하단 고정)
st.write("---")
st.subheader("📜 오늘 검색한 종목 기록")
if st.session_state['history']:
    cols = st.columns(5)
    for i, h_sym in enumerate(st.session_state['history'][:10]):
        with cols[i % 5]:
            if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
                st.session_state['target'] = h_sym
                st.rerun()
else:
    st.write("아직 검색한 종목이 없습니다.")
