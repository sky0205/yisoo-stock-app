import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 스타일 설정 (선생님 전용 레이아웃)
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 20px 20px 0px 0px; text-align: center; font-size: 45px !important; font-weight: 900; border: 10px solid; margin-bottom: 0px; }
    .buy { background-color: #FFECEC !important; border-color: #E63946 !important; color: #E63946 !important; }
    .wait { background-color: #FFFBEB !important; border-color: #F59E0B !important; color: #92400E !important; }
    .sell { background-color: #ECFDF5 !important; border-color: #10B981 !important; color: #065F46 !important; }
    .price-box { background-color: #F1F5F9; border-left: 15px solid #1E3A8A; padding: 20px; border-radius: 0px 0px 15px 15px; text-align: center; margin-bottom: 30px; }
    .price-text { font-size: 38px; color: #1E3A8A; font-weight: 900; }
    .report-main-box { background: #F8FAFC; border: 3px solid #1E3A8A; padding: 25px; border-radius: 20px; margin-bottom: 30px; border-left-width: 15px; }
    .detail-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
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

# 세션 상태 초기화
if 'target' not in st.session_state: st.session_state['target'] = "005930"

st.title("👴 이수할아버지의 주식분석기 v36000")
symbol = st.text_input("📊 종목코드(6자리) 또는 티커 입력", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        # 데이터 로드 (충분한 기간 확보)
        df = fdr.DataReader(symbol).tail(150)
        if not df.empty:
            stock_name = get_stock_name(symbol)
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = float(df['close'].iloc[-1])
            
            # --- [선생님 전용 지수 계산] ---
            # 1. 볼린저 밴드 (20, 2)
            ma20 = df['close'].rolling(20).mean()
            std20 = df['close'].rolling(20).std()
            up_b = float(ma20.iloc[-1] + (std20.iloc[-1] * 2))
            lo_b = float(ma20.iloc[-1] - (std20.iloc[-1] * 2))
            
            # 2. RSI (14, 6)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_main = 100 - (100 / (1 + (gain / loss)))
            rsi_val = float(rsi_main.iloc[-1])
            rsi_sig = float(rsi_main.rolling(window=6).mean().iloc[-1])
            
            # 3. Williams %R (14, 9)
            h14 = df['high'].rolling(14).max()
            l14 = df['low'].rolling(14).min()
            wr_main = ((h14 - df['close']) / (h14 - l14)) * -100
            wr_val = float(wr_main.iloc[-1])
            wr_sig = float(wr_main.rolling(window=9).mean().iloc[-1])
            
            # 4. MACD (기본형)
            exp12 = df['close'].ewm(span=12, adjust=False).mean()
            exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_val = float((exp12 - exp26).iloc[-1])
            macd_sig = float((exp12 - exp26).ewm(span=9, adjust=False).mean().iloc[-1])

            # --- [화면 출력] ---
            st.header(f"🏢 {stock_name} ({symbol})")
            
            # 매수/매도 로직 (시그널선 교차 반영)
            is_buy = (wr_val < -80 and wr_val > wr_sig) or (rsi_val < 35 and rsi_val > rsi_sig) or (curr_p <= lo_b)
            is_sell = (wr_val > -20 and wr_val < wr_sig) or (rsi_val > 65 and rsi_val < rsi_sig) or (curr_p >= up_b)
            
            sig_class = "buy" if is_buy else "sell" if is_sell else "wait"
            sig_text = "🔴 매수 적기" if is_buy else "🟢 매도 검토" if is_sell else "🟡 관망 유지"
            st.markdown(f"<div class='signal-box {sig_class}'>{sig_text}</div>", unsafe_allow_html=True)
            
            p_val = f"${curr_p:,.2f}" if not symbol.isdigit() else f"{curr_p:,.0f}원"
            st.markdown(f"<div class='price-box'><div class='price-text'>현재가 : {p_val}</div></div>", unsafe_allow_html=True)

            # 종합 분석 리포트
            st.markdown("<div class='report-main-box'>", unsafe_allow_html=True)
            st.markdown("### 🔍 이수할아버지 종합 분석")
            trend = "상승 돌파 시도 중" if wr_val > wr_sig else "하락 압력 우세"
            psych = "심리 회복세" if rsi_val > rsi_sig else "심리 위축세"
            st.write(f"**📈 수급 추세:** {trend} (Williams %R 시그널 교차 확인)")
            st.write(f"**⚖️ 투자 심리:** {psych} (RSI 시그널 교차 확인)")
            st.write(f"**💎 최종 결론:** {sig_text} 전략이 유효합니다.")
            st.markdown("</div>", unsafe_allow_html=True)

            # 세부 지표 카드 (선생님 기준)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='detail-card'><b>볼린저 (20,2)</b><br>{lo_b:,.0f} ~ {up_b:,.0f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='detail-card'><b>RSI (14,6)</b><br>지수: {rsi_val:.1f} / 시그널: {rsi_sig:.1f}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='detail-card'><b>MACD</b><br>{'골든크로스' if macd_val > macd_sig else '데드크로스'}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='detail-card'><b>Will %R (14,9)</b><br>지수: {wr_val:.1f} / 시그널: {wr_sig:.1f}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
