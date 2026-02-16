import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import yfinance as yf

# 1. 고대비 스타일 및 대형 글자
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F1F5F9; border-left: 10px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 기억 장치 (오늘 검색한 종목)
if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("👨‍💻 이수할아버지의 통합 분석기 v1400")

# 3. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        # 데이터 가져오기 (한국/미국 통합 시도)
        if symbol.isdigit():
            df = fdr.DataReader(symbol).tail(100)
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                stock_name = krx[krx['Code'] == symbol].iloc[0]['Name']
            except: pass
        else:
            df = yf.download(symbol, period="6mo").tail(100)
            stock_name = symbol

        if not df.empty:
            # 기록 저장
            display_name = f"{stock_name} ({symbol})"
            if display_name not in st.session_state['history']:
                st.session_state['history'].insert(0, display_name)

            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산: RSI ($RSI = 100 - \frac{100}{1 + RS}$)
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100

            # 4. 출력
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"🏢 {display_name}")
            st.write(f"## 현재가: {price_txt}")

            if rsi < 35 or wr < -80:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or wr > -20:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 5. 지표 테이블
            st.write("### 📋 4대 전문 지표 정밀 진단")
            st.table(pd.DataFrame({
                "지표 항목": ["RSI 강도", "Williams %R", "추세"],
                "분석 수치": [f"{rsi:.1f}", f"{wr:.1f}", "상승" if rsi > 50 else "하락"],
                "기술적 판단": ["저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "안정"]
            }))
    except:
        st.info("🔄 데이터를 불러오는 중입니다. 잠시 후 종목코드를 다시 입력해 주세요.")

# 6. 검색 기록
st.write("---")
st.subheader("📜 오늘 검색한 종목 (기억)")
for item in st.session_state['history'][:5]:
    st.markdown(f"✅ {item}")
