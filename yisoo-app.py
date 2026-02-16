import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 및 부드러운 디자인 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-bottom: 20px; }
    h1, h2, h3 { color: #1E3A8A !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '방탄' 분석기 v3100")

# [기능 1] 환율 및 종목 리스트 캐싱
@st.cache_data(ttl=3600)
def load_base_data():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    try: krx = fdr.StockListing('KRX')[['Code', 'Name']]
    except: krx = pd.DataFrame()
    return rate, krx

usd_krw, krx_list = load_base_data()

# [기능 2] 종목명 확인 함수
def get_name(sym, krx_df):
    if not sym.isdigit(): return sym
    if not krx_df.empty:
        match = krx_df[krx_df['Code'] == sym]
        if not match.empty: return match['Name'].values[0]
    return f"종목({sym})"

symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 NVDA)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        # 데이터 수집
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = df['close'].iloc[-1]
            is_us = not symbol.isdigit()
            stock_name = get_name(symbol, krx_list)
            
            # [출력 1] 종목명 및 가격 (원/달러 환산 포함)
            st.header(f"🏢 {stock_name} ({symbol})")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
                st.caption(f"적용 환율: 1달러당 {usd_krw:,.1f}원")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # 기술 지표 계산
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
            
            # [출력 2] 신호등 및 부드러운 분석 문구
            is_buy = curr_p <= lo_b.iloc[-1] or wr < -80
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
                msg = "가격 메리트가 매우 높지만, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)
                msg = "현재는 추세를 관망하며 에너지를 응축하는 구간입니다."

            # 분석 카드를 명확하게 출력
            st.markdown(f"<div class='trend-card'><b>종합 분석:</b> {msg}</div>", unsafe_allow_html=True)

            # [출력 3] 지수 분석 상세 테이블 (숫자 강제 노출)
            st.write("### 📋 핵심 지수 분석 결과")
            index_summary = pd.DataFrame({
                "지수 항목": ["MACD 에너지", "Williams %R", "현재가 수치"],
                "분석 데이터": [
                    "상승세" if macd.iloc[-1] > signal.iloc[-1] else "하락세",
                    f"{wr:.2f} (바닥권)" if wr < -80 else f"{wr:.2f}",
                    f"{curr_p:,.0f}원" if not is_us else f"${curr_p:,.2f}"
                ],
                "최종 판단": [
                    "상승 에너지 확보" if macd.iloc[-1] > signal.iloc[-1] else "추세 확인 대기",
                    "단기 과매도 완료" if wr < -80 else "심리 안정 구간",
                    "안전 마진 확보" if curr_p < lo_b.iloc[-1] else "밴드 내 위치"
                ]
            })
            st.table(index_summary)

        else: st.warning("데이터 로딩에 실패했습니다. 코드를 다시 확인해 주세요.")
    except Exception as e:
        st.error(f"분석기 실행 중 오류가 발생했습니다: {e}")
