import streamlit as st
import FinanceDataReader as fdr # 네이버/다음 금융 데이터를 가져오는 도구
import pandas as pd

st.title("👨‍💻 이수할아버지의 네이버 실시간 분석기")

# 한국 주식은 6자리 번호만 넣으면 됩니다 (예: 005930)
t_input = st.text_input("종목코드 입력", "005930")

if t_input:
    # 네이버 금융에서 2026년 최신 데이터를 가져옵니다
    df = fdr.DataReader(t_input, '2026-01-01')
    
    if not df.empty:
        curr_price = df['Close'].iloc[-1]
        st.header(f"현재가: {curr_price:,.0f}원")
        
        # 선생님의 평단가 58,000원 기준 수익률
        avg_cost = 58000
        profit = (curr_price - avg_cost) / avg_cost * 100
        st.subheader(f"현재 수익률: {profit:.2f}% 🔥")
        
        # 그래프 출력
        st.line_chart(df['Close'])
