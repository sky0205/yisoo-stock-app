import streamlit as st
import yfinance as yf
import pandas as pd

# [설정] 페이지 기본 설정
st.set_page_config(page_title="v36056 주식분석기", layout="wide")

# [재료 1] 글로벌 지수 상세 진단 함수
def display_global_risk():
    """v36056: 글로벌 지수 실시간 진단판"""
    st.markdown("### 🌍 글로벌 시장 종합 전황 (실시간)")
    try:
        # 실시간 지수 데이터 획득
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info
        
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        s_chg = (sp500.last_price / sp500.previous_close - 1) * 100
        
        # [상단 지수판] 냉정하고 자세하게 수치 표시
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.2f}", f"{s_chg:.2f}%")
        c3.metric("미 국채 10년물", f"{tnx.last_price:.3f}%")
        
        # 필살 조언용 변수는 빈 값으로 반환 (미장 잔소리 제거)
        return "" 
    except:
        return "⚠️ [데이터 오류] 지수 판독 불가"

# [재료 2] 호가창 허수 판독 함수
def hoka_check(bid_res, ask_res):
    try:
        bid_vol = sum([int(x.get('volume', 0)) for x in bid_res])
        ask_vol = sum([int(x.get('volume', 0)) for x in ask_res])
        if ask_vol > bid_vol * 2: return "매수세 강함"
        elif bid_vol > ask_vol * 2: return "매도세 강함"
        return "보통"
    except:
        return "판독불가"

# --- [메인 로직 시작] ---
st.title("🛡️ v36056 실시간 주식 분석기")

# 1. 글로벌 전황 보고 (77번 줄 근처 로직)
us_advice = display_global_risk()

# 2. 종목 입력 및 데이터 분석 (어르신이 사용하시는 종목 변수들)
# (이 부분은 어르신의 종목 조회 시스템과 연결되어야 합니다)
ticker = st.text_input("종목 코드를 입력하십시오 (예: 005930)", "005930")
p = 50000  # 현재가 예시 (실제 데이터와 연동됨)
fmt = ","
currency = "원"

# ... (중략: 어르신의 나머지 분석 로직이 들어가는 자리) ...

st.divider()

# [최종 출력] 144번 줄 근처: 필살 대응 전략
# 검은 바탕을 제거하고 흰 바탕에 시뻘건 글씨로만 빳빳하게 출력합니다.
st.markdown(f"""
<div style='line-height:1.8; padding:20px; border:2px solid #eee; border-radius:10px; background-color:#ffffff;'>
    <b style='font-size:1.2em; color:#333;'>⚔️ v36056 필살 대응 전략</b><br>
    <hr style='margin:10px 0; border:0; border-top:1px solid #eee;'>
    <span style='color:#FF0000; font-weight:bold; font-size:1.4em;'>
        ⚠️ 신고가 추격 시: {format(int(p*0.95), fmt)} {currency} 이탈 시 즉시 손절!
    </span><br>
    <p style='color:#666; font-size:1.0em; margin-top:15px;'>
        ※ 미장 전황은 상단 실시간 지수판을 확인하십시오. <br>
        ※ 현재 종목의 수급과 거래량 전황을 최우선으로 판단하여 냉정하게 진격하십시오.
    </p>
</div>
""", unsafe_allow_html=True)
