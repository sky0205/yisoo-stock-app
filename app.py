import streamlit as st
import yfinance as yf
import pandas_ta as ta

# 앱 제목 및 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도 타이밍 진단기")

# 종목 입력 (기본값: 삼성전자)
ticker = st.text_input("종목 코드를 입력하세요 (예: 삼성전자는 005930.KS)", value="005930.KS")

if ticker:
    # 데이터 불러오기
    data = yf.download(ticker, period="1y")
    
    # 지표 계산 (볼린저밴드, RSI, 윌리엄 %R)
    data.ta.bbands(length=20, std=2, append=True)
    data.ta.rsi(length=14, append=True)
    data.ta.willr(length=14, append=True)
    
    curr_price = data['Close'].iloc[-1]
    rsi = data['RSI_14'].iloc[-1]
    willr = data['WILLR_14'].iloc[-1]

    # 판단 로직 (선생님의 투자 철학)
    st.write(f"### 현재가: {int(curr_price):,}원")
    
    if rsi <= 30 and willr <= -80:
        st.error("🚨 [강력 매수] 바닥권입니다! 지금 사야 합니다.")
    elif rsi >= 70 and willr >= -20:
        st.success("💰 [매도 권장] 과열권입니다! 수익을 실현하세요.")
    else:
        st.warning("🟡 [관망] 신호가 올 때까지 기다리는 중입니다.")

    # 상세 지표 표
    st.write("---")
    st.write("### 📊 현재 지표 상태")
    st.table({
        "지표명": ["RSI (상대강도)", "Williams %R (윌리엄)", "볼린저 밴드"],
        "현재 수치": [f"{rsi:.2f}", f"{willr:.2f}", "밴드 내부"],
        "상태": ["공포 구간" if rsi < 30 else "과열 구간" if rsi > 70 else "보통",
                "발바닥" if willr < -80 else "천장" if willr > -20 else "보통",
                "안정적"]
    })
