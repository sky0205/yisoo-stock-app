import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (현재가 문구 및 박스 디자인 최적화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* 신호등 스타일 */
    .signal-box { padding: 30px; border-radius: 20px 20px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 현재가 박스 스타일 (신호등 하단 결합) */
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 25px; }
    .price-text { font-size: 38px; color: #1E3A8A; font-weight: 900; }

    /* 정밀 분석 카드 스타일 */
    .detail-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 2px 2px 12px rgba(0,0,0,0.05); }
    .detail-header { font-size: 22px; font-weight: 900; color: #1E3A8A; margin-bottom: 10px; display: flex; align-items: center; }
    .detail-badge { background: #1E3A8A; color: white; font-size: 14px; padding: 2px 8px; border-radius: 5px; margin-left: 10px; }
    .detail-body { font-size: 18px; color: #334155; line-height: 1.6; }

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

            # [1] 종목명
            st.header(f"🏢 {stock_name} ({symbol})")
            
            # [2] 신호등 + 현재가 통합 박스 (선생님 요청사항 반영)
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)
            
            price_val = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            # "현재가" 문구 추가
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {price_val}</div></div>", unsafe_allow_html=True)

            # [3] 4대 지수 정밀 분석 리포트
            st.write("### 🔍 이수할아버지의 정밀 분석 리포트")
            
            # 볼린저 밴드
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>① 볼린저 밴드 <span class='detail-badge'>변동성</span></div>
            <div class='detail-body'>현재 주가는 밴드 내 <b>{((curr_p-lo_b)/(up_b-lo_b)*100):.1f}%</b> 위치에 있습니다. {'하단 지지선 근처로 반등 에너지가 모이고 있습니다.' if curr_p < lo_b else '상단 저항선에 도달하여 일시적 눌림이 예상됩니다.' if curr_p > up_b else '안정적인 밴드 내 흐름을 유지 중입니다.'}</div></div>""", unsafe_allow_html=True)
            
            # RSI
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>② RSI <span class='detail-badge'>투자심리</span></div>
            <div class='detail-body'>현재 심리 지수는 <b>{rsi:.1f}%</b>입니다. {'대중의 공포가 극에 달한 바닥권입니다.' if rsi < 35 else '투기적 탐욕이 지배하는 과열권입니다.' if rsi > 65 else '안정적인 투자 심리가 유지되고 있습니다.'}</div></div>""", unsafe_allow_html=True)
            
            # MACD
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>③ MACD <span class='detail-badge'>추세강도</span></div>
            <div class='detail-body'>{'골든크로스 발생: 상승 엔진이 가동되었습니다.' if macd > sig else '데드크로스 발생: 하락 압력이 강해지고 있습니다.'}</div></div>""", unsafe_allow_html=True)
            
            # Williams %R
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>④ Williams %R <span class='detail-badge'>수급에너지</span></div>
            <div class='detail-body'>현재 에너지 <b>{wr:.1f}</b>. {'단기 수급 바닥으로 기술적 반등이 임박했습니다.' if wr < -80 else '단기 수급 천장으로 조정 가능성이 높습니다.' if wr > -20 else '정상적인 수급 흐름입니다.'}</div></div>""", unsafe_allow_html=True)

            # [4] 목표가
            fair_v = curr_p * 1.15
            st.markdown(f"<div class='value-card'>💎 1차 목표가 제안: {f'${fair_v:,.2f}' if is_us else f'{fair_v:,.0f}원'}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"데이터 로드 실패! ({e})")
