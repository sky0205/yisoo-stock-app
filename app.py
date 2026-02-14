import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치
st.set_page_config(page_title="이수 Stock Analyzer v101", layout="wide")

# 오늘 본 종목들을 [이름: 코드] 쌍으로 저장 (기본값 설정)
if 'stock_memory' not in st.session_state:
    st.session_state.stock_memory = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
if 'target_ticker' not in st.session_state:
    st.session_state.target_ticker = "005930.KS"

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면: 번호 입력 및 리스트
st.title("👨‍💻 이수할아버지의 주식분석기 v101")
st.write("---")

col_input, col_hist = st.columns([1.5, 1])

with col_input:
    st.subheader("🔍 종목 번호(6자리)나 티커 입력")
    u_input = st.text_input("번호 입력 후 엔터 (예: 000660)", key="search_bar")
    
    if u_input:
        code = u_input.upper().strip()
        # 한국 주식 번호 처리
        if code.isdigit() and len(code) == 6:
            full_code = code + ".KS"
        else:
            full_code = code
        
        # 이름은 나중에 분석 중에 찾기로 하고 일단 코드만 등록
        st.session_state.stock_memory[full_code] = full_code
        st.session_state.target_ticker = full_code
        st.rerun()

with col_hist:
    st.subheader("📋 오늘 본 종목들")
    # 오늘 검색한 기록들을 보여줍니다.
    mem_options = list(st.session_state.stock_memory.keys())
    selected_name = st.selectbox("다시 볼 종목 선택", options=mem_options, 
                                 index=mem_options.index(st.session_state.target_ticker) if st.session_state.target_ticker in mem_options else 0)
    st.session_state.target_ticker = st.session_state.stock_memory[selected_name]

# 3. 데이터 로딩 엔진 (이름 찾기를 분석 내부로 이동)
@st.cache_data(ttl=60)
def load_and_analyze_v101(ticker):
    try:
        # 데이터 수집
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df is None or df.empty: return None, None
        
        # 이름 찾기 (없어도 에러 안 나게 처리)
        try:
            name = yf.Ticker(ticker).info.get('shortName', ticker)
        except:
            name = ticker
            
        # 데이터 정리
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "") for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna(), name
    except:
        return None, None

# 4. 분석 결과 출력
if st.session_state.target_ticker:
    df, s_name = load_and_analyze_v101(st.session_state.target_ticker)
    
    if df is not None:
        # 지표 계산
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss))); last_rsi = rsi.iloc[-1]
        
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean(); signal = macd.ewm(span=9).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [A] 결론 신호등
        st.write("---")
        if last_rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {s_name}: 강력 매수 (바닥권) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {s_name}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침 메모 (선생님 핵심 로직)
        memo = f"🚩 **{s_name} ({st.session_state.target_ticker}) 투자 대응 지침**<br>"
        if ma20_up: memo += "✅ **이평선**: 주가가 빨간 중간선(20일선) 위로 올라와 안정적입니다.<br>"
        else: memo += "❌ **이평선**: 아직 중간선 아래에 있으니 반등을 확인하세요.<br>"
        if macd_up: memo += "✅ **기세**: 파란선(MACD)이 주황선 위에 있어 보유가 유리합니다.<br>"
        else: memo += "⚠️ **주의**: 기세가 아직 하강 중입니다. 바닥 신호라도 조금 더 기다리세요.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가**: 전고점 돌파 임박! 돌파 시 추가 매수 자리입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 상세 수표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in st.session_state.target_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in st.session_state.target_ticker else f"{y_high:,.2f}")

        # [D] 그래프
        
        st.write("---")
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 빨간 중간선
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else:
        st.error(f"'{st.session_state.target_ticker}' 데이터를 가져올 수 없습니다. 번호를 다시 확인해 보세요.")

with st.sidebar:
    if st.button("🗑️ 오늘 검색 기록 리셋"):
        st.session_state.clear()
        st.rerun()
