import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v104", layout="wide")

# 오늘 본 종목을 기억하는 바구니
if 'fav_list' not in st.session_state:
    st.session_state.fav_list = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
if 'target' not in st.session_state:
    st.session_state.target = "005930.KS"

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면: 제목과 검색창 (에러와 상관없이 무조건 보이게)
st.title("👨‍💻 이수할아버지의 주식분석기 v104")
st.write("---")

# 검색창과 리스트를 나란히 배치
c1, c2 = st.columns([2, 2])
with c1:
    st.subheader("🔍 새로운 종목 번호 입력")
    u_input = st.text_input("숫자 6자리 입력 후 엔터 (예: 000660)", key="search")
    if u_input:
        code = u_input.upper().strip()
        full_code = code + ".KS" if (code.isdigit() and len(code) == 6) else code
        st.session_state.fav_list[full_code] = full_code
        st.session_state.target = full_code
        st.rerun()

with c2:
    st.subheader("📋 오늘 분석 중인 종목들")
    opts = list(st.session_state.fav_list.keys())
    sel = st.selectbox("다시 볼 종목 선택", options=opts, index=opts.index(st.session_state.target) if st.session_state.target in opts else 0)
    st.session_state.target = st.session_state.fav_list[sel]

st.write("---")

# 3. 데이터 로딩 및 분석 (에러 방지용 try-except 사용)
try:
    ticker = st.session_state.target
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
    
    if df is not None and not df.empty:
        # 데이터 정리
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        # 지표 계산
        close = df['close']
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

        # [A] 결론 신호등
        last_rsi = rsi.iloc[-1]
        if last_rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 (바닥권) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침
        curr_p = close.iloc[-1]; macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]
        memo = f"🚩 **{ticker} 투자 대응 전략**<br>"
        if ma20_up: memo += "✅ **이평선**: 주가가 중간선(빨간선) 위로 올라왔습니다. 매수 시점!<br>"
        else: memo += "❌ **이평선**: 아직 중간선 아래에 있으니 반등을 확인하세요.<br>"
        if macd_up: memo += "✅ **기세**: 파란선(MACD)이 주황선 위에 있어 보유가 유리합니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 상세 수표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{close.max():,.0f}" if ".K" in ticker else f"{close.max():,.2f}")

        # [D] 차트
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else:
        st.warning("⚠️ 데이터를 가져오는 중입니다. 잠시만 기다려주세요 (F5를 눌러도 좋습니다).")
except Exception as e:
    st.error(f"⚠️ 시스템 오류가 발생했습니다. '번역 기능'을 끄고 다시 시도해 보세요. (에러: {e})")

with st.sidebar:
    if st.button("🗑️ 전체 초기화"):
        st.session_state.clear()
        st.rerun()
