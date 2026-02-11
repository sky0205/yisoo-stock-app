import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")

st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .buy-signal { font-size:50px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 20px; border-radius: 10px; }
    .sell-signal { font-size:50px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 20px; border-radius: 10px; }
    .wait-signal { font-size:50px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 2026년형 무적 주식 분석기 (최종)")

# [보강] 데이터 이름표를 강제로 깨끗하게 씻어내는 함수
@st.cache_data(ttl=600)
def get_clean_data(ticker):
    try:
        # 데이터를 가져올 때 무조건 최신 규격을 따르도록 설정
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        
        if df.empty: return None
        
        # 이름표(컬럼)에 불순물이 섞여 있으면 제거
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    except:
        return None

# 2. 똑똑한 사전
stock_dict = {
    "삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ", 
    "삼성E&A": "028050.KS", "삼성ENA": "028050.KS", "아이온큐": "IONQ"
}

st.info("💡 이름(삼성전자)이나 숫자(028050)를 입력하고 '엔터'를 치세요.")

# 3. 입력값 처리 (숫자만 치면 .KS를 자동으로 붙여주는 마법)
user_input = st.text_input("종목을 입력하세요", value="028050").strip()

# 만약 숫자 6자리만 입력했다면 자동으로 .KS를 붙여줍니다.
if user_input.isdigit() and len(user_input) == 6:
    ticker = user_input + ".KS"
else:
    ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    with st.spinner(f"'{ticker}' 데이터를 불러오는 중..."):
        df = get_clean_data(ticker)
        
        # 만약 코스피(.KS)로 안 나오면 코스닥(.KQ)으로 한 번 더 시도!
        if df is None and ticker.endswith(".KS"):
            ticker = ticker.replace(".KS", ".KQ")
            df = get_clean_data(ticker)

        if df is not None and 'close' in df.columns:
            close = df['close']
            
            # 지표 계산
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

            # 출력
            is_korea = ".KS" in ticker or ".KQ" in ticker
            unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
            curr_p = close.iloc[-1]
            
            st.write(f"### 🔍 {user_input} ({ticker}) 분석 결과")
            st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
            
            c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
            c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
            
            if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
                st.markdown("<div class='buy-signal'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
            elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
                st.markdown("<div class='sell-signal'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='wait-signal'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)

            st.write("---")
            st.subheader("📈 주가 흐름 (최근 100일)")
            chart_data = pd.DataFrame({'현재가': close, '상단': upper_bb, '하단': lower_bb}).tail(100)
            st.line_chart(chart_data)
        else:
            st.error(f"❌ '{ticker}' 데이터를 찾을 수 없습니다. 코드를 다시 확인해 주세요.")

      
