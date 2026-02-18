import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (불필요한 여백 제거 및 시인성 강화)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; font-size: 45px !important; font-weight: 900; border: 12px solid; margin-bottom: 5px; } /* 여백 최소화 */
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    
    /* 지표 및 분석 카드 스타일 */
    .indicator-card { background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 15px; padding: 25px; margin-bottom: 15px; }
    .indicator-title { font-size: 20px; color: #1E3A8A; font-weight: 900; margin-bottom: 8px; border-bottom: 2px solid #CBD5E1; padding-bottom: 5px; }
    .indicator-value { font-size: 24px; color: #1E293B; font-weight: 800; }
    .indicator-desc { font-size: 18px; color: #475569; line-height: 1.5; }
    
    /* 종합 추세 분석 리포트 스타일 */
    .trend-report { background: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 30px; border-radius: 15px; margin-top: 0px; margin-bottom: 20px; }
    .trend-title { font-size: 26px; font-weight: 900; color: #1E3A8A; margin-bottom: 15px; }
    .trend-item { font-size: 20px; color: #334155; margin-bottom: 12px; line-height: 1.6; }
    
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

            # [1] 기본 정보 표시
            st.header(f"🏢 {stock_name} ({symbol})")
            price_txt = f"${curr_p:,.2f}" if is_us else f"{curr_p:,.0f}원"
            
            # 신호등 로직
            is_buy = curr_p <= lo_b or rsi < 35 or wr < -80
            is_sell = curr_p >= up_b or rsi > 65 or wr > -20
            
            if is_buy: st.markdown("<div class='signal-box buy'>🔴 매수 적기 (바닥권)</div>", unsafe_allow_html=True)
            elif is_sell: st.markdown("<div class='signal-box sell'>🟢 매도 검토 (고점권)</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='signal-box wait'>🟡 관망 유지 (중립)</div>", unsafe_allow_html=True)

            # [2] 종합 추세 분석 리포트 (박스 간격 조정 완료)
            st.markdown("<div class='trend-report'>", unsafe_allow_html=True)
            st.markdown("<div class='trend-title'>🔍 이수할아버지의 종합 추세 분석</div>", unsafe_allow_html=True)
            
            # 추세 분석 심층 로직
            if macd > sig and curr_p > ma20.iloc[-1]:
                trend_msg = "단기/중기 추세가 모두 정배열로 진입했습니다. 강한 매수 에너지가 느껴지는 구간입니다."
            elif macd < sig and curr_p < ma20.iloc[-1]:
                trend_msg = "추세가 하락세로 기울었습니다. 무리한 물타기보다는 바닥 확인이 우선입니다."
            else:
                trend_msg = "상승과 하락 에너지가 팽팽히 맞서고 있습니다. 변곡점이 머지 않았으니 신중히 지켜보세요."
            
            st.markdown(f"<div class='trend-item'><b>📈 추세 진단:</b> {trend_msg}</div>", unsafe_allow_html=True)
            
            # 수급 및 심리 분석
            if rsi < 35 and wr < -80:
                psych_msg = "시장이 완전히 얼어붙었습니다. 역발상 투자자에게는 최고의 '바닥 줍기' 기회가 될 수 있습니다."
            elif rsi > 65 and wr > -20:
                psych_msg = "과열 징후가 뚜렷합니다. 탐욕이 지배하는 구간이니 차익 실현을 고려할 시점입니다."
            else:
                psych_msg = "군중 심리가 안정적입니다. 큰 변동성보다는 박스권 내 움직임이 예상됩니다."
                
            st.markdown(f"<div class='trend-item'><b>⚖️ 수급 및 심리:</b> {psych_msg}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # [3] 4대 핵심 지표 상세 분석 (수치 및 상세 설명)
            st.write("### 📋 4대 핵심 지표 상세 브리핑")
            
            # 지표별 상세 분석 내용
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>① 볼린저 밴드 (지지/저항)</div><div class='indicator-value'>밴드 범위: {lo_b:,.0f} ~ {up_b:,.0f}</div><div class='indicator-desc'>{'하단 돌파: 매수세 유입 기대' if curr_p < lo_b else '상단 돌파: 매도 압력 증가' if curr_p > up_b else '평균 회귀 진행 중'}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>② RSI (공포와 탐욕)</div><div class='indicator-value'>현재 심리: {rsi:.1f}%</div><div class='indicator-desc'>{'공포 구간: 매수 관점' if rsi < 35 else '탐욕 구간: 경계 관점' if rsi > 65 else '정상 심리 유지 중'}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>③ MACD (자금의 방향)</div><div class='indicator-value'>추세 강도: {macd:.2f}</div><div class='indicator-desc'>{'상승 엔진 가동: 긍정적' if macd > sig else '상승 엔진 정지: 주의 요망'}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='indicator-card'><div class='indicator-title'>④ Williams %R (단기 반등력)</div><div class='indicator-value'>수급 에너지: {wr:.1f}</div><div class='indicator-desc'>{'단기 과매도: 반등 준비' if wr < -80 else '단기 과매수: 조정 가능성' if wr > -20 else '중립적 에너지'}</div></div>", unsafe_allow_html=True)

            # [4] 목표가 제안
            fair_v = curr_p * 1.15
            target_txt = f"${fair_v:,.2f}" if is_us else f"{fair_v:,.0f}원"
            st.markdown(f"<div class='value-card'>💎 이수할아버지의 1차 목표가 제안: {target_txt}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다! (에러: {e})")
