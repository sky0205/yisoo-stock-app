import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 화면 스타일 설정
st.set_page_config(page_title="이수 투자비책", layout="wide")

st.markdown("""
    <style>
    /* 분석 버튼을 화면 꽉 차게 큼직하게 만듭니다 */
    .stButton > button {
        width: 100% !important;
        background-color: #FF8C00 !important;
        color: white !important;
        font-size: 26px !important;
        font-weight: bold !important;
        height: 60px !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 5px !important;
        margin-bottom: 20px !important;
    }
    .big-font { font-size:32px !important; font-weight: bold; }
    .index-font { font-size:28px !important; font-weight: bold; color: #007BFF; }
    .time-font { font-size:16px !important; color: #FF4B4B; font-weight: bold; }
    .buy-signal { font-size:55px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 25px; border-radius: 15px; border: 3px solid #FF4B4B; }
    .sell-signal { font-size:55px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 25px; border-radius: 15px; border: 3px solid #2E7D32; }
    .wait-signal { font-size:55px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 25px; border-radius: 15px; border: 3px solid #FFA000; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수 할아버지의 투자 비책")

@st.cache_data(ttl=30)
def get_fresh_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        ticker_obj = yf.Ticker(ticker)
        today_data = ticker_obj.history(period="1d")
        if not today_data.empty:
            if today_data.index[-1].date() > df.index[-1].date():
                df = pd.concat([df, today_data])
                df = df[~df.index.duplicated(keep='last')]
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except:
        return None

stock_dict = {
    "에스피지": "058610.KQ", "삼성전자": "005930.KS", "유한양행": "000100.KS", 
    "삼성E&A": "028050.KS", "실리콘투": "247020.KQ", "아이온큐": "IONQ",
    "엔비디아": "NVDA", "넷플릭스": "NFLX"
}

# 2. 입력창과 버튼을 세로로 배치 (모바일에서 가장 안전한 방법)
user_input = st.text_input("종목을 입력하고 아래 버튼을 누르세요", value="에스피지").strip()
analyze_btn = st.button("🔍 지금 분석하기")

ticker = stock_dict.get(user_input, user_input).upper()
if user_input.isdigit() and len(user_input) == 6:
    # 에스피지는 코스닥(.KQ), 나머지는 코스피(.KS)로 일단 설정
    ticker = user_input + (".KQ" if user_input == "058610" else ".KS")

# 버튼을 눌렀을 때만 분석 결과가 나오게 하거나, 처음 로딩 때 보여줍니다.
if ticker:
    df = get_fresh_data(ticker)
    
    if df is not None and 'close' in df.columns:
        close = df['close']
        last_date = df.index[-1].strftime('%Y-%m-%d %H:%M')
        
        # 지표 계산
        delta = close.diff()
        rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
        willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        curr_p = close.iloc[-1]
        is_korea = ".KS" in ticker or ".KQ" in ticker
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='time-font'>📅 최종 업데이트: {last_date}</p>", unsafe_allow_html=True)
        
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
        chart_data = pd.DataFrame({'현재가': close, '상단': upper_bb, '하단': lower_bb}).tail(100)
        st.line_chart(chart_data)
