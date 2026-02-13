import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 및 간판 고정
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

# 미장 한글 사전
US_KR_MAP = {
    "AAPL": "애플", "TSLA": "테슬라", "NVDA": "엔비디아", "IONQ": "아이온큐",
    "MSFT": "마이크로소프트", "GOOGL": "구글", "AMZN": "아마존", "META": "메타",
    "NFLX": "넷플릭스", "TSM": "TSMC", "PLTR": "팔란티어"
}

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:45px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            name = soup.select_one(".wrap_company h2 a").text
            return name, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    else:
        if symbol in US_KR_MAP: return US_KR_MAP[symbol], symbol
        try:
            ticker_obj = yf.Ticker(symbol)
            eng_name = ticker_obj.info.get('shortName', symbol)
            clean_name = eng_name.split(' ')[0].split(',')[0]
            return clean_name, symbol
        except: return symbol, symbol

@st.cache_data(ttl=60)
def get_analysis_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

# 앱 시작
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col_input, _ = st.columns([4, 1])
with col_input:
    history_list = list(st.session_state.name_map.keys())
    selected_name = st.selectbox("📋 나의 종목 수첩", options=history_list, index=None, placeholder="보관된 종목을 선택하세요")
    new_symbol = st.text_input("➕ 새 종목 추가", value="", placeholder="번호 6자리 또는 영어 티커")

target_name = ""; target_ticker = ""
if new_symbol:
    name, ticker = fetch_stock_name(new_symbol)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    target_name = name; target_ticker = ticker
elif selected_name:
    target_name = selected_name; target_ticker = st.session_state.name_map[selected_name]

if target_ticker:
    df = get_analysis_data(target_ticker)
    if df is not None:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산
        rsi = 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean())))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()) * -100
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

        # [수정] 신고가 판단 로직 강화 (최근 5일간의 최고가를 1년 최고가와 비교)
        year_high = close.iloc[:-1].max() # 오늘을 제외한 1년 최고가
        curr_price = close.iloc[-1]
        # 현재가가 1년 최고가의 97% 이상이거나, 이미 뚫었을 때 신고가로 인정
        is_new_high = curr_price >= (year_high * 0.97)

        st.markdown(f"<p class='big-font'>{target_name} 지표 분석</p>", unsafe_allow_html=True)
        
        # [신고가 안내창] 어떤 종목이든 조건만 맞으면 즉시 노출
        if is_new_high:
            st.markdown(f"""
            <div class='info-box'>
                <h3 style='margin-top:0; color:#1565C0;'>🚀 {target_name} 신고가 영역 진입!</h3>
                현재 주가가 전고점 근처이거나 이미 돌파한 <strong>'달리는 말'</strong> 구간입니다. <br>
                RSI 수치가 높아도 기세가 워낙 강해 추가 상승이 빈번한 자리입니다. <br>
                <strong>매도 전략:</strong> MACD 파란선이 주황선 밑으로 꺾일 때까지 수익을 즐기세요. <br>
                <strong>신규 매수:</strong> 지금 따라가기보다는 볼린저 밴드 빨간선(중심선) 터치 시 진입이 안전합니다.
            </div>
            """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{curr_price:,.2f}")
        c2.metric("RSI", f"{rsi.iloc[-1]:.1f}")
        c3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        c4.metric("전고점(1년)", f"{year_high:,.2f}")

        # 신호등 로직
        st.write("---")
        last_rsi = rsi.iloc[-1]
        macd_up = macd.iloc[-1] > macd.iloc[-2]
        
        if is_new_high and macd_up:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 (수익 극대화 구간) 📈</div>", unsafe_allow_html=True)
        elif last_rsi <= 35 or w_r.iloc[-1] <= -80:
            if macd_up: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (하강 중)</div>", unsafe_allow_html=True)
        elif last_rsi >= 75:
            st.markdown("<div style='background-color:#E1F5FE; color:#0288D1; border-color:#0288D1;' class='status-box'>💰 과열 주의 (분할 익절 고려) 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 관찰 구간 🟡</div>", unsafe_allow_html=True)

        # 차트
        st.write("### 📊 볼린저 밴드 (중심선 터치 시 매수 고려)")
        bb_df = pd.DataFrame({'Price': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(80).reset_index()
        bb_df.columns = ['Date', 'Price', 'Upper', 'Lower', 'MA20']
        base = alt.Chart(bb_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        line = base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Price:Q', scale=alt.Scale(zero=False)))
        b_up = base.mark_line(color='#B0BEC5', strokeDash=[5,5]).encode(y='Upper:Q')
        b_low = base.mark_line(color='#B0BEC5', strokeDash=[5,5]).encode(y='Lower:Q')
        b_ma = base.mark_line(color='#EF5350', strokeWidth=1.5).encode(y='MA20:Q')
        st.altair_chart(alt.layer(b_up, b_low, b_ma, line).properties(height=350), use_container_width=True)

        st.write("### 📉 MACD 추세선 (파란선이 주황선 위에 있으면 보유)")
        macd_df = pd.DataFrame({'MACD': macd, 'Signal': sig}).tail(80).reset_index()
        macd_df.columns = ['Date', 'MACD', 'Signal']
        base_m = alt.Chart(macd_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        l_macd = base_m.mark_line(color='#0059FF', strokeWidth=2).encode(y=alt.Y('MACD:Q'))
        l_sig = base_m.mark_line(color='#FF8000', strokeWidth=2).encode(y='Signal:Q')
        st.altair_chart(alt.layer(l_macd, l_sig).properties(height=250), use_container_width=True)
