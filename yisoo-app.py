import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (어르신 원본 스타일 100% 유지)
st.set_page_config(page_title="이수할아버지 분석기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .title-text { font-size: 32px !important; color: #1565C0 !important; margin: 15px 0 10px 0; display: block; border-left: 10px solid #1565C0; padding-left: 15px; }
    .info-card-box { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 3px solid #CFD8DC; margin-bottom: 25px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 42px !important; color: #0D47A1 !important; margin-bottom: 12px; }
    .vol-sub-text { font-size: 26px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .advice-highlight { color: #D32F2F !important; font-size: 26px !important; text-decoration: underline; }
    
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    [data-testid="stMetricValue"] { font-size: 55px !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 판독
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        st.markdown("<span class='title-text'>🌍 글로벌 시장 종합 전황</span>", unsafe_allow_html=True)
        st.markdown("<div class='info-card-box'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년", f"{tnx.last_price:.2f}%", f"{(tnx.last_price/tnx.previous_close-1)*100:+.2f}%")
        advice = f"✅ **[미장 쾌청: 진격!]** 나스닥 {n_chg:.2f}% 불을 뿜으며 유동성이 숨을 쉬구먼! 세력들이 고삐 풀었으니 빳빳하게 기세를 타시게." if n_chg > 0.5 else "🧐 **[안개 정국: 관망]** 지표 끝단을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
        st.markdown("</div>", unsafe_allow_html=True)
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("👴 이수할아버지의 냉정 진단기 v36056")
display_global_risk()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "NVDA")

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
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); diff = p - prev_p
            chg_rate = (diff / prev_p) * 100  # [복구] 상승률 계산
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # [수정] 전일비 금액(콤마/소수점 제거) + 상승률(%) 추가
            diff_str = f"{format(diff, ',.0f')}" if is_kr else f"{format(diff, '+.2f')}"
            st.markdown(f"""<div class='stock-header'><p style='font-size:32px; color:#1565C0; margin-bottom:5px;'>📈 현재 주가 진황</p>
                <p style='font-size:35px; color:#455A64; margin:0;'>{name} ({symbol})</p>
                <p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency} (전일비: {diff_str} / {chg_rate:+.2f}%)</p></div>""", unsafe_allow_html=True)
            
            # 지수 계산 및 신호등
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            if p >= up_b or rsi_val >= 65: sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= low_b or rsi_val <= 35: sig, col = "🔴 매수권 진입", "#D32F2F"
            else: sig, col = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {col};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # 거래량 및 성벽 (원본 유지)
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            v_adv = "🚨 <b>가짜 상승!</b> 빈집에 바람 드는 격이니 절대 속지 마십시오." if p > prev_p and v_ratio < 100 else "✅ 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_ratio:.1f} %</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            st.markdown("<span class='title-text'>🛡️ 매수·매도 핵심 성벽 가격선</span>", unsafe_allow_html=True)
            st.markdown("<div class='info-card-box'>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 지수 설명 (원본 복구)
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Bollinger (기세)</p><p class='ind-diag'>● **[상단 돌파!]** 하늘 찌르네! 익절 준비 하시게. 평균 회귀 본능에 의해 조만간 소나기가 올 수 있으니 보따리 싸시게.</p></div>", unsafe_allow_html=True)
            with i2:
                r_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                r_diag = f"● 온도 {rsi_val:.2f}로 **탐욕의 불지옥** 직전입니다. 분할 매도로 수익을 확정 지으십시오." if r_stat=="👺 불지옥" else f"● 온도 {rsi_val:.2f}의 **냉골 상태**입니다. 지수가 식을 때까지 기다리십시오." if r_stat=="🧊 냉골" else "● 매수와 매도가 팽팽한 줄다리기 중일세."
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3:
                h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
                w_diag = f"● **불나방 광기(-20↑)** 직전! 후퇴를 준비하십시오." if will_val > -35 else f"● **항복 지점(-75↓)** 근처! 분할 매수 보따리를 푸십시오." if will_val < -65 else "● 안개 속이니 째려만 보시게."
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>MACD (엔진)</p><p class='ind-diag'>● {'엔진 정회전! 기세 좋구먼.' if m_l > s_l else '엔진 **역회전** 중! 절대 속지 마시게.'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
