import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 할배 캐릭터 스타일
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
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지표 실시간 연동
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황 (미장 실시간 분석)")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        if n_chg > 0.5 and tnx_chg < 0: advice = f"✅ **[미장 쾌청: 진격!]** 나스닥 불 뿜고 금리도 안정세일세!"
        elif n_chg < -1.0: advice = f"🚨 **[긴급 상황: 정박!]** 나스닥 급락 중이니 피신하시게."
        elif tnx_val > 4.3: advice = "⚠️ **[금리 비상: 관망]** 금리 너무 높네! 관망하시게."
        else: advice = "🧐 **[안개 정국]** 지표 끝단을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul')); currency = "원"; fmt_p = ",.0f"
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            currency = "$"; fmt_p = ",.2f"; name = ticker.info.get('shortName', symbol)
        
        if not df.empty:
            # 1. 기초 데이터 및 지표 계산
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100
            
            # RSI 및 배신(Divergence) 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val = rsi_series.iloc[-1]; rsi_prev = rsi_series.iloc[-2]
            is_divergence = p > prev_p and rsi_val < rsi_prev # 지표의 배신 포착

            # Williams %R 및 기세(Momentum) 계산
            h14_s = df['High'].rolling(14).max(); l14_s = df['Low'].rolling(14).min()
            will_series = (h14_s - df['Close']) / (h14_s - l14_s + 1e-10) * -100
            will_val = will_series.iloc[-1]; will_prev = will_series.iloc[-2]
            w_momentum = will_val - will_prev # 기세 폭발 여부

            # MACD 엔진 및 역회전폭 계산
            exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_series = exp1 - exp2; sig_series = macd_series.ewm(span=9, adjust=False).mean()
            m_l = macd_series.iloc[-1]; s_l = sig_series.iloc[-1]
            m_prev_l = macd_series.iloc[-2]; s_prev_l = sig_series.iloc[-2]
            m_diff = m_l - s_l; m_diff_prev = m_prev_l - s_prev_l

            # 볼린저 밴드 및 성벽
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # [화면 출력 시작]
            st.markdown("### 📊 현재주가현황")
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} ({p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # 거래량 판독
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            v_adv = f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_label} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 60: sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= low_b or rsi_val <= 35: sig, col = "🔴 매수권 진입", "#D32F2F"
            else: sig, col = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p></div>", unsafe_allow_html=True)

            # 네 기둥 지수 상세 분석
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "🏰 **[성문 수복]** 중앙선 위일세." if p > mid_line else "🏚️ **[성문 함락]** 중앙선 아래네."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI (배신 감지)
                d_adv = "🚨 **[배신 포착!]** 주가는 오르나 지수 하락!" if is_divergence else "✅ 정상 흐름"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{d_adv}</p></div>", unsafe_allow_html=True)
            with i3: # Williams (기세 폭발)
                m_adv = "🔥 **[기세 폭발!]**" if w_momentum > 10 else "📈 기세 유지 중"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{m_adv}</p></div>", unsafe_allow_html=True)
            with i4: # MACD (엔진 정교화)
                if m_l > s_l: m_status, m_diag = "정회전", "• 엔진 **정회전** 유지 중! 홀딩하시게."
                else: 
                    m_status = "역회전"
                    m_diag = "• 엔진 역회전 중이나 **폭이 급감**하며 채비 중!" if m_diff > m_diff_prev else "• 엔진 **역회전** 심화 중! 기다리시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 (종합 결론 상자)
            st.markdown("---")
            st.markdown(f"### ⚔️ {name} 실전 필살 대응 전략")
            if is_divergence:
                st.warning("🚨 **[비상! 지표의 배신]** 주가는 오르나 지표 온도가 식었네. '불 트랩' 가능성 농후하니 보따리 챙겨두시게!")
            elif w_momentum > 10:
                st.info("🔥 **[진격! 기세 폭발]** 윌리엄 시그널 뚫고 천정 돌진 중! 엔진 사수하며 수익 극대화하시게.")
            else:
                if p > mid_line:
                    st.success(f"📈 **[안정적 진격]** 현재 성벽 사수 중이며 엔진은 {m_status} 상태일세. 냉정하게 지켜보시게.")
                else:
                    st.error(f"📉 **[성문 함락]** 성벽 밑으로 가라앉았고 엔진은 {m_status}네. 칼 거두고 자숙하시게.")

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
