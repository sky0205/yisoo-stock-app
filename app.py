import streamlit as st
import yfinance as yf
import pandas as pd

# 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도 타이밍 진단기")

# 안내 문구
st.info("💡 삼성전자: 005930.KS / 실리콘투: 247020.KQ / 아이온큐: IONQ")

# [보강] 입력값에서 앞뒤 빈칸을 없애고 무조건 대문자로 변환합니다.
ticker_input = st.text_input("종목 코드를 입력하세요", value="247020.KQ").strip().upper()

if ticker_input:
    try:
        # [보강] 데이터를 가져올 때 오류를 줄이는 설정을 추가했습니다.
        data = yf.download(ticker_input, period="1y", multi_level_index=False)
        
        if data.empty:
            st.error(f"❌ '{ticker_input}' 데이터를 찾을 수 없습니다. 코드 뒤에 .KS나 .KQ가 붙었는지 확인해 주세요.")
        else:
            df = data.copy()
            # 모든 열 이름을 소문자로 통일 (오류 방지)
            df.columns = [str(col).lower() for col in df.columns]
            
            # 지표 계산
            close = df['close']
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            high_14 = df['high'].rolling(14).max()
            low_14 = df['low'].rolling(14).min()
            willr = -100 * (high_14 - close) / (high_14 - low_14)

            # 결과 출력
            curr_price = close.iloc[-1]
            st.subheader(f"🔍 {ticker_input} 분석 결과")
            st.metric(label="현재가", value=f"{int(curr_price):,}원")
            
            c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
            
            # 신호 판독
            if c_rsi <= 30 and c_will <= -80:
                st.error("🚨 [강력 매수] 바닥권 신호입니다! 적극 검토해 보세요.")
            elif c_rsi >= 70 and c_will >= -20:
                st.success("💰 [매도 권장] 과열권 신호입니다! 수익 실현을 준비하세요.")
            else:
                st.warning("🟡 [관망] 현재는 뚜렷한 신호가 없는 평온한 상태입니다.")
                
            # 상세 지표 확인용 표
            st.write("---")
            st.write("📊 현재 지표 수치")
            st.write(f"- RSI: {c_rsi:.2f} (30 이하 매수 / 70 이상 매도)")
            st.write(f"- Williams %R: {c_will:.2f} (-80 이하 매수 / -20 이상 매도)")

    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다. (원인: {e})")
           
          
          
