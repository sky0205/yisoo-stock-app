import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 (흰 바탕, 파란 버튼, 대형 텍스트)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div.stButton > button { background-color: white !important; color: #1E3A8A !important; border: 2px solid #1E3A8A !important; font-weight: bold !important; width: 100%; border-radius: 8px; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 42px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👨‍💻 이수할아버지의 '핵심 요약' 분석기 v2200")

# 2. 종목 입력
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            if symbol not in st.session_state['history']: st.session_state['history'].insert(0, symbol)
            
            # 종목명 찾기
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                match = krx[krx['Code'] == symbol]
                if not match.empty: stock_name = match.iloc[0]['Name']
            except: pass

            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산 1: 볼린저 밴드 (판단용으로만 사용)
            ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
            up_b = ma20 + (std20 * 2); lo_b = ma20 - (std20 * 2)
            
            # 지표 계산 2: MACD ($EMA_{12} - EMA_{26}$)
            exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            
            # 지표 계산 3: Williams %R
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            
            # 지표 계산 4: RSI
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]

            # 3. [출력] 종목명 및 신호등
            curr_p = close.iloc[-1]
            st.header(f"🏢 {stock_name} ({symbol}) | 현재가: {curr_p:,.2f}{unit}")

            # 신호등 판단 로직 (볼린저 밴드 + 윌리엄 지수 결합)
            if curr_p <= lo_b.iloc[-1] or wr < -80:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif curr_p >= up_b.iloc[-1] or wr > -20:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기 (횡보)</div>", unsafe_allow_html=True)

            # 4. [핵심 지수 테이블] - 볼린저 수치 제외, MACD/윌리엄 추가
            st.write("### 📋 전문 지표 정밀 진단")
            st.table(pd.DataFrame({
                "항목": ["MACD 추세", "Williams %R", "RSI 강도", "현재가 위치"],
                "분석 수치": [
                    "상승 (골든크로스)" if macd.iloc[-1] > signal.iloc[-1] else "하락 (데드크로스)",
                    f"{wr:.1f}",
                    f"{rsi:.1f}",
                    "밴드 상단 근접" if curr_p > ma20.iloc[-1] else "밴드 하단 근접"
                ],
                "진단 결과": [
                    "매수세 우세" if macd.iloc[-1] > signal.iloc[-1] else "매도세 우세",
                    "과매도(바닥)" if wr < -80 else "과매수(천장)" if wr > -20 else "보통",
                    "저평가" if rsi < 30 else "고평가" if rsi > 70 else "적정",
                    "조정 가능성" if curr_p > up_b.iloc[-1] else "반등 가능성" if curr_p < lo_b.iloc[-1] else "안정"
                ]
            }))

            # 5. [추세 정밀 진단] (요청하신 기능)
            st.write("### 📉 종합 추세 분석 보고서")
            macd_msg = "📈 **상승 추세 강화:** MACD가 시그널 선 위에 있어 에너지가 좋습니다." if macd.iloc[-1] > signal.iloc[-1] else "📉 **하락 추세 지속:** 에너지가 약해지고 있어 보수적인 접근이 필요합니다."
            st.markdown(f"""
            <div class='trend-card'>
                <b>1. 추세 방향:</b> {macd_msg}<br>
                <b>2. 윌리엄 판단:</b> {wr:.1f} 수준으로 현재는 {"기술적 반등을 노릴 바닥" if wr < -80 else "이익 실현을 준비할 고점"} 부근입니다.<br>
                <b>3. 종합 전략:</b> 볼린저 밴드 하단 지지 여부를 내부적으로 확인한 결과, {"지금이 분할 매수 적기" if curr_p < lo_b.iloc[-1] else "관망하며 지켜볼 때"}입니다.
            </div>
            """, unsafe_allow_html=True)
    except:
        st.error("데이터 로딩 중입니다.")

# 6. 검색 기록 (흰 바탕/파란 버튼)
st.write("---")
st.subheader("📜 오늘 검색한 종목 리스트")
cols = st.columns(5)
for i, h_sym in enumerate(st.session_state['history'][:10]):
    with cols[i % 5]:
        if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
            st.session_state['target'] = h_sym
            st.rerun()
