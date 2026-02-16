import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정 (부드럽고 직관적인 고대비 스타일)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; }
    h1, h2, h3 { color: #1E3A8A !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '지수 복구' 분석기 v2700")

# 실시간 환율 정보 (미장 환산용)
try:
    usd_krw = fdr.DataReader('USD/KRW').iloc[-1]['close']
except:
    usd_krw = 1350.0

symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 IONQ)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = df['close'].iloc[-1]
            is_us = not symbol.isdigit()
            
            st.header(f"🏢 {symbol} 분석 결과")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # --- [핵심 지표 계산] ---
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
            
            # --- [신호등 및 부드러운 진단] ---
            is_buy = curr_p <= lo_b.iloc[-1] or wr < -80
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
                msg = "현재 가격은 충분히 저렴하지만, 에너지는 **조심스럽게 바닥을 확인 중**에 있습니다."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)
                msg = "추세를 관망하며 숨을 고르는 중입니다."

            st.markdown(f<div class='trend-card'><b>종합 의견:</b> {msg}</div>, unsafe_allow_html=True)

            # --- [선생님이 찾으시던 지수 분석 결과 표] ---
            st.write("### 📋 핵심 지수 분석 결과 (상세)")
            
            # 데이터를 명확하게 구성
            index_data = {
                "지수 항목": ["MACD 에너지", "Williams %R", "Bollinger Band"],
                "상세 수치": [
                    "상승세" if macd.iloc[-1] > signal.iloc[-1] else "하락세",
                    f"{wr:.1f} (과매도)" if wr < -80 else f"{wr:.1f}",
                    "하단 돌파" if curr_p < lo_b.iloc[-1] else "밴드 내 위치"
                ],
                "최종 판단": [
                    "추세 반전 대기" if macd.iloc[-1] < signal.iloc[-1] else "상승 에너지 확보",
                    "단기 바닥 확인" if wr < -80 else "심리 안정 구간",
                    "안전 마진 확보" if curr_p < lo_b.iloc[-1] else "추세 추종 구간"
                ]
            }
            st.table(pd.DataFrame(index_data)) # 표를 강제로 출력

        else: st.warning("데이터를 가져오지 못했습니다.")
    except Exception as e:
        st.error(f"지수 분석 중 오류가 발생했습니다: {e}")
