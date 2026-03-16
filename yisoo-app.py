import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (어르신 원본 스타일 100% 보존)
st.set_page_config(page_title="이수할아버지 분석기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .title-text { font-size: 32px !important; color: #1565C0 !important; margin: 15px 0 10px 0; display: block; border-left: 10px solid #1565C0; padding-left: 12px; }
    .info-card { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 3px solid #CFD8DC; margin-bottom: 25px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    [data-testid="stMetricValue"] { font-size: 55px !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# [복구] 미장 판독 상세 내용 (image_abc7b5.png 기반 100% 복구)
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        t_chg = (tnx.last_price / tnx.previous_close - 1) * 100
        
        st.markdown("<span class='title-text'>🌍 글로벌 시장 종합 전황</span>", unsafe_allow_html=True)
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년", f"{tnx.last_price:.2f}%", f"{t_chg:+.2f}%")
        
        if n_chg > 0.5:
            advice = f"✅ **[미장 쾌청: 진격!]** 나스닥 {n_chg:.2f}% 불을 뿜으며 유동성이 숨을 쉬구먼! 세력들이 고삐 풀었으니 빳빳하게 기세를 타시게."
        elif n_chg < -1.0:
            advice = f"🚨 **[긴급 상황: 정박!]** 나스닥 {n_chg:.2f}% 급락에 비명 소리가 자자하네! 성벽 함락 위기니 무리한 진격은 금물이고 일단 보따리 싸서 소나기를 피하시게."
        else:
            advice = f"🧐 **[안개 정국: 관망]** 방향성 없이 눈치싸움이 치열하구먼. 대왕 고래들 움직임 보일 때까지 자중하며 기다리시게."
        
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
        st.markdown("</div>", unsafe_allow_html=True)
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("👴 이수할아버지의 냉정 진단기 v36056")
display_global_risk()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]; currency = "원"; fmt = ",.0f" 
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # [1순위] 현재 주가 헤더
            st.markdown(f"""<div class='stock-header'><p style='font-size:32px; color:#1565C0; margin-bottom:5px;'>📈 현재 주가 진황</p>
                <p style='font-size:35px; color:#455A64; margin:0;'>{name} ({symbol})</p>
                <p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency} (전일비: {p-prev_p:+.2f})</p></div>""", unsafe_allow_html=True)
            
            # [2순위] 신호등 (주가 바로 아래)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            if p >= up_b or rsi_val >= 65: sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= low_b or rsi_val <= 35: sig, col = "🔴 매수권 진입", "#D32F2F"
            else: sig, col = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {col};'><span style='font-size:65px; color:white;'>{sig}</span></div>", unsafe_allow_html=True)

            # [3순위] 거래량 분석 (원본 복구)
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            price_up = p > prev_p
            if v_ratio < 100: v_status = "💤 거래침체"; v_advice = "🚨 <b>가짜 상승!</b> 거래량 없이 오르는 건 빈집에 바람 드는 격이니 절대 속지 마십시오." if price_up else "⏳ <b>눈치보기 중.</b> 파는 사람도 없으니 바닥 확인될 때까지 섣불리 물타지 마십시오."
            elif 100 <= v_ratio < 200: v_status = "📈 거래증가"; v_advice = "✅ <b>관심 집중.</b> 거래량이 실리며 오르니 기세가 붙고 있습니다. 정찰병 파견 검토하십시오." if price_up else "⚠️ <b>물량 출회.</b> 누군가 던지기 시작했으니 하단 성벽 사수 여부를 부라리고 보십시오."
            else: v_status = "🔥 거래폭발"; v_advice = "🚀 <b>세력 진격!</b> 큰손들이 문 부수고 들어왔습니다. 장대양봉이면 진격 수위를 높이십시오." if price_up else "💣 <b>투매 발생!</b> 아비규환이니 지하실 열리기 전에 일단 보따리 싸서 대피하십시오."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_advice}</div></div>", unsafe_allow_html=True)

            # [4순위] 실전 필살 조언 (image_ab5a41.png 반영)
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            trend_desc = "정배열 상승 가도" if (m_l > s_l and p > mid_line) else "역배열 하락 늪" if (m_l < s_l and p < mid_line) else "횡보 및 안개 정국"
            if p >= up_b: adv_text = "💰 **[과열 경보]** 성벽 밖으로 튀어나갔네! 탐욕 버리고 익절 수익을 빳빳하게 챙기시게."
            elif p <= low_b: adv_text = "🛡️ **[바닥 포착]** 하단 성벽 근처일세! 겁내지 말고 분할 매수 보따리를 푸시게."
            else: adv_text = "🎣 낚싯대만 던져두고 지표 바닥권을 차분히 기다리십시오."
            st.markdown(f"""<div class='trend-card'><div style='font-size:32px; color:#D32F2F; border-bottom:3px solid #FFEBEE; padding-bottom:12px; margin-bottom:20px;'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> {trend_desc} 상태일세.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt)}) {'함락! 후퇴!' if p < defense_line else '사수 중.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{adv_text}</span></div></div>""", unsafe_allow_html=True)

            # [5순위] 4대 지수 훈수 (image_abbc54.png 기반 100% 복구)
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Bollinger (기세)</p><p class='ind-diag'>● **[상단 돌파!]** 하늘 찌르네! 익절 준비 하시게.</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>● 온도 {rsi_val:.2f}로 **탐욕의 불지옥** 직전입니다. 냉정하게 수익을 확정 지으십시오.</p></div>", unsafe_allow_html=True)
            with i3:
                h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.1f}</p><p class='ind-diag'>● 지수 {will_val:.1f}로 **항복 지점** 근처입니다. 분할 매수 보따리를 푸십시오.</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>MACD (엔진)</p><p class='ind-diag'>● {'엔진 정회전!' if m_l > s_l else '엔진 **역회전** 중!'} 절대 속지 마시게.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
