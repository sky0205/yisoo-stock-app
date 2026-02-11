import streamlit as st
import yfinance as yf
import pandas as pd

# [핵심] 1. 데이터를 기억해두는 기능 (다운 현상 방지)
@st.cache_data(ttl=600) # 10분 동안은 서버 안 가고 기억한 데이터 사용
def get_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1y", multi_level_index=False)
        return data
    except:
        return None

st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도·볼린저 진단기")

# 검색 기록 및 사전 설정
if 'history' not in st.session_state: st.session_state['history'] = []
stock_dict = {"삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ", "아이온큐": "IONQ"}

user_input = st.text_input("종목을 입력하세요 (예: 유한양행)", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    # [핵심] 2. 기억해둔 데이터 꺼내오기
    data = get_stock_data(ticker)
    
    if data is None or data.empty:
        st.error("⚠️ 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    else:
        # 검색 기록 저장
        if user_input not in st.session_state['history']:
            st.session_state['history'].insert(0, user_input)

        df = data.copy()
        df.columns = [str(col).lower() for col in df.columns]
        close = df['close']
        
        # 지표 계산 (RSI, 볼린저 밴드)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        # 결과 출력 (단위 설정 포함)
        is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        
        curr_p = close.iloc[-1]
        st.subheader(f"🔍 {user_input} 분석 결과")
        st.metric(label="현재가", value=f"{fmt.format(curr_p)} {unit}")
        
        # 신호 판단
        c_rsi = rsi.iloc[-1]
        c_upper, c_lower = upper_bb.iloc[-1], lower_bb.iloc[-1]
        
        if curr_p <= c_lower and c_rsi <= 35:
            st.error("🚨 [강력 매수] 바닥입니다! 적극 검토하세요.")
        elif curr_p >= c_upper and c_rsi >= 65:
            st.success("💰 [매도 권장] 천장입니다! 수익 실현하세요.")
        else:
            st.warning("🟡 [관망] 신호 대기 중입니다.")
            
        st.write(f"📊 RSI: {c_rsi:.2f} | 밴드 하단: {fmt.format(c_lower)}{unit}")

if st.session_state['history']:
    st.write("---")
    st.write("🕒 최근 검색: " + ", ".join(st.session_state['history'][:5]))
        
