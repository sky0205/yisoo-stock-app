import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정 (부드러운 디자인 유지)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B; padding: 20px; background: #F8FAFC; border-left: 10px solid #1E3A8A; border-radius: 10px; }
    h1, h2, h3 { color: #1E3A8A !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '부드러운' 글로벌 분석기 v2600")

# 실시간 환율 정보 (미장 분석용)
try:
    usd_krw = fdr.DataReader('USD/KRW').iloc[-1]['close']
except:
    usd_krw = 1350.0

symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 IONQ)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        # 데이터 수집
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = df['close'].iloc[-1]
            is_us = not symbol.isdigit() # 미국 주식 여부
            
            st.header(f"🏢 {symbol} 분석 결과")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
                st.caption(f"기준 환율: 1달러당 {usd_krw:,.1f}원 적용")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # 지수 계산 (MACD, Williams %R, Bollinger)
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
            
            # 신호등 및 부드러운 진단
            is_buy = curr_p <= lo_b.iloc[-1] or wr < -80
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
                msg = "현재 가격은 충분히 매력적이지만, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)
                msg = "추세를 관망하며 숨을 고르는 중입니다."

            st.markdown(f"<div class='trend-card'><b>종합 의견:</b> {msg}</div>", unsafe_allow_html=True)

            # 지수 테이블 (선생님이 요청하신 부분)
            st.write("### 📋 핵심 지수 분석 결과")
            st.table(pd.DataFrame({
                "지수 항목": ["MACD 에너지", "Williams %R", "현재가 위치"],
                "수치 결과": ["상승" if macd.iloc[-1] > signal.iloc[-1] else "하락", f"{wr:.1f}", "밴드 하단" if curr_p < ma20.iloc[-1] else "밴드 상단"],
                "판단": ["매수 우세" if macd.iloc[-1] > signal.iloc[-1] else "매도 우세", "바닥권" if wr < -80 else "보통", "안전 마진" if curr_p < lo_b.iloc[-1] else "조정 주의"]
            }))
        else: st.warning("데이터가 없습니다.")
    except Exception as e:
        st.error(f"코드 실행 중 오류가 발생했습니다: {e}")
