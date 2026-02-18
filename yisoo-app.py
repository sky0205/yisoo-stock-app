import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (종합 분석 박스 및 세부 지표 카드 최적화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* 신호등 및 현재가 스타일 */
    .signal-box { padding: 30px; border-radius: 20px 20px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 30px; }
    .price-text { font-size: 38px; color: #1E3A8A; font-weight: 900; }

    /* [선생님 요청] 종합 분석 리포트 박스 스타일 */
    .report-main-box { 
        background: #F8FAFC; 
        border: 3px solid #1E3A8A; 
        padding: 30px; 
        border-radius: 20px; 
        margin-bottom: 35px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
    }
    .report-header { font-size: 28px; font-weight: 900; color: #1E3A8A; margin-bottom: 20px; border-bottom: 4px solid #1E3A8A; padding-bottom: 10px; display: inline-block; }
    .report-content { font-size: 20px; color: #334155; line-height: 1.8; margin-bottom: 15px; }
    .report-tag { background: #1E3A8A; color: white; padding: 4px 12px; border-radius: 8px; font-size: 16px; margin-right: 10px; }

    /* [선생님 요청] 4대 지표 세부 분석 카드 */
    .detail-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    .detail-title { font-size: 22px; font-weight: 900; color: #1E3A8A; margin-bottom: 10px; display: flex; align-items: center; }
    .detail-info { font-size: 18px; color: #475569; border-top: 1px dashed #CBD5E1; pt: 10px; mt: 10px; line-height: 1.6; }

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

            # 지표 계산 로직
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2)); up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = float((exp12 - exp26).iloc[-1]); sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = float(((h14.iloc[-1] - curr_p) / (h14.iloc[-1] - l14.iloc[-1])) * -100)

            # [1] 종목 및 신호등/현재가
            st.header(f"🏢 {stock_name} ({symbol})")
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)
            
            p_val = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {p_val}</div></div>", unsafe_allow_html=True)

            # [2] 종합 분석 리포트 박스 (선생님 요청사항)
            st.markdown("<div class='report-main-box'>", unsafe_allow_html=True)
            st.markdown("<div class='report-header'>🔍 종합 분석 리포트</div>", unsafe_allow_html=True)
            
            # 종합 분석 알고리즘
            if macd > sig:
                trend_eval = "상승 추세가 강화되고 있으며 매수 심리가 살아나고 있습니다."
            else:
                trend_eval = "하락 추세가 이어지거나 매수세가 약화되어 주의가 필요한 시점입니다."
            
            if rsi < 40 and wr < -70:
                pos_eval = "현재 극심한 과매도 구간으로 기술적 반등 가능성이 매우 높습니다."
            elif rsi > 60 and wr > -30:
                pos_eval = "과열 징후가 포착되었습니다. 추가 상승보다는 차익 실현 압력이 클 것입니다."
            else:
                pos_eval = "안정적인 흐름 속에 있으나 뚜렷한 방향성을 탐색 중입니다."

            st.markdown(f"<div class='report-content'><span class='report-tag'>추세</span> {trend_eval}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='report-content'><span class='report-tag'>심리</span> {pos_eval}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='report-content'><span class='report-tag'>결론</span> <b>{('공포를 이겨내고 매수' if is_buy else '탐욕을 참고 매도' if is_sell else '인내하며 관망')}</b> 전략을 제안합니다.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # [3] 4대 지표 세부사항 분석 (선생님 요청사항)
            st.write("### 📊 4대 지표 세부 정밀 분석")
            
            # ① 볼린저 밴드
            st.markdown(f"""<div class='detail-card'><div class='detail-title'>① 볼린저 밴드 (Volatility)</div>
            <div class='detail-info'><b>지지선: {lo_b:,.0f} / 저항선: {up_b:,.0f}</b><br>
            현재 가격은 통계적 범위 내 하단으로부터 약 <b>{((curr_p-lo_b)/(up_b-lo_b)*100):.1f}%</b> 위치에 있습니다. 
            {'밴드 하단을 건드리는 구간은 저점 매수의 기회가 될 수 있습니다.' if curr_p < lo_b else '상단 저항선에 근접할수록 매도 압력이 강해지는 경향이 있습니다.' if curr_p > up_b else '밴드 중심부에서 안정적인 가격을 형성 중입니다.'}</div></div>""", unsafe_allow_html=True)
            

            # ② RSI 심리도
            st.markdown(f"""<div class='detail-card'><div class='detail-title'>② RSI (Relative Strength)</div>
            <div class='detail-info'><b>현재 수치: {rsi:.1f}%</b><br>
            투자자들의 심리를 수치화한 지표입니다. 30% 이하인 <b>{rsi:.1f}%</b>는 '공포'에 의한 매도 과다 상태를 의미하며, 
            반대로 70% 이상은 '탐욕'에 의한 과매수 상태로 봅니다. 현재는 <b>{'침체' if rsi < 35 else '과열' if rsi > 65 else '평온'}</b> 상태입니다.</div></div>""", unsafe_allow_html=True)
            

            # ③ MACD 추세
            st.markdown(f"""<div class='detail-card'><div class='detail-title'>③ MACD (Trend Momentum)</div>
            <div class='detail-info'><b>시그널 대비 수치: {macd:.2f}</b><br>
            단기 이동평균선이 장기 이동평균선을 뚫고 올라가는 <b>골든크로스({'유효' if macd > sig else '미발생'})</b> 여부를 체크합니다. 
            현재 <b>{'상승 에너지가 시그널을 앞서고 있어' if macd > sig else '하락 압력이 시그널을 아래로 누르고 있어'}</b> 추세의 힘이 강합니다.</div></div>""", unsafe_allow_html=True)
            

            # ④ Williams %R 수급
            st.markdown(f"""<div class='detail-card'><div class='detail-title'>④ Williams %R (Overbought/Oversold)</div>
            <div class='detail-info'><b>현재 수급: {wr:.1f}</b><br>
            -80 이하인 <b>{wr:.1f}</b>는 단기적으로 물량이 쏟아져 나온 바닥권임을 나타냅니다. 반등의 속도가 가장 빠른 지표로, 
            현재 <b>{'바닥권에서 반등을 준비하는' if wr < -80 else '천장권에서 조정을 기다리는' if wr > -20 else '정상적인 수급'}</b> 구간입니다.</div></div>""", unsafe_allow_html=True)

            # [4] 목표가 제안
            fair_v = curr_p * 1.15
            st.markdown(f"<div class='value-card'>💎 1차 목표가 제안: {f'${fair_v:,.2f}' if is_us else f'{fair_v:,.0f}원'}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류 발생! ({e})")
