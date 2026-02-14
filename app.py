
import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

st.set_page_config(page_title="이수 매매타이밍 분석기", layout="wide")
st.title("🎯 이수할아버지의 전문 매매타이밍 엔진 v201")

# 1. 입력 및 데이터 수집
ticker = st.text_input("🔍 분석할 종목 번호를 입력하세요 (예: 005930, IONQ)", value="005930").strip()

@st.cache_data(ttl=60)
def fetch_trading_data(t):
    try:
        if t.isdigit(): df = fdr.DataReader(t, '2024')
        else: df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None

if ticker:
    df = fetch_trading_data(ticker)
    if isinstance(df, pd.DataFrame):
        # 2. 기술적 지표 계산 (선생님의 요청 사항)
        # 볼린저 밴드
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['ma20'] + (df['std'] * 2)
        df['bb_lower'] = df['ma20'] - (df['std'] * 2)
        
        # RSI
        diff = df['close'].diff()
        g = diff.where(diff > 0, 0).rolling(14).mean()
        l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        df['rsi'] = 100 - (100 / (1 + (g / l)))
        
        # Williams %R
        h14 = df['high'].rolling(14).max()
        l14 = df['low'].rolling(14).min()
        df['w_r'] = ((h14 - df['close']) / (h14 - l14)) * -100
        
        # MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

        # 3. 매매 신호 요약 표 (선생님 전용 양식)
        st.write("### 📢 실시간 기술적 지표 요약")
        last = df.iloc[-1]
        summary = {
            "지표": ["RSI (상대강도)", "Williams %R", "Bollinger Band", "MACD 추세"],
            "현재값": [f"{last['rsi']:.2f}", f"{last['w_r']:.2f}", f"{last['close']:,.0f}", f"{last['macd']:.2f}"],
            "판정": [
                "과매도(매수기회)" if last['rsi'] < 30 else "과매수(매도주의)" if last['rsi'] > 70 else "보통",
                "바닥권(매수)" if last['w_r'] < -80 else "상단권(매도)" if last['w_r'] > -20 else "중립",
                "하단터치(매수)" if last['close'] < last['bb_lower'] else "상단터치(매도)" if last['close'] > last['bb_upper'] else "밴드 내 위치",
                "상승전환" if last['macd'] > last['signal'] else "하락전환"
            ]
        }
        st.table(pd.DataFrame(summary))

        # 4. 종합 차트 (볼린저 밴드 중심)
        st.write("#### 📊 볼린저 밴드 및 주가 흐름")
        base = alt.Chart(df.tail(100)).encode(x='date:T')
        line = base.mark_line(color='#1E40AF').encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        band = base.mark_area(opacity=0.2, color='gray').encode(y='bb_lower:Q', y2='bb_upper:Q')
        st.altair_chart((band + line).properties(height=400), use_container_width=True)

        # 5. 보조 지표 차트 (MACD/RSI)
        st.write("#### 📉 추세 및 강도 지표 (MACD & RSI)")
        macd_chart = base.mark_line(color='red').encode(y='macd:Q')
        sig_chart = base.mark_line(color='blue').encode(y='signal:Q')
        st.altair_chart((macd_chart + sig_chart).properties(height=200), use_container_width=True)
