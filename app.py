import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 종목 기억장치
st.set_page_config(page_title="이수 Stock Analyzer v94", layout="wide")

# 오늘 본 종목들을 기억하고, 현재 보고 있는 종목이 무엇인지 추적합니다.
if 'favorites' not in st.session_state:
    st.session_state.favorites = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "아이온큐": "IONQ", "엔비디아": "NVDA"
    }
if 'current_sel' not in st.session_state:
    st.session_state.current_sel = "삼성전자"

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 15px; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 15px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 21px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 지능형 종목 정보 검색 함수
def get_ticker_info(input_code):
    code = input_code.upper().strip()
    if code.isdigit() and len(code) == 6:
        for suffix in [".KS", ".KQ"]:
            t = yf.Ticker(code + suffix)
            if not t.history(period="1d").empty:
                name = t.info.get('shortName', code)
                return name, code + suffix
    else:
        t = yf.Ticker(code)
        if not t.history(period="1d").empty:
            name = t.info.get('shortName', code)
            return name, code
    return None, None

# 3. 상단: 자유 검색창 (즉시 전환 로직 포함)
st.title("👨‍💻 이수할아버지의 주식분석기 v94")
st.subheader("🔍 번호나 티커 입력 후 엔터! (화면이 바로 바뀝니다)")

search_input = st.text_input("종목 입력 (예: 000660 또는 TSLA)", key="search_bar")

if search_input:
    name, full_code = get_ticker_info(search_input)
    if full_code:
        # 리스트에 추가하고, 현재 선택 종목을 이것으로 바꿉니다.
        st.session_state.favorites[name] = full_code
        st.session_state.current_sel = name
        # 입력창을 비우기 위해 리런(Rerun)
        st.rerun()
    else:
        st.error("❌ 종목을 찾을 수 없습니다.")

st.write("---")

# 4. 분석 대상 선택 (검색하면 여기가 자동으로 바뀝니다)
list_options = list(st.session_state.favorites.keys())
# 현재 세션에 저장된 종목이 리스트에 있는지 확인 후 위치 선정
try:
    default_idx = list_options.index(st.session_state.current_sel)
except:
    default_idx = 0

sel_name = st.selectbox("📋 오늘 분석 중인 종목 리스트", options=list_options, index=default_idx)
st.session_state.current_sel = sel_name # 선택이 바뀌면 세션도 업데이트
target_code = st.session_state.favorites[sel_name]

# 5. 데이터 엔진
@st.cache_data(ttl=60)
def get_stock_data_v94(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df.sort_values('Date').ffill().dropna()
    except: return None

if target_code:
    df = get_stock_data_v94(target_code)
    if df is not None and not df.empty:
        # 지표 계산 ($RSI$, $W\%R$, $MACD$)
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss))); last_rsi = rsi.iloc[-1]
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100; last_wr = w_r.iloc[-1]
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean(); signal = macd.ewm(span=9, adjust=False).mean()
        
        curr_p = close.iloc[-1]; y_high = close.max()
        macd_up = macd.iloc[-1] > signal.iloc[-1]; ma20_up = curr_p > ma20.iloc[-1]

        # [1] 결론 신호등
        if last_rsi <= 35 or last_wr <= -80:
            st.markdown("<div class='buy-box'>🚨 강력 매수 (바닥권 진입) 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 관망 및 추세 대기 🟡</div>", unsafe_allow_html=True)

        # [2] 투자 지침 메모
        memo = f"🚩 **{sel_name} ({target_code}) 분석 결과**<br>"
        if last_rsi <= 35 and not macd_up:
            memo += "💡 **알림**: 가격은 싸지만 기세는 하락 중입니다. 분할 매수하세요.<br>"
        if ma20_up: memo += "✅ **20일선**: 주가가 중간선(빨간선) 위로 올라왔습니다. 긍정적입니다.<br>"
        else: memo += "❌ **20일선**: 아직 중간선 아래에 있으니 반등을 확인하세요.<br>"
        if macd_up: memo += "✅ **기세**: MACD 파란선이 위에 있어 보유가 유리합니다.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가**: 전고점 돌파 임박! 불타기 가능 자리입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # [3] 수치 보고서
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if ".K" in target_code else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승 중" if macd_up else "하락 중")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in target_code else f"${y_high:,.2f}")

        # [4] 주가 차트 (볼린저
