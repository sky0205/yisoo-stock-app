import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 (군더더기 없는 큰 글씨 모드)
st.set_page_config(page_title="이수 주식마스터 v163", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .status-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 25px; }
    .info-text { font-size: 20px; line-height: 1.8; color: #1F2937; }
    .stButton>button { width: 100%; height: 70px; font-size: 22px; font-weight: bold; background-color: #F3F4F6; border: 2px solid #D1D5DB; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 명품 주식분석기")
st.write(f"### 📅 분석 일시: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
st.write("---")

# 2. 선생님의 4대 핵심 종목 (바로가기 버튼)
st.write("#### 🔍 내 주식 바로 분석하기 (버튼을 누르세요)")
c1, c2, c3, c4 = st.columns(4)

if 't_code' not in st.session_state: st.session_state.t_code = "005930"

if c1.button("📱 삼성전자"): st.session_state.t_code = "005930"
if c2.button("📦 쿠팡"): st.session_state.t_code = "CPNG"
if c3.button("⚛️ 아이온큐"): st.session_state.t_code = "IONQ"
if c4.button("🎬 넷플릭스"): st.session_state.t_code = "NFLX"

# 직접 입력창 (글씨 크게)
t_input = st.text_input("📊 다른 종목 번호 직접 입력", value=st.session_state.t_code)
ticker = t_input.strip()

# 3. 데이터 분석 및 결과 표시
@st.cache_data(ttl=60)
def get_data(t):
    try:
        if t.isdigit(): df = fdr.DataReader(t, '2024')
        else: df = yf.download(t, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None

if ticker:
    df = get_data(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close'].iloc[-1]
        
        # RSI 계산 (매수/매도 타이밍)
        # $$RSI = 100 - \frac{100}{1 + \frac{\text{Average Gain}}{\text{Average Loss}}}$$
        diff = df['close'].diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]

        # [결론 판정]
        st.write("---")
        if rsi <= 35:
            st.markdown(f"<div class='status-box' style='border:8px solid #FF4B4B; background-color:#FFF5F5; color:#FF4B4B;'>🚨 {ticker}: 지금 매수 추천 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-box' style='border:8px solid #6B7280; background-color:#F9FAFB; color:#6B7280;'>🟡 {ticker}: 관망 대기 중 🟡</div>", unsafe_allow_html=True)

        # 삼성전자 전용: 수익률 계산
        if ticker == "005930":
            p_rate = ((close - 58000) / 58000) * 100
            st.info(f"💡 현재가 {close:,.0f}원 기준, 선생님의 평단가(58,000원) 대비 수익률은 **{p_rate:.2f}%** 입니다.")

        # 차트
        chart = alt.Chart(df.tail(120)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        ).properties(height=500)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("⚠️ 종목을 찾을 수 없습니다. 번호를 다시 확인해 주세요.")
