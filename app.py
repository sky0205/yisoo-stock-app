import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도·윌리엄 진단기")

# [보강] 데이터를 기억해서 멈춤을 방지하는 기능
@st.cache_data(ttl=600)
def get_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1y", multi_level_index=False)
        return data
    except:
        return None

# 2. 검색 기록 및 똑똑한 사전
if 'history' not in st.session_state: st.session_state['history'] = []

stock_dict = {
    "삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ",
    "카카오": "035720.KS", "네이버": "035420.KS", "현대차": "005380.KS",
    "아이온큐": "IONQ", "넷플릭스": "NFLX", "쿠팡": "CPNG", "테슬라": "TSLA"
}

st.info("💡 종목명(유한양행)이나 코드(000660.KS)를 입력하세요.")

# 3. 입력창
user_input = st.text_input("종목을 입력하세요", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    data = get_stock_data(ticker)
    
    if data is None or data.empty:
        st.error(f"❌ '{user_input}' 데이터를 불러올 수 없습니다. 코드 뒤에 .KS나 .KQ를 붙여보세요.")
    else:
        # 검색 성공 시 기록 저장
        if user_input not in st.session_state['history']:
            st.session_state['history'].insert(0, user_input)

        df = data.copy()
        df.columns = [str(col).lower() for col in df.columns]
        close = df['close']
        
        # --- [3대 지표 계산] ---
        # (1) RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))

        # (2) 윌리엄 지수 (Williams %R) - 다시 추가!
        high_14 = df['high'].rolling(14).max()
        low_14 = df['low'].rolling(14).min()
        willr = -100 * (high_14 - close) / (high_14 - low_14)

        # (3) 볼린저 밴드
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)
        # ------------------------

        # 화폐 설정
        is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        
        # 결과 출력
        curr_p = close.iloc[-1]
        st.subheader(f"🔍 {user_input} ({ticker}) 분석 결과")
        st.metric(label="현재가", value=f"{fmt.format(curr_p)} {unit}")
        
        c_rsi = rsi.iloc[-1]
        c_will = willr.iloc[-1]
        c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
        
        # 4. 상세 수치 표 (보기 좋게 정리)
        col1, col2, col3 = st.columns(3)
        col1.metric("RSI (상대강도)", f"{c_rsi:.1f}")
        col2.metric("윌리엄 지수", f"{c_will:.1f}")
        col3.metric("볼린저 하단", f"{fmt.format(c_low)}")

        # 5. 종합 신호 판독 (3대 지표 결합)
        st.write("---")
        if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
            st.error("🚨 [강력 매수 신호] 볼린저 바닥 + RSI 바닥 + 윌리엄 바닥! 절호의 기회입니다.")
        elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
            st.success("💰 [매도 권장 신호] 모든 지표가 천장을 가리키고 있습니다. 수익을 챙기세요!")
        else:
            st.warning("🟡 [관망] 지표가 서로 엇갈리거나 안정권에 있습니다. 조금 더 지켜보세요.")

# 6. 최근 검색 기록
if st.session_state['history']:
    st.write("---")
    st.write("🕒 최근 검색: " + ", ".join(st.session_state['history'][:5]))
