import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v85", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "아이온큐": "IONQ", "삼성전자": "005930", "현대차": "005380", 
        "엔비디아": "NVDA", "유한양행": "000100", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .sell-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #0059FF; background-color: #EEF2FF; color: #0059FF; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 10px; border: 5px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 20px; border-radius: 10px; background-color: #FFF9C4; border-left: 10px solid #FBC02D; color: #424242; font-size: 19px; font-weight: bold; line-height: 1.6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. [국장용] 네이버 금융 시세 직거래 엔진
@st.cache_data(ttl=300)
def get_naver_data_v85(code):
    try:
        url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count=250&requestType=0"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'xml')
        items = soup.find_all('item')
        data = [item['data'].split('|') for item in items]
        df = pd.DataFrame(data, columns=['Date', 'open', 'high', 'low', 'close', 'volume'])
        df['Date'] = pd.to_datetime(df['Date'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        return df.set_index('Date').sort_index()
    except: return None

# 3. [미장용] 야후 보안 우회 및 이름표 강제 수리 엔진
@st.cache_data(ttl=60)
def get_us_data_v85(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        if 'close' not in df.columns: df['close'] = df.iloc[:, 1]
        return df.set_index('Date').sort_index()
    except: return None

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v85")
st.write("---")

sel_name = st.selectbox("📋 종목을 다시 선택해 보세요", options=list(st.session_state.name_map.keys()), index=0)
code = st.session_state.name_map[sel_name]

if code:
    with st.spinner(f'{sel_name} 데이터를 불러오는 중...'):
        if code.isdigit(): df = get_naver_data_v85(code)
        else: df = get_us_data_v85(code)

    if df is not None and not df.empty:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산: RSI, Williams %R, MACD, MA20
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        curr_p = close.iloc[-1]; last_rsi = rsi.iloc[-1]; last_wr = w_r.iloc[-1]
        y_high = close.max()

        # 1. 상단 신호등
        if last_rsi <= 35 or last_wr <= -80:
            st.markdown("<div class='buy-box'>🚨 가격 바닥권 (매수 검토) 🚨</div>", unsafe_allow_html=True)
        elif last_rsi >= 75:
            st.markdown("<div class='sell-box'>⚠️ 이익 실현 (과열 구간) ⚠️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-box'>🟡 추세 관망 및 보유 🟡</div>", unsafe_allow_html=True)

        # 2. 전문가 메모 (신호등 바로 아래)
        macd_up = macd.iloc[-1] > signal.iloc[-1]
        ma20_up = curr_p > ma20.iloc[-1]
        memo = f"🚩 **{sel_name} 투자 지침**<br>"
        if ma20_up: memo += "✅ **매수 고려**: 주가가 <b>빨간색 중간선(20일선)</b> 위로 올라왔습니다. 매수를 긍정적으로 검토하세요.<br>"
        else: memo += "❌ **대기**: 아직 주가가 중간선 아래에 있으니 반등을 좀 더 확인하세요.<br>"
        if macd_up: memo += "✅ **보유**: <b>파란선(MACD)이 주황선 위</b>에 있어 상승 기세가 살아있습니다.<br>"
        else: memo += "⚠️ **주의**: 파란선이 아래로 꺾였으니 기세가 약해진 상태입니다.<br>"
        if curr_p >= y_high * 0.98: memo += "🔥 **신고가 돌파**: 전고점 돌파 임박! 강한 상승이 예상되는 <b>불타기 매수</b> 자리입니다."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # 3. 상세 지표
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}원" if code.isdigit() else f"${curr_p:,.2f}")
        m2.metric("RSI (바닥)", f"{last_rsi:.1f}")
        m3.metric("MACD 기세", "상승" if macd_up else "하락")
        m4.metric("1년 최고가", f"{y_high:,.0f}원" if code.isdigit() else f"${y_high:,.2f}")

        # 4. 그래프
        st.write("---")
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
                chart_df = df.tail(100).reset_index()
        chart_df['MA20'] = ma20.tail(100).values; chart_df['Upper'] = upper.tail(100).values; chart_df['Lower'] = lower.tail(100).values
        base = alt.Chart(chart_df).encode(x='Date:T')
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=400), use_container_width=True)

        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있을 때 보유!)")
                m_df = pd.DataFrame({'Date': chart_df['Date'], 'MACD': macd.tail(100).values, 'Signal': signal.tail(100).values})
        m_base = alt.Chart(m_df).encode(x='Date:T')
        st.altair_chart((m_base.mark_line(color='#2563EB', strokeWidth=2).encode(y='MACD:Q') + 
                         m_base.mark_line(color='#F59E0B', strokeWidth=2).encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else:
        st.error("⚠️ 데이터를 가져오지 못했습니다. 인터넷 창을 새로고침(F5) 해주세요.")

if st.sidebar.button("🗑️ 전체 리셋"):
    st.session_state.clear()
    st.rerun()
