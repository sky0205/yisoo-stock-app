import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 모바일 최적화 스타일 (어르신 전용)
st.set_page_config(page_title="이수할아버지 v36056 모바일", layout="wide")
st.markdown("""
    <style>
    /* 배경 및 기본 폰트 설정 */
    .stApp { background-color: #F8F9FA; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; }
    
    /* 모바일 가독성을 위한 글씨 크기 대폭 강화 */
    .stock-header { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-left: 12px solid #1E88E5; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .price-text { font-size: 45px !important; color: #D32F2F !important; line-height: 1.2; }
    
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 5px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 35px !important; color: #0D47A1 !important; margin-bottom: 12px; }
    .vol-sub-text { font-size: 24px !important; color: #1565C0 !important; line-height: 1.5; background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 8px solid #1E88E5; }
    
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
    .signal-text { font-size: 70px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 6px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 35px !important; color: #D32F2F !important; border-bottom: 4px solid #FFEBEE; padding-bottom: 15px; margin-bottom: 20px; }
    .trend-item { font-size: 26px !important; line-height: 1.8; margin-bottom: 15px; color: #212121; }
    
    .ind-box { background-color: #FFFFFF; padding: 25px; border-radius: 20px; border: 3px solid #90A4AE; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 30px !important; color: #1976D2 !important; margin-bottom: 15px; border-bottom: 2px solid #EEEEEE; }
    .ind-diag { font-size: 24px !important; color: #333333 !important; line-height: 1.7; background-color: #FDFDFD; padding: 18px; border-radius: 12px; border-left: 10px solid #D32F2F; }
    
    /* 메트릭 글씨 크기 조정 */
    [data-testid="stMetricValue"] { font-size: 35px !important; }
    [data-testid="stMetricLabel"] { font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지표 (모바일 가독성 보완)
def display_global_risk():
    st.markdown("### 🌍 글로벌 실시간 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채10년", f"{tnx_val:.2f}%", f"{tnx_chg:+.2f}%")
        
        if n_chg > 0.5: advice = "✅ **[진격!]** 미장 쾌청!"
        elif n_chg < -1.0: advice = "🚨 **[정박!]** 비명 소리 포착!"
        else: advice = "🧐 **[관망]** 안개 정국일세."
        st.info(f"🧐 할배 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지 냉정 진단 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 종목번호/티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul')); currency = "원"; fmt_p = ",.0f"
            df = fdr.DataReader(symbol, start_date, end_date); stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"; name = ticker.info.get('shortName', symbol)
        
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [헤더] 시원한 주가 표시
            st.markdown(f"<div class='stock-header'><p style='font-size:30px; color:#1565C0; margin:0;'>{name}</p><p class='price-text'>{format(p, fmt_p)} {currency} <span style='font-size:25px;'>({p_chg:+.2f}%)</span></p></div>", unsafe_allow_html=True)
            
            # [거래량] 가짜상승 잡아내는 호통 로직 (유지)
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            if v_ratio >= 30 and is_opening:
                v_status = f"🔥 시초 거래폭발 ({v_ratio:.1f}%)"
                v_adv = "🔥 **[세력 진격!]** 기세가 빳빳하구먼!" if p_chg >= 3 else "💀 **[비명 포착!]** 피신하시게!" if p_chg <= -3 else "✅ 눈치싸움 중."
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                v_adv = "🚨 **[가짜 상승!]** 빈 수레일세!" if p_chg > 3 and v_ratio < 100 else "✅ 세력 추적 중."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>{v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # [신호등]
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권", "#388E3C", "👺 불지옥! 익절하시게."
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권", "#D32F2F", "🧊 바닥권! 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망", "#FBC02D", "🧐 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:28px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # [가격선]
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("⚖️ 공략선", format(low_b, fmt_p))
            with c2: st.metric("🎯 수확선", format(up_b, fmt_p))
            with c3: st.metric("🛡️ 성벽", format(defense_line, fmt_p))

            # [필살 조언 및 최종 결론] (유지 및 강화)
            adv1 = f"1. **진격 금지:** RSI {rsi_val:.1f}로 아직 60을 안 뚫었네. 섣불리 타지 마시게." if rsi_val < 60 else "1. **기세 타기:** RSI 60 돌파! 불이 붙었구먼!"
            adv2 = f"2. **성벽 사수:** 성벽({format(defense_line, fmt_p)}) {'함락!' if p < defense_line else '사수 중.'}"
            adv3 = f"3. **엔진 확인:** 엔진이 {'정회전 중!' if m_l > s_l else '**역회전 중!** 속지 마시게.'}"
            
            if p >= up_b or rsi_val >= 60: final = "💰 **[최종] 분할 매도하여 수익 챙기시게!**"
            elif p <= low_b or rsi_val <= 35: final = "🛡️ **[최종] 분할 매수로 보따리 푸시게!**"
            elif m_l < s_l or p < defense_line: final = "🧐 **[최종] 관망하며 빳빳하게 기다리시게!**"
            else: final = "📈 **[최종] 보유하며 성벽 사수 보시게!**"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:2px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:32px !important;'>{final}</div></div>""", unsafe_allow_html=True)

            # [네 기둥 지수 상세] (모바일은 세로로 배치되도록 columns 대신 개별 출력 고려 가능하나 일단 columns 유지)
            st.divider()
            i1, i2 = st.columns(2); i3, i4 = st.columns(2)
            with i1:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>● {'상단 돌파! 수확!' if p >= up_b else '하단 돌파! 기회!' if p <= low_b else '성벽 사수 보시게.'}</p></div>", unsafe_allow_html=True)
            with i2:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:45px; color:#E65100;'>{rsi_val:.1f}</p><p class='ind-diag'>● {'👺 불지옥' if rsi_val >= 60 else '🧊 냉골' if rsi_val <= 35 else '눈치싸움'} 구간.</p></div>", unsafe_allow_html=True)
            with i3:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams (항복)</p><p style='font-size:45px; color:#E65100;'>{will_val:.1f}</p><p class='ind-diag'>● {'🏳️ 개미 항복!' if will_val < -80 else '🧨 천장 광기!' if will_val > -20 else '중간지대'}</p></div>", unsafe_allow_html=True)
            with i4:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>● 엔진 {'정회전 중!' if m_l > s_l else '**역회전 중!**'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류: {e}")
