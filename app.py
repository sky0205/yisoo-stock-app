import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 초기 데이터 세팅
st.set_page_config(page_title="이수 Stock Analyzer v111", layout="wide")

if 'favorites' not in st.session_state:
    st.session_state.favorites = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "현대차": "005380.KS", "엔비디아": "NVDA", "쿠팡": "CPNG"}
if 'current_sel' not in st.session_state:
    st.session_state.current_sel = "삼성전자"

# 선생님 취향의 시원시원한 대형 스타일
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 검색 및 리스트 관리 (에러 방지용 로직)
st.title("👨‍💻 이수할아버지의 주식분석기 v111")
st.write("---")

st.subheader("🔍 종목 번호(6자리)나 티커를 입력하고 엔터를 치세요")
u_input = st.text_input("숫자만 입력해도 됩니다 (예: 000660)", key="main_search")

if u_input:
    code = u_input.upper().strip()
    found_ticker = None
    with st.spinner('서버에서 데이터를 끈질기게 찾는 중...'):
        if code.isdigit() and len(code) == 6:
            # 코스피(.KS) 시도 후 안되면 코스닥(.KQ) 시도
            for suffix in [".KS", ".KQ"]:
                try:
                    df_test = yf.download(code + suffix, period="1d", progress=False)
                    if not df_test.empty:
                        found_ticker = code + suffix
                        break
                except: continue
        else:
            # 미국 주식 등 티커 시도
            try:
                df_test = yf.download(code, period="1d", progress=False)
                if not df_test.empty: found_ticker = code
            except: pass
    
    if found_ticker:
        st.session_state.favorites[found_ticker] = found_ticker
        st.session_state.current_sel = found_ticker
        st.rerun()
    else:
        st.error("⚠️ 데이터를 가져올 수 없습니다. 번역 기능을 끄셨는지 확인하시고 번호를 다시 확인해 주세요.")

# 3. 분석 종목 선택
st.write("---")
opts = list(st.session_state.favorites.keys())
sel_name = st.selectbox("📋 오늘 분석 중인 종목 리스트", options=opts, 
                          index=opts.index(st.session_state.current_sel) if st.session_state.current_sel in opts else 0)
st.session_state.current_sel = sel_name
target_ticker = st.session_state.favorites[sel_name]

# 4. 데이터 엔진 (최신 야후 에러 완벽 수정판)
@st.cache_data(ttl=60)
def fetch_safe_v111(ticker):
    try:
        # 최신 yfinance의 다중 인덱스 문제를 해결하기 위해 multi_level_index=False 강제 설정
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False, threads=False)
        if df is None or df.empty: return None
        
        # 열 이름을 무조건 소문자/단순화하여 고정
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except:
        return None

if target_ticker:
    df = fetch_safe_v111(target_ticker)
    if df is not None:
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        
        # 1) RSI 계산 ($$RSI = 100 - [100 / (1 + RS)]$$)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 2) MACD 계산 ($$MACD = EMA_{12} - EMA_{26}$$)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # 3) 볼린저 밴드 (20일 이평선 ± 2 표준편차)
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        curr_p = close.iloc[-1]; last_rsi = rsi.iloc[-1]; macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [A] 결론 신호등
        st.write("---")
        if last_rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {sel_name}: 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {sel_name}: 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [B] 투자 지침 메모 (신호등 바로 아래)
        memo = f"🚩 **{sel_name} 투자 대응 전략**<br>"
        if ma20_up: memo += "✅ **이평선**: 주가가 빨간 중간선(20일선) 위로 올라왔습니다. 매수 시점입니다.<br>"
        else: memo += "❌ **이평선**: 아직 중간선 아래에 있습니다. 반등을 더 기다리세요.<br>"
        if macd_up: memo += "✅ **기세**: 파란선(MACD)이 주황선 위에 있어 보유가 유리합니다.<br>"
        else: memo += "⚠️ **주의**: 기세가 아직 하락 중입니다. 바닥 신호라도 조금 더 기다리세요."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [C] 상세 수치
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".K" in target_ticker else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{close.max():,.0f}" if ".K" in target_ticker else f"${close.max():,.2f}")

        # [D] 그래프
        st.write("---")
        
        chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q') # 20일선
        st.altair_chart((band + line + ma_line).properties(height=500), use_container_width=True)

        m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB').encode(y='MACD:Q') + m_base.mark_line(color='#F59E0B').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else:
        st.error(f"⚠️ '{sel_name}' 데이터를 가져올 수 없습니다. 브라우저 상단의 '번역 기능'을 끄고 다시 시도해 주세요.")

with st.sidebar:
    if st.button("🗑️ 전체 기록 리셋"):
        st.session_state.clear()
        st.rerun()
