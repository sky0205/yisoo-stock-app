import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 및 간판 설정 (Translation OFF)
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

# UI 스타일 설정
st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:45px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            return name, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    return symbol, symbol

@st.cache_data(ttl=60)
def get_final_data(ticker):
    try:
        # Multi-level index 방지 및 데이터 구조 최적화
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).lower() for c in df.columns]
        return df.dropna()
    except: return None

# 앱 시작
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col_in, _ = st.columns([4, 1])
with col_in:
    h_list = list(st.session_state.name_map.keys())
    sel_name = st.selectbox("📋 나의 종목 수첩", options=h_list, index=None, placeholder="보관된 종목을 선택하세요")
    new_sym = st.text_input("➕ 새 종목 추가", placeholder="예: 000660 또는 TSLA")

target_name = ""; target_ticker = ""
if new_sym:
    name, ticker = fetch_stock_name(new_sym)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    target_name, target_ticker = name, ticker
elif sel_name:
    target_name, target_ticker = sel_name, st.session_state.name_map[sel_name]

if target_ticker:
    df = get_final_data(target_ticker)
    if (df is None or df.empty) and ".KS" in target_ticker:
        df = get_final_data(target_ticker.replace(".KS", ".KQ"))

    if df is not None and 'close' in df.columns:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산 ($RSI$, $MACD$, $Williams \%R$)
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean()

        # 신고가 분석 (1년 최고가)
        year_high = close.iloc[:-1].max()
        curr_p = close.iloc[-1]
        is_high = curr_p >= (year_high * 0.97)

        st.markdown(f"<p class='big-font'>{target_name} 지표 분석</p>", unsafe_allow_html=True)
        
        # 🚀 [부활] 신고가 안내 박스
        if is_high:
            st.markdown(f"""
            <div class='info-box'>
                <h3 style='margin-top:0; color:#1565C0;'>🚀 {target_name} 신고가 영역 진입!</h3>
                현재 전고점 돌파가 임박한 <strong>'달리는 말'</strong> 구간입니다. <br>
                추세가 강하므로 MACD 신호가 꺾이기 전까지는 수익을 길게 가져가세요.
            </div>
            """, unsafe_allow_html=True)

        # 📊 [부활] 4개 지표 한눈에 보기
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr_p:,.2f}")
        c2.metric("RSI (과열도)", f"{rsi.iloc[-1]:.1f}")
        c3.metric("윌리엄 %R (바닥)", f"{w_r.iloc[-1]:.1f}")
        c4.metric("1년 최고가", f"{year_high:,.2f}")

        # 🚦 [부활] 화려한 신호등 로직
        st.write("---")
        last_rsi = rsi.iloc[-1]
        macd_up = macd.iloc[-1] > macd.iloc[-2]
        
        if is_high and macd_up:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 (수익 극대화 구간) 📈</div>", unsafe_allow_html=True)
        elif last_rsi <= 35 or w_r.iloc[-1] <= -80:
            if macd_up: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (하락 중)</div>", unsafe_allow_html=True)
        elif last_rsi >= 75:
            st.markdown("<div style='background-color:#E1F5FE; color:#0288D1; border-color:#0288D1;' class='status-box'>💰 과열 주의 (일부 익절 고려) 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 관찰 구간 🟡</div>", unsafe_allow_html=True)

        # 📉 차트 섹션
        st.write("### 📊 주가 및 중심선 (빨간선 터치 시 매수 고려)")
        chart_data = pd.DataFrame({'Price': close, 'MA20': ma20}).tail(80).reset_index()
        base = alt.Chart(chart_data).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart(alt.layer(
            base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Price:Q', scale=alt.Scale(zero=False))),
            base.mark_line(color='#EF5350', strokeWidth=1.5).encode(y='MA20:Q')
        ).properties(height=350), use_container_width=True)

        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있으면 보유)")
        m_df = pd.DataFrame({'MACD': macd, 'Signal': sig}).tail(80).reset_index()
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart(alt.layer(
            m_base.mark_line(color='#0059FF', strokeWidth=2).encode(y='MACD:Q'),
            m_base.mark_line(color='#FF8000', strokeWidth=2).encode(y='Signal:Q')
        ).properties(height=200), use_container_width=True)
    else:
        st.error("데이터 로딩 실패. (번역 기능을 끄고 다시 시도해 주세요)")

if st.sidebar.button("🗑️ 수첩 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
    st.rerun()
