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
    
    /* 제목 및 박스 스타일 */
    .title-text { font-size: 32px !important; color: #1565C0 !important; margin: 15px 0 10px 0; display: block; border-left: 8px solid #1565C0; padding-left: 12px; }
    .info-card { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 3px solid #CFD8DC; margin-bottom: 25px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    
    [data-testid="stMetricValue"] { font-size: 55px !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지수 표시
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        st.markdown("<span class='title-text'>🌍 글로벌 시장 종합 전황</span>", unsafe_allow_html=True)
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년", f"{tnx.last_price:.2f}%", f"{(tnx.last_price/tnx.previous_close-1)*100:+.2f}%")
        st.info(f"🧐 이수 할배의 글로벌 판독: {'✅ **[진격!]** 미장 쾌청!' if n_chg > 0.5 else '🚨 **[정박!]** 피신하시게.' if n_chg < -1.0 else '🧐 **[관망]** 안개 정국일세.'}")
        st.markdown("</div>", unsafe_allow_html=True)
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("👴 이수할아버지의 냉정 진단기 v36056")
display_global_risk()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]; currency = "원"; fmt = ",.0f" 
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # [수정] "현재 주가" 제목 추가 및 기존 스타일 유지
            st.markdown(f"""
                <div class='stock-header'>
                    <p style='font-size:32px; color:#1565C0; margin-bottom:5px;'>📈 현재 주가 진황</p>
                    <p style='font-size:35px; color:#455A64; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency} (전일비: {p-prev_p:+.0f})</p>
                </div>""", unsafe_allow_html=True)
            
            # 거래량 및 지표 로직은 어르신 원본 100% 그대로입니다.
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; color:#0D47A1;'>📊 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:20px; color:#1565C0;'>✅ 세력의 발자국을 추적 중일세.</div></div>", unsafe_allow_html=True)

            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); up_b = df['MA20'].iloc[-1] + (df['Std'].iloc[-1] * 2); low_b = df['MA20'].iloc[-1] - (df['Std'].iloc[-1] * 2)

            if p >= up_b or rsi_val >= 65: sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= low_b or rsi_val <= 35: sig, col = "🔴 매수권 진입", "#D32F2F"
            else: sig, col = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {col};'><span style='font-size:65px; color:white;'>{sig}</span></div>", unsafe_allow_html=True)

            # 성벽 가격선
            st.markdown("<span class='title-text'>🛡️ 매수·매도 핵심 성벽 가격선</span>", unsafe_allow_html=True)
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("⚖️ 공략 대기선", format(low_b, fmt))
            c2.metric("🎯 수확 목표선", format(up_b, fmt))
            c3.metric("🛡️ 성벽 (방어선)", format(defense_line, fmt))
            st.markdown("</div>", unsafe_allow_html=True)

            # 4대 지수 상세 훈수 (원본 100% 복구)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Bollinger (기세)</p><p class='ind-diag'>● **[상단 돌파!]** 하늘 찌르네! 익절 준비 하시게.</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.1f}</p><p class='ind-diag'>● 지수 {rsi_val:.1f}로 **👺 불지옥** 문턱일세! 익절가 잡으시게.</p></div>", unsafe_allow_html=True)
            with i3:
                h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.1f}</p><p class='ind-diag'>● 지수 {will_val:.1f}로 **🏳️ 개미 항복** 구간! 보따리 푸시게.</p></div>", unsafe_allow_html=True)
            with i4:
                m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>MACD (엔진)</p><p class='ind-diag'>● {'엔진 정회전! 기세 좋구먼.' if m_l > s_l else '엔진 **역회전** 중! 절대 속지 마시게.'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
