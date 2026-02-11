import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도 타이밍 진단기")

st.info("💡 삼성전자: 005930.KS / 실리콘투: 247020.KQ / 아이온큐: IONQ")

ticker = st.text_input("분석할 종목 코드를 입력하세요", value="005930.KS").strip()

if ticker:
    try:
        # 데이터 가져오기
        data = yf.download(ticker, period="1y", multi_level_index=False)
        if data.empty:
            st.warning("데이터를 불러오지 못했습니다. 코드를 확인해 주세요.")
        else:
            df = data.copy()
            df.columns = [col.lower() for col in df.columns]
            close = df['close']
            
            # 지표 계산
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())

            st.write(f"### {ticker} 현재가: {int(close.iloc[-1]):,}원")
            
            # 신호 판단
            c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
            if c_rsi <= 30 and c_will <= -80:
                st.error("🚨 [강력 매수] 바닥권 신호입니다! 매수를 고려해 보세요.")
            elif c_rsi >= 70 and c_will >= -20:
                st.success("💰 [매도 권장] 천장권 신호입니다! 수익 실현을 준비하세요.")
            else:
                st.warning("🟡 [관망] 현재는 신호 대기 중입니다.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
     
