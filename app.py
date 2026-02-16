import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    .history-item { padding: 10px; border-bottom: 1px solid #EEE; font-size: 18px; color: #1E3A8A; }
    h1, h2, h3 { color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 검색 기록 저장 창고 만들기 (기억 장치)
if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("👨‍💻 이수할아버지의 '기억하는' 분석기")

# 3. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            # 검색 기록에 추가 (중복 제거)
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 가져오기 (비상용 로직 포함)
            stock_name = symbol
            try:
                # 한국 주식 리스트에서 이름 찾기
                krx = fdr.StockListing('KRX')
                name_row = krx[krx['Code'] == symbol]
                if not name_row.empty: stock_name = name_row.iloc[0]['Name']
            except: pass

            df = df.tail(30)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100

            # 4. 출력 (종목명 + 코드)
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"🏢 종목: {stock_name} ({symbol})")
            st.write(f"### 현재가: {price_txt}")
            
            if rsi < 35 or wr < -80:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or wr > -20:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 5. 지수 테이블
            st.table(pd.DataFrame({
                "지표 항목": ["RSI 강도", "Williams %R", "추세"],
                "수치": [f"{rsi:.1f}", f"{wr:.1f}", "상승" if rsi > 50 else "하락"],
                "진단": ["저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "안정"]
            }))
    except:
        st.error("데이터를 불러올 수 없습니다.")

# 6. 검색 기록 표시 (하단)
st.write("---")
st.subheader("📜 오늘 검색한 종목 (기억)")
for item in st.session_state['history'][:5]: # 최근 5개만 표시
    st.markdown(f"<div class='history-item'>✅ {item}</div>", unsafe_allow_html=True)
