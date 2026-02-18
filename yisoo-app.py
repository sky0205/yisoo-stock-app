import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정 (박스 디자인 및 글자 크기 대폭 강화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; font-size: 45px !important; font-weight: 900; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 4대 지수 전용 박스 스타일 */
    .indicator-card {
        background: #F8FAFC;
        border: 2px solid #E2E8F0;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .indicator-title { font-size: 18px; color: #64748B; font-weight: bold; margin-bottom: 5px; }
    .indicator-value { font-size: 28px; color: #1E3A8A; font-weight: 900; }
    
    .trend-card { font-size: 24px; line-height: 1.6; color: #1E293B !important; padding: 25px; background: #F1F5F9; border-left: 15px solid #1E3A8A; border-radius: 12px; margin-bottom: 20px; }
    .value-card { font-size: 30px; font-weight: 900; color: #FFFFFF !important; padding: 25px; background: #1E3A8A; border-radius: 15px; text-align: center; margin-bottom: 30px; }
    
    h1, h2, h3 { color: #1E3A8A !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👨‍💻 v36000: 지표 박스 & 정밀 분석기")

@st.cache_data(ttl=3600)
def load_base_info():
    try: rate = fdr.DataReader('USD/KRW').iloc[-1]['close']
    except: rate = 1350.0
    return float(rate)

usd_krw = load_base_info()
symbol = st.text_input("📊 종목코드 또는 티커 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            if symbol in st.session_state['history']: st.session_state['history'].remove(symbol)
            st.session_state['history'].insert(0, symbol)
            st.session_state['target'] = symbol
            
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()

            # 4대 지표 정밀 계산
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = float((exp12 - exp26).iloc[-1]); sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr = float(((h14.iloc[-1] - curr_p) / (h14.iloc[-1] - l14.iloc[-1])) * -100)

            # [1] 상단 현재가 및 신호등
            st.header(f"🏢 분석 종목: {symbol}")
            price_display = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.subheader(f"현재가: {price_display}")

            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 사정권 (바닥 진입)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (어깨 돌파)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 및 유지 (중립)</div>", unsafe_allow_html=True)

            # [2] 4대 핵심 지표 박스 정리
            st.write("### 📋 4대 핵심 지표 박스 브리핑")
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            
            with col1:
                st.markdown(f"""<div class='indicator-card'><div class='indicator-title'>볼린저 밴드</div>
                <div class='indicator-value'>{'하단 지지' if curr_p < lo_b else '상단 저항' if curr_p > up_b else '안정권'}</div></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class='indicator-card'><div class='indicator-title'>RSI 심리도</div>
                <div class='indicator-value'>{rsi:.1f} ({'과매도' if rsi < 35 else '과매수' if rsi > 65 else '정상'})</div></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class='indicator-card'><div class='indicator-title'>MACD 추세</div>
                <div class='indicator-value'>{'상승 가속' if macd > sig else '하락 가속'}</div></div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class='indicator-card'><div class='indicator-title'>Williams %R</div>
                <div class='indicator-value'>{wr:.1f} ({'바닥권' if wr < -80 else '고점권' if wr > -20 else '중간'})</div></div>""", unsafe_allow_html=True)

            # [3] 현 상황 정밀 진단
            st.write("### 🔍 현 상황 정밀 진단 보고서")
            analysis = []
            if rsi < 35: analysis.append("현재 시장의 공포가 극에 달해 심리적 저점 구간에 진입했습니다.")
            if curr_p < lo_b: analysis.append("가격이 통계적 변동 범위를 벗어나 하단 지지선을 터치했습니다. 기술적 반등 가능성이 높습니다.")
            if macd > sig: analysis.append("단기 추세가 살아나며 돈의 흐름이 위로 향하고 있습니다.")
            if not analysis: analysis.append("현재 주가는 뚜렷한 방향성 없이 박스권 내에서 힘을 응축하고 있습니다.")
            
            analysis_text = " ".join(analysis)
            st.markdown(f"<div class='trend-card'><b>📋 진단 결과:</b> {analysis_text}</div>", unsafe_allow_html=True)

            # [4] 적정가 제안
            fair_v = curr_p * 1.15
            fair_display = f"${fair_v:,.2f}" if is_us else f"{fair_v:,.0f}원"
            st.markdown(f"<div class='value-card'>💎 테이버의 1차 목표가 제안: {fair_display}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"데이터를 읽어오는 중 오류가 발생했습니다: {e}")
