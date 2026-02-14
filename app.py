import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치
st.set_page_config(page_title="이수 Stock Analyzer v131", layout="wide")

if 'my_stocks' not in st.session_state:
    st.session_state.my_stocks = {"삼성전자": "005930", "아이온큐": "IONQ", "현대차": "005380", "엔비디아": "NVDA"}
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "005930"

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-top: 20px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면 상단
st.title("👨‍💻 주식 분석기 v131 (국내 데이터 엔진 교체)")
st.write("---")

u_input = st.text_input("🔍 종목 번호(6자리)나 티커 입력 후 엔터 (예: 000660)", key="main_search")

if u_input:
    code = u_input.upper().strip()
    st.session_state.my_stocks[code] = code
    st.session_state.active_ticker = code
    st.rerun()

# 3. 리스트 선택
opts = list(st.session_state.my_stocks.keys())
sel_name = st.selectbox("📋 오늘 분석 리스트", options=opts, index=opts.index(st.session_state.active_ticker) if st.session_state.active_ticker in opts else 0)
ticker = st.session_state.my_stocks[sel_name]

# 4. 국내 데이터 전용 엔진 (FinanceDataReader 사용)
@st.cache_data(ttl=60)
def fetch_local_v131(t):
    try:
        # 야후를 거치지 않고 네이버/KRX 등에서 직접 데이터를 가져옵니다.
        df = fdr.DataReader(t, '2023') 
        if df is not None and not df.empty:
            df = df.reset_index()
            # 열 이름을 소문자로 통일
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except:
        return None
    return None

if ticker:
    with st.spinner('국내 데이터 서버에서 정보를 가져오는 중...'):
        df = fetch_local_v131(ticker)
        
    if df is not None:
        close = df['close']
        # 지표 계산 ($$RSI = 100 - \frac{100}{1+RS}$$)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # MACD: $$MACD = EMA_{12} - EMA_{26}$$
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        up, lo = ma20 + (std20 * 2), ma20 - (std20 * 2)

        # [A] 결론 신호등
        st.write("---")
        if rsi.iloc[-1] <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {sel_name}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {sel_name}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침
        m_up = macd.iloc[-1] > sig.iloc[-1]; a_up = close.iloc[-1] > ma20.iloc[-1]
        memo = f"🚩 **{sel_name} 대응 지침**<br>"
        if a_up: memo += "✅ **이평선**: 주가가 빨간 20일선 위에 있어 안전합니다.<br>"
        else: memo += "❌ **이평선**: 아직 20일선 아래에 있습니다. 반등을 더 기다리세요.<br>"
        if m_up: memo += "✅ **기세**: MACD가 상승 신호를 유지하고 있습니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 차트 출력
        st.metric("현재가", f"{close.iloc[-1]:,.0f}원" if ticker.isdigit() else f"${close.iloc[-1]:,.2f}")
        
        # 볼린저 밴드 차트
        c_df = df.tail(100).reset_index()
        c_df['MA20'] = ma20.tail(100).values; c_df['Upper'] = up.tail(100).values; c_df['Lower'] = lo.tail(100).values
        base = alt.Chart(c_df).encode(x='date:T')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((line + ma_line).properties(height=500), use_container_width=True)
    else:
        st.error(f"⚠️ '{sel_name}' 데이터를 가져올 수 없습니다. 코드 맨 위에 'pip install finance-datareader' 명령어가 필요한 환경인지 확인해 보세요.")

with st.sidebar:
    if st.button("🗑️ 모든 기록 리셋"):
        st.session_state.clear()
        st.rerun()
