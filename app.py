import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 화면 스타일 설정
st.set_page_config(page_title="이수 투자비책 V2", layout="wide")

st.markdown("""
    <style>
    .stButton > button {
        width: 100% !important; background-color: #4B89FF !important; color: white !important;
        font-size: 26px !important; font-weight: bold !important; height: 60px !important;
        border-radius: 15px !important; border: none !important;
    }
    .big-font { font-size:32px !important; font-weight: bold; }
    .realtime-font { font-size:20px !important; color: #00AD21; font-weight: bold; }
    .index-font { font-size:28px !important; font-weight: bold; color: #007BFF; }
    .signal-box { padding: 25px; border-radius: 15px; border: 3px solid; text-align: center; font-size: 50px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수 할아버지의 실시간 분석기 (MACD 강화판)")

# 네이버 실시간 가격 함수
def get_naver_realtime_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.select_one(".today .no_today .blind")
        return float(price_tag.text.replace(',', '')) if price_tag else None
    except: return None

@st.cache_data(ttl=30)
def get_analysis_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if df.empty: return None
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except: return None

# 종목 리스트
stock_dict = {
    "에스피지": "058610.KQ", "삼성전자": "005930.KS", "유한양행": "000100.KS", 
    "삼성E&A": "028050.KS", "실리콘투": "247020.KQ", "아이온큐": "IONQ",
    "엔비디아": "NVDA", "넷플릭스": "NFLX"
}

user_input = st.text_input("종목명을 입력하세요", value="아이온큐").strip()
analyze_btn = st.button("🚀 실시간 추세 분석!")

ticker = stock_dict.get(user_input, user_input).upper()
if user_input.isdigit() and len(user_input) == 6:
    ticker = user_input + (".KQ" if user_input == "058610" else ".KS")

if ticker:
    df = get_analysis_data(ticker)
    if df is not None:
        # 실시간 가격 연동
        realtime_p = get_naver_realtime_price(ticker.split('.')[0]) if ".K" in ticker else None
        close_series = df['close'].copy()
        if realtime_p:
            close_series.iloc[-1] = realtime_p
            curr_p, status_text = realtime_p, "🟢 실시간(네이버)"
        else:
            curr_p, status_text = close_series.iloc[-1], "📅 지연 데이터(20분)"

        # 지표 계산
        # 1. RSI
        delta = close_series.diff()
        rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
        # 2. 볼린저 밴드
        sma20 = close_series.rolling(20).mean()
        std20 = close_series.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)
        # 3. MACD (신규 추가!)
        exp1 = close_series.ewm(span=12, adjust=False).mean()
        exp2 = close_series.ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        # 화면 표시
        is_korea = ".K" in ticker
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='realtime-font'>{status_text}</p>", unsafe_allow_html=True)

        st.write("---")
        col1, col2, col3 = st.columns(3)
        
        # 지표별 요약
        c_rsi = rsi.iloc[-1]
        c_macd, c_sig = macd_line.iloc[-1], signal_line.iloc[-1]
        p_macd, p_sig = macd_line.iloc[-2], signal_line.iloc[-2]
        
        col1.metric("RSI (강도)", f"{c_rsi:.1f}")
        
        # MACD 상태 판정
        macd_status = "상승 추세" if c_macd > c_sig else "하락 추세"
        if p_macd < p_sig and c_macd > c_sig: macd_status = "⭐ 골든크로스"
        elif p_macd > p_sig and c_macd < c_sig: macd_status = "💀 데드크로스"
        col2.metric("MACD 상태", macd_status)
        
        bb_pos = "하단 근접" if curr_p <= lower_bb.iloc[-1] else "상단 근접" if curr_p >= upper_bb.iloc[-1] else "중심선"
        col3.metric("볼린저 밴드", bb_pos)

        # 종합 판정 로직 강화
        st.write("---")
        if (curr_p <= lower_bb.iloc[-1] and c_rsi <= 35) or (p_macd < p_sig and c_macd > c_sig):
            st.markdown("<div class='signal-box' style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
            st.info("RSI가 낮거나 MACD 골든크로스가 발생했습니다. 매수하기 좋은 타이밍입니다!")
        elif (curr_p >= upper_bb.iloc[-1] and c_rsi >= 65) or (p_macd > p_sig and c_macd < c_sig):
            st.markdown("<div class='signal-box' style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
            st.info("RSI가 높거나 MACD 데드크로스가 발생했습니다. 수익을 실현할 때입니다!")
        else:
            st.markdown("<div class='signal-box' style='background-color:#FFF9EE; color:#FFA000; border-color:#FFA000;'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)

        # 차트 (MACD 추가)
        st.write("---")
        st.line_chart(pd.DataFrame({'가격': close_series, '상단밴드': upper_bb, '하단밴드': lower_bb}).tail(60))
        st.write("**[MACD 추세 차트]**")
        st.line_chart(pd.DataFrame({'MACD선': macd_line, '시그널선': signal_line}).tail(60))
    else:
        st.error("데이터를 가져올 수 없습니다.")
