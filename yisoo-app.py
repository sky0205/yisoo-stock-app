import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (정밀 분석용 레이아웃)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 20px 20px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 25px; }
    .price-value { font-size: 40px; color: #1E3A8A; font-weight: 900; }

    /* 정밀 분석 카드 스타일 */
    .detail-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 2px 2px 12px rgba(0,0,0,0.05); }
    .detail-header { font-size: 22px; font-weight: 900; color: #1E3A8A; margin-bottom: 10px; display: flex; align-items: center; }
    .detail-badge { background: #1E3A8A; color: white; font-size: 14px; padding: 2px 8px; border-radius: 5px; margin-left: 10px; }
    .detail-body { font-size: 18px; color: #334155; line-height: 1.6; }
    .detail-footer { font-size: 16px; color: #64748B; margin-top: 10px; font-style: italic; }

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
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
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
            
            p_display = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-value'>{p_display}</div></div>", unsafe_allow_html=True)

            # [2] 4대 지수 세밀 분석 (선생님 요청사항)
            st.write("### 🔍 4대 지수 세밀 분석 리포트")
            
            # ① 볼린저 밴드 세밀 분석
            bb_width = (up_b - lo_b) / ma20.iloc[-1] * 100
            bb_txt = "밴드 폭이 좁아지며 조만간 큰 변동성(상승 혹은 하락)이 나올 응축 구간입니다." if bb_width < 10 else "현재 변동성이 확대되어 추세가 진행 중인 구간입니다."
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>① 볼린저 밴드 <span class='detail-badge'>변동성 파악</span></div>
            <div class='detail-body'>현재 주가는 밴드 내 <b>{((curr_p-lo_b)/(up_b-lo_b)*100):.1f}%</b> 지점에 위치합니다. {bb_txt}</div>
            <div class='detail-footer'>※ 하단 돌파 시 과매도 반등, 상단 돌파 시 과매수 조정을 주의하세요.</div></div>""", unsafe_allow_html=True)
            

            # ② RSI 세밀 분석
            rsi_txt = "시장에 공포가 만연하여 매수세가 실종되었습니다. 역발상적 접근이 필요합니다." if rsi < 30 else "매수세가 과열되어 신규 진입 시 상투를 잡을 위험이 높습니다." if rsi > 70 else "투자 심리가 안정적이며 현재의 추세를 유지하려는 경향이 강합니다."
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>② RSI <span class='detail-badge'>심리 측정</span></div>
            <div class='detail-body'>현재 심리 지수는 <b>{rsi:.1f}%</b>입니다. {rsi_txt}</div>
            <div class='detail-footer'>※ 30 미만은 바닥 신호, 70 이상은 상투 신호로 봅니다.</div></div>""", unsafe_allow_html=True)
            

            # ③ MACD 세밀 분석
            macd_txt = "골든크로스 발생! 단기 매수세가 중기 추세를 돌파하며 상승 탄력이 붙었습니다." if macd > sig else "데드크로스 발생! 매수 에너지가 고갈되어 주가가 힘을 잃고 있습니다."
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>③ MACD <span class='detail-badge'>돈의 흐름</span></div>
            <div class='detail-body'>추세 강도 {macd:.2f}. {macd_txt}</div>
            <div class='detail-footer'>※ 0선 위에서 골든크로스가 나면 매우 강한 상승 신호입니다.</div></div>""", unsafe_allow_html=True)
            

            # ④ Williams %R 세밀 분석
            wr_txt = "단기적으로 바닥을 치고 올라올 준비가 끝났습니다. 빠른 반등이 예상됩니다." if wr < -80 else "단기 고점에 도달하여 차익 실현 매물이 쏟아질 수 있는 자리입니다." if wr > -20 else "단기 수급이 평이하며 박스권 움직임이 예상됩니다."
            st.markdown(f"""<div class='detail-card'><div class='detail-header'>④ Williams %R <span class='detail-badge'>단기 수급</span></div>
            <div class='detail-body'>수급 에너지 <b>{wr:.1f}</b>. {wr_txt}</div>
            <div class='detail-footer'>※ -80 이하에서 -50을 돌파할 때가 강력한 단기 매수 시점입니다.</div></div>""", unsafe_allow_html=True)

            # [3] 최종 목표가
            fair_v = curr_p * 1.15
            st.markdown(f"<div class='value-card'>💎 이수할아버지의 1차 목표가: {f'${fair_v:,.2f}' if is_us else f'{fair_v:,.0f}원'}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류 발생: {e}")
