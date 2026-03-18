import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 스타일 (자네 틀 그대로일세)
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
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 320px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지표 (그대로 유지)
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥", f"{nasdaq.last_price:,.2f}")
        c2.metric("S&P 500", f"{sp500.last_price:,.2f}")
        c3.metric("미 국채 10년물", f"{tnx.last_price:.3f}%")
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
            df = fdr.DataReader(symbol, start_date, end_date); stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"; name = ticker.info.get('shortName', symbol)

        if not df.empty:
            # [기초 데이터 준비]
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100 if df['Volume'].iloc[-6:-1].mean() > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # [지표 계산]
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val = rsi_series.iloc[-1]; rsi_prev = rsi_series.iloc[-2]
            
            h14_s = df['High'].rolling(14).max(); l14_s = df['Low'].rolling(14).min()
            will_series = (h14_s - df['Close']) / (h14_s - l14_s + 1e-10) * -100
            will_val = will_series.iloc[-1]; will_prev = will_series.iloc[-2]

            exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_series = exp1 - exp2; sig_series = macd_series.ewm(span=9, adjust=False).mean()
            m_l = macd_series.iloc[-1]; s_l = sig_series.iloc[-1]; m_prev_l = macd_series.iloc[-2]; s_prev_l = sig_series.iloc[-2]

            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [핵심 로직]
            is_divergence = p > prev_p and rsi_val < rsi_prev
            w_momentum = (will_val - will_prev)
            m_status = "정회전" if m_l > s_l else "역회전"
            m_diff = m_l - s_l; m_diff_prev = m_prev_l - s_prev_l

            # [상단 출력]
            st.markdown(f"<div class='stock-header'><p style='font-size:35px;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F;'>{format(p, fmt_p)} {currency} ({p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # [매수매도 성벽] (자네 틀 그대로 복구했네!)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # [필승 대응 전략] --- 여기서 상자를 열고 ---
            st.markdown(f"<div class='trend-card'><div class='trend-title'>⚔️ {name} v36056 필승 대응 전략</div>", unsafe_allow_html=True)
            
            if is_divergence:
                st.warning(f"🚨 **[진격 중단: 지표의 배신]** 주가 오르나 온도가 식었네! 성벽({defense_line:,.0f}) 사수보다 익절이 우선일세.")
            elif w_momentum > 10:
                st.info(f"🔥 **[진격 개시: 기세 폭발]** 윌리엄이 성문을 부쐈으니 노도와 같은 기세로 진격하시게! 필승전략: 수익 극대화!")
            else:
                if p > mid_line: st.success(f"📈 **[성벽 사수]** 중앙선 위일세. 엔진은 {m_status} 상태니 냉정하게 관망하시게.")
                else: st.error(f"📉 **[성문 함락]** 성벽 밑일세. 엔진 {m_status}이니 절대 칼 뽑지 마시게.")

            # --- 여기서 상자를 닫아야 모든 내용이 안으로 들어오네! ---
            st.markdown("</div>", unsafe_allow_html=True)

            # [네 기둥 지수 상세 분석]
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger</p><p>{'🏰 성벽 사수 중일세.' if p > mid_line else '🏚️ 성벽 함락되었네.'}</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p>{rsi_val:.2f}<br>{'🚨 배신 포착!' if is_divergence else '정상 온도일세.'}</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams</p><p>{will_val:.2f}<br>{'🔥 기세 폭발!' if w_momentum > 10 else '기세 유지 중.'}</p></div>", unsafe_allow_html=True)
            with i4:
                m_diag = "● 엔진 **정회전**!" if m_l > s_l else ("● 엔진 **역회전폭 급감**! 채비 중." if m_diff > m_diff_prev else "● 엔진 역회전 심화 중.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
