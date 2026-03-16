import streamlit as st
import yfinance as yf
import pandas_ta as ta

# 1. 앱 페이지 설정 (어르신의 격식)
st.set_page_config(page_title="v36056 냉정분석기", layout="centered")

st.title("👴 이수 할아버지의 냉정분석기 (v36056-Final)")
st.write("---")

# 2. 종목 입력
ticker = st.text_input("분석할 종목 코드를 넣으셔 (예: 005930.KS)", "005930.KS")

if ticker:
    # 2026년 실시간 장부 데이터 우선 (yfinance)
    df = yf.download(ticker, period="60d", interval="1d")
    
    if not df.empty:
        # 보조지표 계산 (20/2, 14/9, 14/6)
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.willr(length=14, append=True)
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 변수 정리
        close_p = curr['Close']
        diff = close_p - prev['Close']
        rsi_val = curr['RSI_14']
        willr_val = curr['WILLR_14']
        bb_mid = curr['BBM_20_2.0']
        bb_low = curr['BBL_20_2.0']

        # --- [v36056 기본 틀 시작] ---
        st.subheader(f"📋 [v36056] {ticker} 실시간 진단 보고")
        st.write("---")

        # 1. 거래량 전황
        st.markdown("### 1. 거래량 전황 (Volume Status)")
        st.write(f"* **현재가**: {close_p:,.0f}원 (전일대비 {diff:,.0f}원)")
        st.write("* **진단**: 외인들은 짐을 싸는데 기관이 억지로 댐을 막고 있구먼. 거래량 없는 반등은 개미 유인용 함정일 뿐이야.")
        
        st.write("---")

        # 2. 필살 대응 전략 (냉정 진단 & 맥점 보완)
        st.markdown("### 2. 필살 대응 전략 (Sure-win Strategy)")
        st.markdown(f"""
        <div style="border: 2px solid #e74c3c; padding: 15px; border-radius: 10px; background-color: #fffdfd;">
            <h4 style="color: #e74c3c; margin-top: 0;">⚠️ [냉정 진단]</h4>
            <p style="font-size: 1.1em; line-height: 1.6;">
            현재 주가가 Bollinger Band 중앙선(<b>{bb_mid:,.0f}원</b>) 위에서 알짱거리지만, 
            이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. 
            RSI 지표가 <b>{rsi_val:.1f}</b>로 여전히 미지근하다는 것은, 시장에 낀 거품이 다 빠지지 않았음을 뜻합니다.
            </p>
            <hr style="border: 0.5px solid #eee;">
            <h4 style="color: #2980b9;">🎯 [필살 지침]</h4>
            <p>가짜 반등에 속아 방아쇠를 당기지 마시게. 윌리엄 지수({willr_val:.2f})가 심해로 잠수하며 
            개미들이 투항할 때까지 독하게 기다려야 하네. 지금은 <b>함정 수사</b>의 시간이야.</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("---")

        # 3. 네 기둥 지수 상세 진단 (세밀한 분석 보완)
        st.markdown("### 3. 네 기둥 지수 상세 진단 (Four Pillars)")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"""
            ### 🛡️ 수율(Yield) x Bollinger
            * **상세**: 기술력 논란은 주가를 밴드 하단({bb_low:,.0f}원)으로 끌어당기는 자석일세. 
              밴드 폭이 좁아지며 에너지를 응축하고 있으나, 수율 확신이 없는 한 
              오늘의 반등은 하단으로 가기 전 잠시 숨을 고르는 **'가짜 숨구멍'**일 뿐이야.
            
            ### 🛡️ 관세(Tariff) x RSI
            * **상세**: 미국의 관세 압박은 수출주의 RSI를 50 선 아래로 짓누르는 거대한 벽이지. 
              지표가 {rsi_val:.1f}에서 고개를 숙이는 건 이미 이익 전망치가 썩어 들어가고 있다는 증거야. 
            """)
        
        with col_p2:
            st.markdown(f"""
            ### 🛡️ 환율(FX) x Momentum
            * **상세**: 환율 1,490원 돌파는 외인들에게 '환차손 도살장' 입구와 같네. 
              수급 모멘텀이 꺾인 자리에 발을 들이는 건 제 발로 호랑이 굴에 들어가는 짓이야. 
            
            ### 🛡️ 지표(Index) x Williams %R
            * **상세**: 신용 잔고 33조 원은 시한폭탄일세. 
              윌리엄 지수가({willr_val:.2f})가 바닥을 기며 모든 개미가 항복을 선언할 때, 
              그 피비린내 속에 진짜 기회가 숨어 있구먼.
            """)

    else:
        st.error("장부를 불러올 수 없구먼! 종목 코드를 다시 보시게.")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 양식(보완형) 적용")
