import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 할배 캐릭터 스타일 (완벽 유지)
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

# 글로벌 지표 실시간 연동 (그대로 유지)
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황 (미장 정밀 분석)")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")

        if tnx_val >= 4.5: advice = "🚨 **[금리 발작: 비상]** 국채 금리가 4.5%를 넘어섰네! 기술주 성벽 무너질 수 있으니 진격을 멈추시게."
        elif n_chg > 0.5 and tnx_chg < 0: advice = "🔥 **[골디락스 진입]** 지수는 오르고 금리는 내리니, 이건 하늘이 준 진격의 기회일세! 기세 타시게."
        elif n_chg < -1.0: advice = "💀 **[패닉 셀 감지]** 나스닥 비명 지르며 투매 중이네. 성문 닫고 소나기 피하는 게 상책일세."
        elif tnx_val > 4.2: advice = "⚠️ **[금리 압박: 주의]** 금리가 빳빳하게 고개 드니 시장 맷집 시험할 걸세. 무리한 진격은 금물이네."
        else: advice = "🧐 **[눈치싸움 중]** 세력들이 다음 재료 기다리며 간 보고 있구먼. 섣부른 판단은 독이네."
        st.info(f"🧐 이수 할배의 글로벌 정밀 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul'))
            currency, fmt_p = "원", ",.0f"
            ticker_symbol = f"{symbol}.KS"
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(start=start_date, end=end_date)
            try:
                df_krx = fdr.StockListing('KRX')
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = ticker.info.get('shortName', symbol).split(',')[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern'))
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol)
            currency, fmt_p = "$", ",.2f"
        
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
            df = df.ffill().dropna()
            
            # [수정] 현주가 실시간 사수
            try: p = float(ticker.fast_info.last_price)
            except: p = float(df['Close'].iloc[-1])
            
            prev_p = float(df['Close'].iloc[-2])
            if is_kr and p == prev_p and len(df) > 2: prev_p = float(df['Close'].iloc[-3])
            
            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100
            peak_20 = float(df['High'].iloc[-21:-1].max())
            defense_line = peak_20 * 0.93

            # 기술 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
            signal = macd.ewm(span=9).mean()
            m_l, s_l, m_p, s_p = macd.iloc[-1], signal.iloc[-1], macd.iloc[-2], signal.iloc[-2]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # 전광판 출력
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                    <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p>
                </div>
            """, unsafe_allow_html=True)

            # [핵심 수정] 시간 가중치 및 거래강도 점수
            s_h, s_m = (9, 0) if is_kr else (9, 30)
            elapsed = (now_local.hour - s_h) * 60 + (now_local.minute - s_m)
            if now_local.weekday() >= 5 or elapsed > 390: elapsed = 390
            elif elapsed < 10: elapsed = 10 # 분모가 0이 되어 점수가 튀는 것 방지
            
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 else 0
            vol_strength = v_ratio / (elapsed / 390)

            # 거래량 판독
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            if v_ratio >= 30 and is_opening:
                v_status = f"📈 시초 거래급등 ({v_ratio:.1f}%)"
                v_adv = f"✅ 거래량 {v_ratio:.1f}%로 터졌으나 주가가 힘겨루기 중일세. 방향 정해질 때까지 눈을 부라리고 보시게."
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                v_adv = f"🔥 **[진짜 상승!]** 거래량 {v_ratio:.1f}% 실린 빳빳한 진격일세!" if p_chg > 3 and v_ratio > 150 else f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"● {'👺 불지옥 문턱일세!' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= (low_b * 1.005) or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 겁먹지 말고 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 및 [최종 결론]
            adv1 = f"1. **진격 금지:** RSI가 {rsi_val:.2f}로 아직 60 아래일세." if rsi_val < 60 else "1. **기세 타기:** RSI가 60을 돌파하며 불이 붙었구먼!"
            adv2 = f"2. **성벽 사수 확인:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세."
            adv3 = f"3. **엔진 확인:** 엔진이 {'역회전' if m_l < s_l else '정회전'} 중이라네!"
            
            if p >= up_b or rsi_val >= 60: final_adv = f"💰 **[최종 결론]** 거래강도({vol_strength:.0f}점). 탐욕의 끝자락일세. **분할 매도**하여 수익을 챙기시게!"
            elif m_l < s_l or p < defense_line:
                tag = "🚨" if vol_strength > 150 else "🧐"
                final_adv = f"{tag} **[최종 결론]** 거래강도({vol_strength:.0f}점). 엔진 역회전 혹은 성벽 위태롭네. **관망하며 소나기를 피하시게!**"
            else: final_adv = f"📈 **[최종 결론]** 거래강도({vol_strength:.0f}점). 추세 살아있구먼. 성벽 사수 확인하며 **보유(홀딩)**하시게!"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # 4대 지수 상세 분석 (원형 복구)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "⚠️ **[과열 진입]** 성벽 사수 중이나 온도가 높네. 익절을 권하네." if p >= up_b or rsi_val >= 60 else (" castles **[성벽 사수]** 안정적 진격 중일세." if p > mid_line else "🏚️ **[성문 함락]** 성벽 밑일세. 절대 칼 뽑지 마시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                is_div = p > prev_p and rsi_val < rsi_prev
                r_diag = f"● 지수 {rsi_val:.2f}로 **{'👺 불지옥' if rsi_val >= 60 else '🧊 냉골' if rsi_val <= 35 else '중립'}**일세. {'🚨 가짜 상승 주의(배신 포착)!' if is_div else '지표 끝단을 기다리시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                w_diag = f"● 지수 {will_val:.2f}로 **{'🧨 천장 광기' if will_val >= -20 else '📉 하락 가속' if will_val <= -65 else '중간 지대'}**일세. {'비수 꽂히기 전에 수확하시게.' if will_val >= -20 else '바닥 확인 전까지 자숙하시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diff, m_diff_prev = m_l - s_l, m_p - s_p
                m_diag = "● 엔진 **정회전**!" if m_l > s_l else ("● 엔진 **역회전폭 급감**! 시동 채비 하시게." if m_diff > m_diff_prev else "● 엔진 **역회전 심화**! 절대 타지 마시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
