import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 화면 스타일 설정
st.set_page_config(page_title="이수 투자비책", layout="wide")

st.markdown("""
    <style>
    .stButton > button {
        width: 100% !important; background-color: #FF8C00 !important; color: white !important;
        font-size: 26px !important; font-weight: bold !important; height: 60px !important;
        border-radius: 15px !important; border: none !important; margin-top: 5px !important;
    }
    .big-font { font-size:32px !important; font-weight: bold; }
    .realtime-font { font-size:20px !important; color: #00AD21; font-weight: bold; } /* 네이버 초록색 강조 */
    .index-font { font-size:28px !important; font-weight: bold; color: #007BFF; }
    .buy-signal { font-size:55px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 25px; border-radius: 15px; border: 3px solid #FF4B4B; }
    .sell-signal { font-size:55px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 25px; border-radius: 15px; border: 3px solid #2E7D32; }
    .wait-signal { font-size:55px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 25px; border-radius: 15px; border: 3px solid #FFA000; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수 할아버지의 실시간 투자 비책")

# [보강] 네이버에서 1초 만에 현재가 가져오는 함수
def get_naver_realtime_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.select_one(".today .no_today .blind")
        if price_tag:
            return float(price_tag.text.replace(',', ''))
        return None
    except:
        return None

@st.cache_data(ttl=20) # 20초마다 새 데이터 허용
def get_analysis_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if df.empty: return None
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except:
        return None

# 종목 사전
stock_dict = {
    "에스피지": "058610.KQ", "삼성전자": "005930.KS", "유한양행": "000100.KS", 
    "삼성E&A": "028050.KS", "실리콘투": "247020.KQ", "아이온큐": "IONQ",
    "엔비디아": "NVDA", "넷플릭스": "NFLX"
}

user_input = st.text_input("종목을 입력하세요", value="유한양행").strip()
analyze_btn = st.button("🔍 실시간 분석 시작!")

ticker = stock_dict.get(user_input, user_input).upper()
if user_input.isdigit() and len(user_input) == 6:
    ticker = user_input + (".KQ" if user_input == "058610" else ".KS")

if ticker:
    df = get_analysis_data(ticker)
    
    if df is not None:
        # 한국 주식일 경우 네이버 실시간 가격 합병
        realtime_p = None
        if ".KS" in ticker or ".KQ" in ticker:
            pure_code = ticker.split('.')[0]
            realtime_p = get_naver_realtime_price(pure_code)
        
        # 지표 계산용 종가 데이터 준비
        close_series = df['close'].copy()
        if realtime_p:
            # 마지막 데이터를 실시간 가격으로 교체하여 지표를 더 정확하게 계산
            close_series.iloc[-1] = realtime_p
            curr_p = realtime_p
            status_text = "🟢 네이버 실시간"
        else:
            curr_p = close_series.iloc[-1]
            status_text = "📅 지연 데이터(20분)"

        # 3대 지표 계산
        delta = close_series.diff()
        rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
        willr = -100 * (df['high'].rolling(14).max() - close_series) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
        sma20 = close_series.rolling(20).mean()
        std20 = close_series.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        is_korea = ".KS" in ticker or ".KQ" in ticker
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='realtime-font'>{status_text} 기준: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
        
        c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
        st.write("---")
        col1, col2 = st.columns(2)
        col1.markdown(f"**RSI (강도)**: <span class='index-font'>{c_rsi:.1f}</span>", unsafe_allow_html=True)
        col2.markdown(f"**윌리엄 지수**: <span class='index-font'>{c_will:.1f}</span>", unsafe_allow_html=True)

        st.write("---")
        c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
        if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
            st.markdown("<div class='buy-signal'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
            st.markdown("<div class='sell-signal'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-signal'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)

        st.write("---")
        chart_data = pd.DataFrame({'현재가': close_series, '상단': upper_bb, '하단': lower_bb}).tail(100)
        st.line_chart(chart_data)
    else:
        st.error("데이터를 가져오지 못했습니다. 종목 코드를 확인하세요.")
