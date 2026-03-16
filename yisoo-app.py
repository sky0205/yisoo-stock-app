import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 완벽 유지)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 32px !important; color: #0D47A1 !important; margin-bottom: 10px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# [상단] 글로벌 지수 상세 진단
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        s_chg = (sp500.last_price / sp500.previous_close - 1) * 100
        tnx_val = tnx.last_price
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{s_chg:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{(tnx_val - tnx.previous_close)*100:+.2f}bp")
        if n_chg < -1.0 or tnx_val > 4.5: advice = f"🚨 **[긴급: 정박하시게!]** 시장 발작 중일세. 보따리 싸서 피신해 계시게!"
        elif n_chg > 0.8: advice = f"✅ **[쾌청: 진격하시게!]** 기세가 좋구먼. 빳빳하게 기세 타고 올라갈 종목 골라보시게."
        else: advice = f"🧐 **[안개: 낚싯대만 던지시게]** 무리하게 진격하지 말고 지표 바닥권을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=400); end_date = datetime.now()
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date, end_date); currency = "원"; fmt_p = ",.0f"
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"
            name = ticker.info.get('shortName', symbol)
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            
            # 기술 지표 계산
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)})</p></div>", unsafe_allow_html=True)
            
            # 거래량 판독
            v_status = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            v_adv = "✅ 세력이 들어왔구먼! 눈을 부라리고 보시게." if v_ratio >= 100 else "🚨 거래량 없는 움직임은 가짜일세! 섣불리 진격하지 마시게."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 65: sig, col, adv = "🟢 매도권 진입", "#388E3C", "● 과열권일세! 수익 챙겨서 나오시게."
            elif p <= low_b or rsi_val <= 35: sig, col, adv = "🔴 매수권 진입", "#D32F2F", "● 바닥권일세. 분할 매수 보따리 푸시게."
            else: sig, col, adv = "🟡 관망 및 대기", "#FBC02D", "● 아직 안개 속일세. 낚싯대만 던져두시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{adv}</p></div>", unsafe_allow_html=True)

            # [핵심 수선] 볼린저 하단 돌파 시 상세 판독 복구
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                if p <= low_b:
                    bb_diag = f"● **[비상: 성벽 돌파!]** 가격이 하단 성벽({format(low_b, fmt_p)}) 아래로 밀려났구먼! 여기서 지지받고 고개를 들이밀 때가 진짜 진격의 기회일세. 함부로 칼날 잡지 마시게."
                elif p < mid_line:
                    bb_diag = f"● 현재 하단 성벽({format(low_b, fmt_p)})을 향해 내려가는 중일세. 중앙선 아래니 서두르지 말고 성벽 사수를 확인하고 낚싯대 던지시게."
                else:
                    bb_diag = f"● 현재 중앙선 위에서 기세 타는 중일세. 상단 성벽 돌파 여부를 매섭게 보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status'>{'📉 바닥권/돌파' if p <= low_b else '📉 하락세' if p < mid_line else '📈 상승세'}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>● **{'🧊 냉골' if rsi_val < 35 else '👺 불지옥' if rsi_val > 65 else '미지근'}** 상태일세. 냉정하게 보시게.</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                w_status = "🏳️ 바닥항복" if will_val < -80 else "🧨 천장광기" if will_val > -20 else "중간지대"
                w_diag = f"● 지수 {will_val:.2f}로 **개미 항복 구간**일세! 바닥 확인하고 보따리 풀 준비 하시게." if will_val < -80 else f"● 현재 안개 속일세. 바닥인지 천장인지 매섭게 보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</p><p class='ind-diag'>● 엔진이 어디로 도는지 보시게. 함부로 진격하지 마시게.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
