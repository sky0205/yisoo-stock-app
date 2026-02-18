import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (현재가 박스 및 여백 최적화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* 신호등 스타일 */
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 현재가 박스 스타일 (신호등 바로 아래 배치) */
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 25px; }
    .price-label { font-size: 20px; color: #475569; font-weight: bold; }
    .price-value { font-size: 40px; color: #1E3A8A; font-weight: 900; }

    /* 종합 추세 분석 스타일 */
    .trend-report { background: #F8FAFC; border: 2px solid #E2E8F0; padding: 30px; border-radius: 15px; margin-bottom: 25px; }
    .trend-title { font-size: 26px; font-weight: 900; color: #1E3A8A; margin-bottom: 15px; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; }
    .trend-item { font-size: 20px; color: #334155; margin-bottom: 12px; line-height: 1.6; }
    
    /* 4대 지표 카드 스타일 */
    .indicator-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; padding: 20px; margin-bottom: 10px; }
    .indicator-title { font-size: 18px; color: #1E3A8A; font-weight: 900; }
    .indicator-desc { font-size: 16px; color: #64748B; }

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
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            delta = df['close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = float((exp12 - exp26).iloc[-1]); sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
            wr = float(((h14.iloc[-1] - curr_p) / (h14.iloc[-1] - l14.iloc[-1])) * -100)

            # [1] 종목 정보
            st.header(f"🏢 {stock_name} ({symbol})")
            
            # [2] 신호등 + 현재가 박스 통합 (선생님 요청사항)
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)
            
            price_display = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-label'>실시간 현재가</div><div class='price-value'>{price_display}</div></div>", unsafe_allow_html=True)

            # [3] 종합 추세 분석 리포트
            st.markdown("<div class='trend-report'>", unsafe_allow_html=True)
            st.markdown("<div class='trend-title'>🔍 이수할아버지의 종합 분석 리포트</div>", unsafe_allow_html=True)
            
            # 추세 분석
            if macd > sig and curr_p > ma20.iloc[-1]:
                t_msg = "상승 에너지가 강하게 응축된 상태입니다. 안정적인 우상향 흐름이 기대됩니다."
            elif macd < sig and curr_p < ma20.iloc[-1]:
                t_msg = "하락 힘이 강해지는 구간입니다. 성급한 진입보다는 관망이 유리합니다."
            else:
                t_msg = "방향성을 탐색 중인 변곡점입니다. 지지선 확인이 필요합니다."
            
            # 심리 및 수급 분석
            if rsi < 35: p_msg = "공포 심리가 극에 달해 저가 매수세가 유입될 수 있는 바닥권입니다."
            elif rsi > 65: p_msg = "탐욕 구간에 진입했습니다. 신규 진입은 자제하고 수익 실현을 고민할 때입니다."
            else: p_msg = "시장의 심리가 안정되어 있습니다. 특별한 이슈가 없는 한 현재 흐름을 유지할 전망입니다."
                
            st.markdown(f"<div class='trend-item'><b>📈 추세 진단:</b> {t_msg}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='trend-item'><b>⚖️ 심리 및 수급:</b> {p_msg}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # [4] 4대 핵심 지표 브리핑
            st.write("### 📋 4대 핵심 지표 브리핑")
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>① 볼린저 밴드</div><div class='indicator-desc'>통계적 가격 범위: {lo_b:,.0f} ~ {up_b:,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>② RSI 심리도</div><div class='indicator-desc'>현재 수치: {rsi:.1f}% ({'공포' if rsi < 35 else '탐욕' if rsi > 65 else '안정'})</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>③ MACD 추세</div><div class='indicator-desc'>돈의 흐름: {'상승 우위' if macd > sig else '하락 압력'}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>④ Williams %R</div><div class='indicator-desc'>수급 강도: {wr:.1f} ({'바닥권' if wr < -80 else '천장권' if wr > -20 else '정상'})</div></div>", unsafe_allow_html=True)

            # [5] 목표가
            fair_v = curr_p * 1.15
            target_txt = f"${fair_v:,.2f}" if is_us else f"{fair_v:,.0f}원"
            st.markdown(f"<div class='value-card'>💎 이수할아버지의 1차 목표가 제안: {target_txt}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류 발생! 코드번호를 다시 확인해 주세요. ({e})")
