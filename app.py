import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 화면 스타일 설정
st.set_page_config(page_title="주식 분석 프로그램", layout="wide")
st.markdown("""
    <style>
    .big-font { font-size:32px !important; font-weight: bold; }
    .index-font { font-size:28px !important; font-weight: bold; color: #007BFF; }
    .time-font { font-size:18px !important; color: #FF4B4B; font-weight: bold; }
    .buy-signal { font-size:55px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 25px; border-radius: 15px; border: 3px solid #FF4B4B; }
    .sell-signal { font-size:55px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 25px; border-radius: 15px; border: 3px solid #2E7D32; }
    .wait-signal { font-size:55px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 25px; border-radius: 15px; border: 3px solid #FFA000; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 주식 분석 프로그램 (데이터 및 종목 수정 버전)")

# 2. 실시간 데이터 보정 함수
@st.cache_data(ttl=60)
def get_stock_data(ticker):
    try:
        # 기본 일봉 데이터 다운로드
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if df is None or df.empty: return None
        
        # [핵심] 일봉 데이터가 지연될 경우 최신 거래 데이터를 강제로 가져와 합침
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

# 3. 종목 사전 (에스피지 수정)
stock_dict = {
    "에스피지": "058610.KQ",
    "삼성전자": "005930.KS",
    "유한양행": "000100.KS",
    "삼성E&A": "028050.KS"
}

user_input = st.text_input("종목 검색 (이름 또는 6자리 코드)", value="에스피지").strip()

# 숫자 6자리 입력 시 코스닥(.KQ) 우선 적용 로직
if user_input.isdigit() and len(user_input) == 6:
    ticker = user_input + ".KQ"
else:
    ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    with st.spinner(f"'{ticker}' 데이터를 최신으로 업데이트 중..."):
        df = get_stock_data(ticker)
        
        # 데이터가 없으면 코스피(.KS)로 재시도
        if df is None and ".KQ" in ticker:
            ticker = ticker.replace(".KQ", ".KS")
            df = get_stock_data(ticker)

        if df is not None and 'close' in df.columns:
            close = df['close']
            last_date = df.index[-1].strftime('%Y-%m-%d')
            
            # 지표 계산 (RSI, 윌리엄 R, 볼린저 밴드)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            high_14 = df['high'].rolling(14).max()
            low_14 = df['low'].rolling(14).min()
            willr = -100 * (high_14 - close) / (high_14 - low_14)
            
            sma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

            # 결과 출력
            is_korea = ".KS" in ticker or ".KQ" in ticker
            unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
            curr_p = close.iloc[-1]
            
            st.write(f"### 🔍 {user_input} ({ticker})")
            st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='time-font'>📅 데이터 날짜: {last_date}</p>", unsafe_allow_html=True)
            
            c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
            st.write("---")
            col1, col2 = st.columns(2)
            col1.markdown(f"**RSI (강도)**: <span class='index-font'>{c_rsi:.1f}</span>", unsafe_allow_html=True)
            col2.markdown(f"**윌리엄 지수**: <span class='index-font'>{c_will:.1f}</span>", unsafe_allow_html=True)

            # 신호 판독
            st.write("---")
            c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
            if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
                st.markdown("<div class='buy-signal'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
            elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
                st.markdown("<div class='sell-signal'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='wait-signal'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)

            st.write("---")
            st.subheader("📈 최근 주가 흐름 (볼린저 밴드)")
            chart_data = pd.DataFrame({'현재가': close, '상단': upper_bb, '하단': lower_bb}).tail(100)
            st.line_chart(chart_data)
        else:
            st.error("데이터를 불러올 수 없습니다. 종목 코드를 다시 확인하세요.")
