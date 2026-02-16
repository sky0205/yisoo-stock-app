import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 스타일 설정 (흰 바탕, 파란 버튼)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div.stButton > button {
        background-color: white !important;
        color: #1E3A8A !important;
        border: 2px solid #1E3A8A !important;
        font-weight: bold !important;
        width: 100%;
    }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3 { color: #1E3A8A !important; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B !important; padding: 20px; background: #F8FAFC; border-left: 10px solid #1E3A8A; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 저장 창고 (에러 방지용)
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👨‍💻 이수할아버지의 철벽 분석기 v1900")

# 3. 종목 입력창
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['target']).strip().upper()

# 4. 분석 엔진 (에러 차단 try-except 적용)
if symbol:
    try:
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 찾기
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                stock_name = krx[krx['Code'] == symbol].iloc[0]['Name']
            except: pass

            df = df.tail(100)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산 (볼린저 밴드 수치)
            ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
            up_b = ma20 + (std20 * 2); lo_b = ma20 - (std20 * 2)
            
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            
            # 5. 출력
            curr_p = close.iloc[-1]
            st.subheader(f"🏢 {stock_name} ({symbol}) | 현재가: {curr_p:,.2f}{unit}")

            if rsi < 35 or curr_p <= lo_b.iloc[-1]:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권</div>", unsafe_allow_html=True)
            elif rsi > 65 or curr_p >= up_b.iloc[-1]:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 대기</div>", unsafe_allow_html=True)

            # 6. 볼린저 수치 및 지수 테이블 (요청 사항)
            st.write("### 📋 핵심 지표 및 볼린저 밴드 수치")
            st.table(pd.DataFrame({
                "항목": ["현재가", "볼린저 상단", "볼린저 하단", "RSI 강도"],
                "수치": [f"{curr_p:,.2f}{unit}", f"{up_b.iloc[-1]:,.2f}{unit}", f"{lo_b.iloc[-1]:,.2f}{unit}", f"{rsi:.1f}"],
                "진단": ["-", "강한 저항", "강한 지지", "과열" if rsi > 70 else "바닥" if rsi < 30 else "안정"]
            }))

            # 7. 추세 분석 (요청 사항)
            st.write("### 📉 종합 추세 분석")
            trend_txt = "상승 추세가 이어지고 있습니다." if rsi > 50 else "하락 압력이 지속되는 중입니다."
            st.markdown(f"<div class='trend-card'><b>분석:</b> {stock_name}은 {trend_txt}<br><b>전략:</b> 볼린저 하단({lo_b.iloc[-1]:,.0f}) 근처에서 분할 매수를 검토하세요.</div>", unsafe_allow_html=True)
    except:
        st.info("데이터를 불러오는 중입니다. 잠시 후 다시 시도해 주세요.")

# 8. 검색 기록 버튼 (흰 바탕/파란 글씨)
st.write("---")
st.subheader("📜 오늘 검색한 종목 (눌러서 다시 분석)")
if st.session_state['history']:
    cols = st.columns(5)
    for i, h_sym in enumerate(st.session_state['history'][:10]):
        with cols[i % 5]:
            if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
                st.session_state['target'] = h_sym
                st.rerun()
