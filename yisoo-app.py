import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (종합 분석 리포트 및 현재가 레이아웃 최적화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* 신호등 스타일 */
    .signal-box { padding: 30px; border-radius: 20px 20px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 현재가 박스 스타일 */
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 25px; }
    .price-text { font-size: 38px; color: #1E3A8A; font-weight: 900; }

    /* 종합 추세 분석 리포트 스타일 */
    .report-card { background: #F8FAFC; border: 2px solid #E2E8F0; padding: 30px; border-radius: 15px; margin-bottom: 25px; border-left: 10px solid #1E3A8A; }
    .report-title { font-size: 26px; font-weight: 900; color: #1E3A8A; margin-bottom: 15px; display: flex; align-items: center; }
    .report-item { font-size: 20px; color: #334155; margin-bottom: 12px; line-height: 1.6; }
    
    /* 상세 지표 카드 */
    .detail-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .detail-header { font-size: 19px; font-weight: 800; color: #1E3A8A; margin-bottom: 5px; }
    .detail-body { font-size: 17px; color: #475569; }

    .value-card { font-size: 28px; font-weight: 900; color: #FFFFFF !important; padding: 25px; background: #1E3A8A; border-radius: 15px; text-align: center; margin-bottom: 30px; }
    h1, h2, h3 { color: #1E3A8A !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

def get_stock_name(symbol):
    try:
        if symbol.isdigit():
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text
        return symbol
    except: return symbol

if 'history' not in st.session_state: st.session_state['history'] = []
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👴 이수할아버지의 주식분석기 v36000")
symbol = st.text_input("📊 종목코드(6자리) 또는 미장 티커 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            stock_name = get_stock_name(symbol)
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            is_us = not symbol.isdigit()

            # 지표 계산
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2)); up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = float((exp12 - exp26).iloc[-1]); sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = float(((h14.iloc[-1] - curr_p) / (h14.iloc[-1] - l14.iloc[-1])) * -100)

            # [1] 종목 정보
            st.header(f"🏢 {stock_name} ({symbol})")
            
            # [2] 신호등 + 현재가 통합
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)
            
            p_val = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {p_val}</div></div>", unsafe_allow_html=True)

            # [3] 종합 추세 분석 리포트 (선생님 요청사항)
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<div class='report-title'>🔍 이수할아버지의 종합 분석 리포트</div>", unsafe_allow_html=True)
            
            # 추세 분석 엔진
            if macd > sig and curr_p > ma20.iloc[-1]:
                trend_msg = "현재 주가는 탄탄한 매수세를 바탕으로 우상향 궤도에 진입했습니다."
            elif macd < sig and curr_p < ma20.iloc[-1]:
                trend_msg = "추세가 꺾이며 하락 압력이 거세지고 있습니다. 보수적인 접근이 필요합니다."
            else:
                trend_msg = "상승과 하락의 팽팽한 줄다리기가 이어지는 변곡점 구간입니다."
            
            # 심리 분석 엔진
            if rsi < 35: psych_msg = "대중의 공포가 극에 달했습니다. 기술적 반등 가능성이 매우 높은 자리입니다."
            elif rsi > 65: psych_msg = "탐욕이 지배하는 과열권입니다. 신규 진입보다는 익절 타이밍을 고민하세요."
            else: psych_msg = "시장의 심리가 안정적입니다. 큰 변동성보다는 박스권 흐름이 예상됩니다."

            st.markdown(f"<div class='report-item'><b>📈 추세 진단:</b> {trend_msg}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='report-item'><b>⚖️ 시장 심리:</b> {psych_msg}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='report-item'><b>💎 결론:</b> {('바닥 확인 후 분할 매수' if is_buy else '과열 경계 및 분할 매도' if is_sell else '비중 유지 및 관망')} 전략이 유효해 보입니다.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # [4] 4대 지수 세부 지표
            st.write("### 📋 4대 세부 지표 분석")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='detail-card'><div class='detail-header'>① 볼린저 밴드</div><div class='detail-body'>{lo_b:,.0f} ~ {up_b:,.0f}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='detail-card'><div class='detail-header'>② RSI 심리도</div><div class='detail-body'>{rsi:.1f}% ({'공포' if rsi < 35 else '과열' if rsi > 65 else '정상'})</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='detail-card'><div class='detail-header'>③ MACD 추세</div><div class='detail-body'>{'상승 우위' if macd > sig else '하락 압력'}</div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='detail-card'><div class='detail-header'>④ Williams %R</div><div class='detail-body'>{wr:.1f} ({'바닥권' if wr < -80 else '천장권' if wr > -20 else '정상'})</div></div>", unsafe_allow_html=True)

            # [5] 목표가
            fair_v = curr_p * 1.15
            st.markdown(f"<div class='value-card'>💎 1차 목표가 제안: {f'${fair_v:,.2f}' if is_us else f'{fair_v:,.0f}원'}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생! ({e})")
