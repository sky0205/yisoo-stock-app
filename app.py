import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 및 대형 글자 스타일 (선생님 맞춤형)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div.stButton > button { background-color: white !important; color: #1E3A8A !important; border: 2px solid #1E3A8A !important; font-weight: bold !important; width: 100%; height: 50px; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 10px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 종목명 리스트 미리 가져오기 (속도 향상)
@st.cache_data
def get_stock_list():
    try: return fdr.StockListing('KRX')
    except: return pd.DataFrame()

# 3. 데이터 저장소
if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👨‍💻 이수할아버지의 통합 분석기 v2000")

# 4. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        # 데이터 수집
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            # 검색 기록 저장
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 복구 로직
            krx = get_stock_list()
            stock_name = symbol
            if not krx.empty and symbol.isdigit():
                match = krx[krx['Code'] == symbol]
                if not match.empty: stock_name = match.iloc[0]['Name']

            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 기술 지표 계산 ($MA_{20} \pm 2\sigma$)
            ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
            up_b = ma20 + (std20 * 2); lo_b = ma20 - (std20 * 2)
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]

            # 5. [출력] 종목명과 신호등
            curr_p = close.iloc[-1]
            st.header(f"🏢 {stock_name} ({symbol})")
            st.write(f"### 현재가: {curr_p:,.2f}{unit}")

            if rsi < 35 or curr_p <= lo_b.iloc[-1]:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or curr_p >= up_b.iloc[-1]:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 6. [수치 테이블 복구]
            st.write("### 📋 볼린저 밴드 및 주요 지수 수치")
            st.table(pd.DataFrame({
                "지표 항목": ["현재 가격", "볼린저 상단(저항)", "볼린저 하단(지지)", "RSI 강도"],
                "분석 수치": [f"{curr_p:,.2f}{unit}", f"{up_b.iloc[-1]:,.2f}{unit}", f"{lo_b.iloc[-1]:,.2f}{unit}", f"{rsi:.1f}"],
                "판단": ["-", "강한 매도 압력", "강한 매수 지지", "저점" if rsi < 30 else "고점" if rsi > 70 else "안정"]
            }))

            # 7. [추세 분석]
            st.write("### 📉 종합 추세 분석")
            trend_msg = "상승 추세가 이어지고 있습니다." if rsi > 50 else "하락 압력이 지속되는 중입니다."
            st.markdown(f"<div class='trend-card'><b>분석:</b> {stock_name}은 현재 {trend_msg}<br><b>전략:</b> RSI {rsi:.1f} 기준으로 {"분할 매수로 물량을 확보하기 좋은 지점입니다." if rsi < 35 else "추격 매수보다는 익절 타이밍을 노리세요." if rsi > 65 else "추세가 확실해질 때까지 보유 비중을 유지하세요."}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"데이터를 불러올 수 없습니다. 코드 확인: {symbol}")

# 8. 검색 기록 (흰바탕 파란 버튼)
st.write("---")
st.subheader("📜 오늘 검색한 종목 (눌러서 다시 보기)")
cols = st.columns(5)
for i, h_sym in enumerate(st.session_state['history'][:10]):
    with cols[i % 5]:
        if st.button(f"🔍 {h_sym}", key=f"btn_{h_sym}_{i}"):
            st.session_state['target'] = h_sym
            st.rerun()
