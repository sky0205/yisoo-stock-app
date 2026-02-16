import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 및 대형 글자 스타일 (선생님 맞춤형)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 42px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 기억 장치 설정
if 'history' not in st.session_state: st.session_state['history'] = []
if 'sel_sym' not in st.session_state: st.session_state['sel_sym'] = "005930"

st.title("👨‍💻 이수할아버지의 철벽 분석기 v1700")

# 3. 종목 입력창
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['sel_sym']).strip().upper()

# 4. 분석 엔진
if symbol:
    try:
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            # 검색 기록에 추가
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 가져오기
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                stock_name = krx[krx['Code'] == symbol].iloc[0]['Name']
            except: pass

            df = df.tail(100)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            
            exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()

            # 5. [출력] 종목명과 신호등
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"🏢 {stock_name} ({symbol})")
            st.write(f"## 현재가: {price_txt}")

            if rsi < 35 or wr < -80:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 적기</div>", unsafe_allow_html=True)
            elif rsi > 65 or wr > -20:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 대기</div>", unsafe_allow_html=True)

            # 6. [지수 테이블]
            st.table(pd.DataFrame({
                "항목": ["RSI 강도", "Williams %R", "MACD 추세"],
                "수치": [f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd.iloc[-1] > signal.iloc[-1] else "하락"],
                "판단": ["저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "안정"]
            }))

            # 7. [추세 진단]
            st.markdown(f"""<div class='trend-card'><b>추세 진단:</b> {stock_name}은(는) 현재 RSI {rsi:.1f}로 
            {'과열 구간입니다. 분할 익절을 준비하세요.' if rsi > 70 else '바닥 구간입니다. 매수를 고려하세요.' if rsi < 30 else '안정적인 추세 유지 중입니다.'}</div>""", unsafe_allow_html=True)
    except:
        st.error("데이터를 가져오는 중입니다. 종목코드를 다시 확인해 주세요.")

# 8. [검색 기록 - 에러 방지용 버튼]
st.write("---")
st.subheader("📜 오늘 검색한 종목 (누르면 분석)")
if st.session_state['history']:
    cols = st.columns(5)
    for i, h_sym in enumerate(st.session_state['history'][:10]):
        with cols[i % 5]:
            # 버튼마다 고유한 key를 부여하여 에러 방지
            if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
                st.session_state['sel_sym'] = h_sym
                st.rerun()
