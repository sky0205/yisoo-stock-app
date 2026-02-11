import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도 타이밍 진단기")

# 1. [핵심] 종목명과 코드를 연결해주는 '똑똑한 사전'
stock_dict = {
    "삼성전자": "005930.KS",
    "실리콘투": "247020.KQ",
    "아이온큐": "IONQ",
    "넷플릭스": "NFLX",
    "쿠팡": "CPNG",
    "애플": "AAPL",
    "테슬라": "TSLA",
    "엔비디아": "NVDA"
}

st.info("💡 종목명(예: 삼성전자, 실리콘투)이나 코드(005930.KS)를 입력하세요.")

# 2. 사용자 입력 처리 (이름을 치면 코드로 자동 변환)
user_input = st.text_input("종목을 입력하세요", value="실리콘투").strip()

# 사전에서 이름을 찾아보고, 없으면 입력한 그대로(코드) 사용합니다.
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    with st.spinner(f"'{user_input}' 데이터를 분석 중입니다..."):
        try:
            # 3. [보강] 코스닥 및 데이터 오류 방지를 위한 다운로드 설정
            data = yf.download(ticker, period="1y", multi_level_index=False)
            
            if data.empty:
                st.error(f"❌ '{user_input}' 데이터를 가져오지 못했습니다. 코드를 다시 확인해 주세요.")
            else:
                df = data.copy()
                df.columns = [str(col).lower() for col in df.columns]
                close = df['close']
                
                # 화폐 단위 설정 (한국 주식 vs 미국 주식)
                is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
                unit = "원" if is_korea else "달러($)"
                price_format = "{:,.0f}" if is_korea else "{:,.2f}"

                # 지표 계산
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())

                # 결과 출력
                curr_price = close.iloc[-1]
                st.subheader(f"🔍 {user_input} ({ticker}) 분석 결과")
                st.metric(label="현재가", value=f"{price_format.format(curr_price)} {unit}")
                
                c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
                
                if c_rsi <= 30 and c_will <= -80:
                    st.error("🚨 [강력 매수] 바닥권 신호입니다!")
                elif c_rsi >= 70 and c_will >= -20:
                    st.success("💰 [매도 권장] 과열권 신호입니다!")
                else:
                    st.warning("🟡 [관망] 현재는 신호가 없습니다.")
                    
                st.write(f"📊 RSI: {c_rsi:.2f} | Williams %R: {c_will:.2f}")

        except Exception as e:
            st.error("데이터 서버와 연결이 잠시 불안정합니다. 잠시 후 다시 시도해 주세요.")
           
          
