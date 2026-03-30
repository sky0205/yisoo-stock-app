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

# 글로벌 리스크 표시 (그대로 유지)
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
    except: st.error("⚠️ 데이터 호출 불가")

display_global_risk(); st.divider()
symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul'))
            ticker = yf.Ticker(f"{symbol}.KS")
            df = ticker.history(start=start_date, end=end_date)
            try:
                df_krx = fdr.StockListing('KRX')
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = ticker.info.get('shortName', symbol).split(',')[0]
            currency, fmt_p = "원", ",.0f"
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern'))
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol)
            currency, fmt_p = "$", ",.2f"

        if not df.empty:
            df = df.ffill().dropna()
            p = float(ticker.fast_info.last_price) if hasattr(ticker, 'fast_info') else float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            p_diff, p_chg = p - prev_p, (p - prev_p) / prev_p * 100

            # 1. 거래량 및 거래강도 점수 정밀 계산
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 else 0
            
            s_h, s_m = (9, 0) if is_kr else (9, 30)
            elapsed = (now_local.hour - s_h) * 60 + (now_local.minute - s_m)
            
            # 장 시작 전이거나 주말이면 390분(풀 타임) 적용
            if elapsed <= 0 or now_local.weekday() >= 5: elapsed = 390
            elif elapsed > 390: elapsed = 390
            
            # 거래강도 = (현재 거래량비율) / (시간 경과 비율) -> 100점 기준
            vol_strength = v_ratio / (elapsed / 390)

            # 2. 기술 지표 계산 (20/2, 14/6, 14/9 기준)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]
            
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
            
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
            sig_line = macd.ewm(span=9).mean()
            m_l, s_l, m_p, s_p = macd.iloc[-1], sig_line.iloc[-1], macd.iloc[-2], sig_line.iloc[-2]
            
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            peak_20 = float(df['High'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # 현재주가현황 출력
            st.markdown(f"### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                    <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p>
                </div>
            """, unsafe_allow_html=True)

            # 거래량 전황
            is_opening = 9 <= now_local.hour <= 11
            v_status = f"📈 시초 거래급등" if is_opening and v_ratio > 50 else (f"🔥 거래폭발" if v_ratio > 200 else "📈 거래증가")
            v_adv = f"✅ 거래량 {v_ratio:.1f}%로 터졌으나 힘겨루기 중일세."
            if p_chg > 3 and v_ratio > 150: v_adv = f"🔥 **[진짜 상승!]** 거래량 실린 빳빳한 진격일세!"
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 필살 대응 전략 (최종 결론 거래강도 포함)
            if p >= up_b or rsi_val >= 60: final_adv = f"💰 **[최종 결론]** 거래강도({vol_strength:.0f}점). 탐욕의 끝자락일세. **분할 매도**하여 수익을 챙기시게!"
            elif m_l < s_l or p < defense_line:
                tag = "🚨" if vol_strength > 150 else "🧐"
                final_adv = f"{tag} **[최종 결론]** 거래강도({vol_strength:.0f}점). 엔진 역회전 혹은 성벽 위태롭네. **관망하며 소나기를 피하시게!**"
            else: final_adv = f"📈 **[최종 결론]** 거래강도({vol_strength:.0f}점). 추세 살아있구먼. 성벽 사수하며 **보유(홀딩)**하시게!"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>1. **성벽 사수 확인:** 현재 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세.</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # 4대 지수 정밀 진단 (생략 없이 복구)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "⚠️ **[과열 진입]** 성벽 사수 중이나 온도가 높네. 수익을 확정 지으시게." if p >= up_b or rsi_val >= 60 else ("🏰 **[성벽 사수]** 안정적 진격 중일세." if p > mid_line else "🏚️ **[성문 함락]** 성벽 밑일세. 절대 칼 뽑지 마시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                is_div = p > prev_p and rsi_val < rsi_prev
                r_diag = f"● 지수 {rsi_val:.2f}로 **{'👺 불지옥' if rsi_val >= 60 else '🧊 냉골' if rsi_val <= 35 else '중립'}**일세. {'🚨 주가는 오르나 온도가 식는 배신 포착!' if is_div else '지표 끝단을 기다리시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                w_diag = f"● 지수 {will_val:.2f}로 **{'🧨 천장 광기' if will_val >= -20 else '📉 하락 가속' if will_val <= -65 else '중간 지대'}**일세. {'비수 꽂히기 전에 익절하시게.' if will_val >= -20 else '바닥 확인 전까지 자숙하시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diff, m_diff_prev = m_l - s_l, m_p - s_p
                m_diag = "● 엔진 **정회전**!" if m_l > s_l else ("● 엔진 **역회전폭 급감**! 시동 걸 채비 하시게." if m_diff > m_diff_prev else "● 엔진 **역회전 심화**! 냉정하게 자숙하시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
