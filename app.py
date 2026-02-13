import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 화면 설정
st.set_page_config(page_title="이수 투자비책 v11", layout="wide")

# [메모리 설정]
if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX", "에스피지": "058610.KQ"
    }
if 'history' not in st.session_state:
    st.session_state.history = list(st.session_state.name_map.keys())

st.markdown("""
    <style>
    .stMetric { background-color: #F0F2F6; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 45px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

# 종목 이름 찾아오기 함수
def get_stock_name(ticker):
    if ticker.isdigit() and len(ticker) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={ticker}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text
        except: return ticker
    else:
        try:
            stock = yf.Ticker(ticker)
            return stock.info.get('shortName', ticker)
        except: return ticker

@st.cache_data(ttl=60)
def get_analysis_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

st.title("📈 이수 할아버지의 '볼린저 밴드 완벽' 분석기")

# [검색창]
st.subheader("🔍 종목을 선택하거나 새로 입력하세요")
user_choice = st.selectbox("나의 종목 수첩:", options=st.session_state.history, index=None, placeholder="종목을 고르세요")
new_input = st.text_input("새로운 종목 입력 (번호 6자리 또는 영어 티커):", value="")

final_ticker = ""; final_name = ""

if user_choice:
    final_name = user_choice; final_ticker = st.session_state.name_map[user_choice]
elif new_input:
    temp_ticker = new_input.upper()
    final_ticker = temp_ticker + ".KS" if temp_ticker.isdigit() and len(temp_ticker) == 6 else temp_ticker
    final_name = get_stock_name(temp_ticker)
    if final_name not in st.session_state.name_map:
        st.session_state.name_map[final_name] = final_ticker
        if final_name not in st.session_state.history: st.session_state.history.insert(0, final_name)

# 분석 실행
if final_ticker:
    df = get_analysis_data(final_ticker)
    if df is None and ".KS" in final_ticker:
        final_ticker = final_ticker.replace(".KS", ".KQ")
        df = get_analysis_data(final_ticker)

    if df is not None:
        close = df['close']; high = df['high']; low = df['low']
        
        # [지표 계산]
        # 1. RSI
        diff = close.diff(); rsi = 100 - (100 / (1 + (diff.where(diff > 0, 0).rolling(14).mean() / -diff.where(diff < 0, 0).rolling(14).mean())))
        # 2. 윌리엄 %R
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()) * -100
        # 3. MACD
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        # 4. 볼린저 밴드 전체 (상단, 중단, 하단)
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2)
        lower = ma20 - (std20 * 2)

        st.markdown(f"<p class='big-font'>{final_name}: {close.iloc[-1]:,.2f}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("RSI (상대강도)", f"{rsi.iloc[-1]:.1f}")
        c2.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        c3.metric("MACD 에너지", "상승세" if macd.iloc[-1] > macd.iloc[-2] else "하락세")

        # 신호등
        st.write("---")
        is_cheap = rsi.iloc[-1] <= 35 or w_r.iloc[-1] <= -80
        if is_cheap:
            if macd.iloc[-1] > macd.iloc[-2]: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 지금입니다! 매수 신호 🚨</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (하락 중)</div>", unsafe_allow_html=True)
        elif rsi.iloc[-1] >= 70: st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;' class='status-box'>💰 수익 실현 권장 💰</div>", unsafe_allow_html=True)
        else: st.markdown("<div style='background-color:#F0F2F6; color:#31333F; border-color:#D1D5DB;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # [수정] 볼린저 밴드 차트 (상단, 중단, 하단 모두 표시)
        st.write("### 📊 볼린저 밴드 주가 흐름 (상단/중단/하단)")
        chart_data = pd.DataFrame({
            '현재가': close,
            '상단선': upper,
            '중심선(20일)': ma20,
            '하단선': lower
        }).tail(80)
        st.line_chart(chart_data)
        
        st.write("### 📉 MACD 에너지 흐름")
        st.line_chart(pd.DataFrame({'MACD': macd, '시그널': sig}).tail(80))
    else:
        st.error(f"'{final_name}' 데이터를 가져오지 못했습니다.")
