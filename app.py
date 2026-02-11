import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 화면 스타일 및 버튼 디자인 설정
st.set_page_config(page_title="이수 투자비책", layout="wide")

st.markdown("""
    <style>
    /* 분석 버튼 스타일 */
    div.stButton > button:first-child {
        background-color: #FF8C00;
        color: white;
        font-size: 24px !important;
        font-weight: bold;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        border: 2px solid #FF8C00;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #FF7000;
        color: white;
        border: 2px solid #FF7000;
    }
    .big-font { font-size:32px !important; font-weight: bold; }
    .index-font { font-size:28px !important; font-weight: bold; color: #007BFF; }
    .time-font { font-size:18px !important; color: #FF4B4B; font-weight: bold; }
    .buy-signal { font-size:55px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 25px; border-radius: 15px; border: 3px solid #FF4B4B; }
    .sell-signal { font-size:55px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 25px; border-radius: 15px; border: 3px solid #2E7D32; }
    .wait-signal { font-size:55px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 25px; border-radius: 15px; border: 3px solid #FFA000; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수 할아버지의 투자 비책")

# 2. 데이터 수집 함수 (버튼 누를 때마다 최신화되도록 캐시 시간 단축)
@st.cache_data(ttl=30) # 30초 동안만 기억 (버튼 누르면 금방 새 데이터 가져옴)
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

# 종목 사전
stock_dict = {
    "에스피지": "058610.KQ", "삼성전자": "005930.KS", "유한양행": "000100.KS", 
    "삼성E&A": "028050.KS", "실리콘투": "247020.KQ", "아이온큐": "IONQ",
    "엔비디아": "NVDA", "넷플릭스": "NFLX"
}

# 3. 입력창과 분석 버튼
col_input, col_btn = st.columns([3, 1])
with col_input:
    user_input = st.text_input("종목 입력", value="유한양행").strip()
with col_btn:
    analyze_btn = st.button("🔍 지금 분석!")

ticker = stock_dict.get(user_input, user_input).upper()
if user_input.isdigit() and len(user_input) == 6:
    ticker = user_input + (".KQ" if user_input == "058610" else ".KS")

# 분석 실행 (버튼을 누르거나 종목을 입력했을 때)
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

        # 결과 출력
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
    else:
        st.error("데이터를 찾을 수 없습니다. 종목명이나 코드를 확인해 주세요.")
       
    
            
      
