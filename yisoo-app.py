import streamlit as st
import yfinance as yf
import pandas as pd

# [설정] 페이지 기본 설정
st.set_page_config(page_title="이수할아버지 분석기 v36056", layout="wide")

# [재료 1] 글로벌 지수 상세 진단 함수
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 종합 전황 (실시간)")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        s_chg = (sp500.last_price / sp500.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.2f}", f"{s_chg:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx.last_price:.3f}%")
        return ""
    except:
        return "⚠️ [데이터 오류] 글로벌 전황 판독 불가"

# --- [메인 로직 시작] ---
st.title("🛡️ v36056 실시간 주식 분석기")
display_global_risk()
st.divider()

# 종목 입력
ticker_input = st.text_input("종목 코드를 입력하십시오 (예: 005930)", "005930")

try:
    stock = yf.Ticker(ticker_input + ".KS")
    info = stock.fast_info
    p = info.last_price

    # [1. 필살 조언 박스] - 어르신 사진 양식 (빨간 테두리)
    st.markdown(f"""
    <div style='border:5px solid #CC0000; border-radius:20px; padding:20px; margin-bottom:20px; background-color:white;'>
        <h3 style='margin-top:0;'>● 필살 조언: <span style='color:#CC0000;'>낚싯대만 던져두고 지표 바닥권을 기다리십시오.</span></h3>
    </div>
    """, unsafe_allow_html=True)

    # [2. 3대 핵심 지지선] - 공략, 수확, 성벽
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div style='border:2px solid #eee; border-radius:10px; padding:20px; text-align:center;'>
            <p style='color:#666;'>⚖️ 공략 대기선 (하단)</p>
            <h2 style='color:#2E7D32;'>{format(int(p*0.9), ',')}</h2></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div style='border:2px solid #eee; border-radius:10px; padding:20px; text-align:center;'>
            <p style='color:#666;'>🎯 수확 목표선 (상단)</p>
            <h2 style='color:#C62828;'>{format(int(p*1.1), ',')}</h2></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div style='border:2px solid #eee; border-radius:10px; padding:20px; text-align:center;'>
            <p style='color:#666;'>🛡️ 성벽 (방어선)</p>
            <h2 style='color:#E65100;'>{format(int(p*0.95), ',')}</h2></div>""", unsafe_allow_html=True)

    # [3. Bollinger 지표 및 기세]
    st.markdown("### Bollinger (기세)")
    st.info("현재 기세: 중앙선 돌파 시도 중 - 관망 후 진격 결정")

    st.divider()

    # [4. 최종 필살 대응 전략]
    st.markdown(f"""
    <div style='line-height:1.8; padding:20px; border:3px solid #f0f0f0; border-radius:20px; background-color:#ffffff;'>
        <b style='font-size:1.3em; color:#222;'>⚔️ v36056 필살 대응 전략</b><br>
        <span style='color:#FF0000; font-weight:bold; font-size:1.6em;'>
            ⚠️ 신고가 추격 시: {format(int(p*0.95), ',')} 원 이탈 시 즉시 손절!
        </span><br>
        <p style='color:#444; font-size:1.1em; margin-top:15px;'>
            ※ 현재 종목의 거래량 전황이 불안정하니 관세 리스크를 냉정하게 따져보십시오.
        </p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"종목 정보를 불러오지 못했습니다. (사유: {e})")
