import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")

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

st.title("📈 이수 할아버지의 무적 분석기 (날짜 보정형)")

# [핵심 수정] 오늘의 최신 데이터까지 강제로 가져오는 함수
@st.cache_data(ttl=60) # 1분마다 새로고침
def get_realtime_data(ticker):
    try:
        # 1년치 일봉 데이터
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        
        # [보강] 만약 마지막 날짜가 오늘이 아니라면, 실시간 데이터를 따로 가져와서 합침
        latest = yf.Ticker(ticker).history(period="1d")
        if not latest.empty:
            last_date = latest.index[-1].date()
            if last_date > df.index[-1].date():
                df = pd.concat([df, latest])
                df = df[~df.index.duplicated(keep='last')] # 중복 제거

        if df.empty: return None
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except:
        return None

stock_dict = {"삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ", "에스엘": "058610.KS", "삼성E&A": "028050.KS"}

user_input = st.text_input("종목 검색 (한글 이름이나 코드 6자리)", value="058610").strip()
ticker = stock_dict.get(user_input, user_input).upper()
if user_input.isdigit() and len(user_input) == 6: ticker = user_input + ".KS"

if ticker:
    df = get_realtime_data(ticker)
    if df is not None and 'close' in df.columns:
        close = df['close']
        # 마지막 데이터의 실제 날짜 확인
        last_time = df.index[-1].strftime('%Y-%m-%d %H:%M')
        
        # 지표 계산
        rsi = 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean())))
        willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        is_korea = ".KS" in ticker or ".KQ" in ticker
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        curr_p = close.iloc[-1]
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        # 날짜를 더 눈에 띄게 빨간색으로 표시
        st.markdown(f"<p class='time-font'>📅 최종 업데이트 시점: {last_time}</p>", unsafe_allow_html=True)
        
        c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
        st.write("---")
        col_idx1, col_idx2 = st.columns(2)
        with col_idx1:
            st.markdown(f"**RSI (강도)**")
            st.markdown(f"<p class='index-font'>{c_rsi:.1f}</p>", unsafe_allow_html=True)
        with col_idx2:
            st.markdown(f"**윌리엄 지수**")
            st.markdown(f"<p class='index-font'>{c_will:.1f}</p>", unsafe_allow_html=True)

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
