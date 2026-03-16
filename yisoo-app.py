import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 할배 캐릭터 스타일 (빈 박스 전면 제거)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    /* [박스 수선] 제목은 글씨로만, 수치는 빳빳한 박스로! */
    .title-text {
        font-size: 38px !important;
        color: #1565C0 !important;
        margin: 25px 0 10px 0;
        display: block;
        border-left: 12px solid #1565C0;
        padding-left: 18px;
    }
    
    /* 진짜 내용이 담긴 몸통 박스 */
    .real-content-box {
        background-color: #FFFFFF;
        border-radius: 15px;
        border: 3.5px solid #CFD8DC;
        padding: 28px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        margin-bottom: 35px;
    }
    
    .stock-header { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border-left: 15px solid #1E88E5; margin-bottom: 25px; }
    .price-main { font-size: 58px !important; color: #D32F2F !important; line-height: 1.1; }
    
    /* 거래량 상세 훈수 */
    .vol-main-text { font-size: 42px !important; color: #0D47A1 !important; margin-bottom: 12px; }
    .vol-sub-text { font-size: 30px !important; color: #1565C0 !important; line-height: 1.7; background-color: #F5F5F5; padding: 20px; border-radius: 10px; border-left: 12px solid #1E88E5; }
    
    /* 지수 상세 박스 (내용 복구) */
    .ind-box { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 4px solid #90A4AE; min-height: 550px; margin-bottom: 25px; }
    .ind-title { font-size: 38px !important; color: #1976D2 !important; border-bottom: 4.5px solid #EEEEEE; padding-bottom: 15px; margin-bottom: 20px; }
    .ind-diag { font-size: 30px !important; color: #333333 !important; line-height: 1.8; background-color: #FAFAFA; padding: 22px; border-radius: 12px; border-left: 15px solid #D32F2F; }
    
    /* 대왕 글씨 metric 수치 */
    [data-testid="stMetricValue"] { font-size: 65px !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { font-size: 32px !important; color: #546E7A !important; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 전황: 빈 박스 걷어내고 제목과 수치 박스만 남김
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        
        st.markdown("<span class='title-text'>🌍 글로벌 시장 종합 전황</span>", unsafe_allow_html=True)
        # 꼴 보기 싫은 빈 박스 공간은 없애고 바로 알맹이 박스 시작
        st.markdown("<div class='real-content-box'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년", f"{tnx.last_price:.2f}%", f"{(tnx.last_price/tnx.previous_close-1)*100:+.2f}%")
        advice = "✅ **[진격!]** 미장 쾌청!" if n_chg > 0.5 else "🚨 **[정박!]** 피신하시게!" if n_chg < -1.0 else "🧐 **[관망]** 안개 정국일세."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
        st.markdown("</div>", unsafe_allow_html=True)
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "Nvda")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul')); df = fdr.DataReader(symbol, start_date, end_date); stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]; currency = "원"; fmt_p = ",.0f"
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); name = ticker.info.get('shortName', symbol); currency = "$"; fmt_p = ",.2f"
        
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            st.markdown(f"<div class='stock-header'><p style='font-size:38px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p class='price-main'>{format(p, fmt_p)} {currency} <span style='font-size:40px;'>({p_chg:+.2f}%)</span></p></div>", unsafe_allow_html=True)
            
            # 거래량 분석: 빈 박스 없이 제목과 알맹이만!
            st.markdown("<span class='title-text'>📊 실시간 거래량 전황 분석</span>", unsafe_allow_html=True)
            st.markdown("<div class='real-content-box'>", unsafe_allow_html=True)
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가"
            if v_ratio >= 30 and is_opening:
                v_status = f"🔥 시초 거래폭발 ({v_ratio:.1f}%)"
                v_adv = f"🔥 **[세력 진격!]** 거래량이 빳빳하게 터지며 폭등 중일세! 기세 타시게!" if p_chg >= 3 else f"💀 **[비명 포착!]** 거래량이 터지며 폭락 중이니 일단 피신하시게!"
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                v_adv = f"🚨 **[가짜 상승 주의!]** 주가는 올랐는데 거래량은 빈 수레일세! 개미 꼬드기는 격이니 속지 마시게." if p_chg > 3 and v_ratio < 100 else f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-main-text'>{v_status}</div><div class='vol-sub-text'>{v_adv}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 신호등 및 전략 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); up_b = df['MA20'].iloc[-1] + (df['Std'].iloc[-1] * 2); low_b = df['MA20'].iloc[-1] - (df['Std'].iloc[-1] * 2)

            if p >= up_b or rsi_val >= 60: sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= low_b or rsi_val <= 35: sig, col = "🔴 매수권 진입", "#D32F2F"
            else: sig, col = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div style='background-color:{col}; padding:45px; border-radius:20px; text-align:center; margin-bottom:30px;'><p style='font-size:90px; font-weight:900; color:white; margin:0;'>{sig}</p></div>", unsafe_allow_html=True)

            # 성벽 가격선: 빈 박스 없이 깔끔하게!
            st.markdown("<span class='title-text'>🛡️ 매수·매도 핵심 성벽 가격선</span>", unsafe_allow_html=True)
            st.markdown("<div class='real-content-box'>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("⚖️ 공략 대기선", format(low_b, fmt_p))
            with c2: st.metric("🎯 수확 목표선", format(up_b, fmt_p))
            with c3: st.metric("🛡️ 성벽(방어선)", format(defense_line, fmt_p))
            st.markdown("</div>", unsafe_allow_html=True)

            # 4대 지수 상세 분석: 박스 안에 빳빳하게 복구
            st.divider()
            i1, i2 = st.columns(2); i3, i4 = st.columns(2)
            with i1: # Bollinger
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>● **[비상: 상단 돌파!]** 하늘 찌르네! 익절 준비 하시게.</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                r_diag = f"● 지수 {rsi_val:.1f}로 **👺 불지옥** 문턱일세! 익절가 잡으시게." if rsi_val >= 60 else f"● 지수 {rsi_val:.1f}로 **🧊 냉골** 상태일세! 바닥을 보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:75px; color:#E65100;'>{rsi_val:.1f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
                w_diag = f"● 지수 {will_val:.1f}로 **🏳️ 개미 항복** 구간! 보따리 푸시게." if will_val < -80 else f"● 지수 {will_val:.1f}로 **🧨 천장 광기** 구간!"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:75px; color:#E65100;'>{will_val:.1f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
                m_diag = "● 엔진이 정회전 중!" if m_l > s_l else f"● 엔진이 **역회전** 중이네! 속지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
