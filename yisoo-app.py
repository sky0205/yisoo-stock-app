import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 유지)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-diag { font-size: 20px !important; line-height: 1.8; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# [상단] 글로벌 지표
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        c1, c2 = st.columns(2)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("미 국채 10년물 (TNX)", f"{tnx.last_price:.3f}%", f"{(tnx.last_price - tnx.previous_close)*100:+.2f}bp")
        st.info(f"🧐 이수 할배의 글로벌 판독: {'🚨 정박하시게!' if n_chg < -0.5 else '✅ 진격!'}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        # [핵심 수선] 넉넉하게 1년 이상의 데이터를 불러와 진짜 성벽(전고점)을 찾음
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date, end_date); currency = "원"; fmt_p = ",.0f"
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"
            name = ticker.info.get('shortName', symbol)
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            # [수선] 오늘 가격을 제외한 순수 과거 1년(252영업일)간의 최고가 판독
            past_1year = df.iloc[:-1].tail(252) 
            true_high_365 = float(past_1year['Close'].max()) 
            peak_20 = float(df['Close'].iloc[-20:-1].max()); defense_line = peak_20 * 0.93

            # 기술 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # 화면 출력
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)})</p></div>", unsafe_allow_html=True)
            
            # [수선] 진짜 전고점(3,290원)을 넘었을 때만 신호등 불빛을 바꿈
            if p > true_high_365:
                sig, col, adv = "🚀 역사적 신고가", "#D32F2F", f"● 진짜 1년 최고가({format(true_high_365, fmt_p)})를 넘었구먼! 즐기되 익절가 잡으시게."
            elif p >= true_high_365 * 0.95:
                sig, col, adv = "⚔️ 성벽 돌파중", "#E65100", f"● 신고가는 무슨! 전고점({format(true_high_365, fmt_p)}) 성벽이 안 보이나? 자중하시게."
            elif p <= low_b or rsi_val <= 35:
                sig, col, adv = "🔴 매수권 진입", "#D32F2F", "● 바닥권일세. 분할 매수 보따리 푸시게."
            elif p >= up_b or rsi_val >= 65:
                sig, col, adv = "🟢 매도권 진입", "#388E3C", "● 과열권일세. 수익 챙겨서 나오시게."
            else:
                sig, col, adv = "🟡 관망 및 대기", "#FBC02D", f"● 아직 전고점({format(true_high_365, fmt_p)}) 밑일세. 낚싯대만 던져두시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{adv}</p></div>", unsafe_allow_html=True)

            # 네 기둥 지수 상세 진단 (현실 훈수 보강)
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger</p><p class='ind-status'>{'📈 상' if p > mid_line else '📉 하'}</p><p class='ind-diag'>현재 중앙선({format(mid_line, fmt_p)}) {'위' if p > mid_line else '아래'} 기세를 보시게.</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>● **{'👺 불지옥' if rsi_val > 65 else '🧊 냉골' if rsi_val < 35 else '미지근'}** 상태일세. 냉정하게 판단하시게.</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>● **{'🧨 천장광기' if will_val > -25 else '🏳️ 바닥항복' if will_val < -75 else '중간지대'}** 구간일세. 매섭게 보시게.</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</p><p class='ind-diag'>엔진이 어디로 도는지 보시게. 함부로 키 잡지 마시게.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
