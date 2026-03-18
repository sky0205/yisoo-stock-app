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
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황 (미장 실시간 분석)")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        if n_chg > 0.5 and tnx_chg < 0: advice = f"✅ **[미장 쾌청: 진격!]** 나스닥 불 뿜고 금리도 안정세일세! 기세 타고 진격하시게."
        elif n_chg < -1.0: advice = f"🚨 **[긴급 상황: 정박!]** 나스닥 급락 중이니 성벽 무너지기 전에 보따리 싸서 피신하시게."
        elif tnx_val > 4.3: advice = "⚠️ **[금리 비상: 관망]** 국채 금리 너무 높네! 성벽 위태로우니 무리한 진격은 금물일세."
        else: advice = "🧐 **[안개 정국: 관망]** 지표 끝단을 기다리시게."
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
            df = fdr.DataReader(symbol, start_date, end_date); stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"; name = ticker.info.get('shortName', symbol)
        
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
            # [재료 준비] 어제와 오늘 데이터를 빳빳하게 대조하시게
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # 기술 지표 계산 (배신 및 기세 논리 탑재)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val = rsi_series.iloc[-1]; rsi_prev = rsi_series.iloc[-2]
            
            h14_s = df['High'].rolling(14).max(); l14_s = df['Low'].rolling(14).min()
            will_series = (h14_s - df['Close']) / (h14_s - l14_s + 1e-10) * -100
            will_val = will_series.iloc[-1]; will_prev = will_series.iloc[-2]

            exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_series = exp1 - exp2; sig_series = macd_series.ewm(span=9, adjust=False).mean()
            m_l = macd_series.iloc[-1]; s_l = sig_series.iloc[-1]
            m_prev_l = macd_series.iloc[-2]; s_prev_l = sig_series.iloc[-2]

            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [출력] 현재주가현황
            st.markdown("### 📊 현재주가현황")
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)} / {p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # 거래량 상세 판독 (원본 유지)
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            if v_ratio >= 30 and is_opening:
                if p_chg >= 3: v_status, v_adv = f"🔥 현지 시초 주가 폭등 / 거래폭발 ({v_ratio:.1f}%)", f"🔥 **[세력 진격!]** 거래폭발 중일세! 빳빳하게 기세 타시게!"
                elif p_chg <= -3: v_status, v_adv = f"💀 현지 시초 주가 폭락 / 거래폭발 ({v_ratio:.1f}%)", f"💀 **[비명 포착!]** 성벽 함락 중이니 일단 피신하시게!"
                else: v_status, v_adv = f"📈 현지 시초 거래급등 ({v_ratio:.1f}%)", f"✅ 거래량 터졌으나 힘겨루기 중일세. 방향 정해질 때까지 눈 부라리고 보시게."
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                if p_chg > 3 and v_ratio < 100: v_adv = f"🚨 **[가짜 상승 주의!]** 거래량 없이 오르는 건 개미 꼬드기는 격일세."
                elif p_chg > 3 and v_ratio > 150: v_adv = f"🔥 **[진짜 상승!]** 성벽을 제대로 뚫었구먼. 진격하시게!"
                else: v_adv = f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등 신호 (원본 보존)
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"● {'👺 불지옥 문턱일세! 익절하시게.' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # 성벽 수치 (원본 보존)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 (논리 정교화)
            is_divergence = p > prev_p and rsi_val < rsi_prev
            w_momentum = will_val - will_prev
            m_status = "정회전" if m_l > s_l else "역회전"
            
            adv1 = f"1. **배신 감지:** 지수 {rsi_val:.2f}로 {'🚨 가짜 상승 포착! 불 트랩 조심하시게.' if is_divergence else '정상 온도 흐름일세.'}"
            adv2 = f"2. **성벽 사수:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세."
            adv3 = f"3. **엔진(MACD):** {m_status} 상태네. {'역회전폭이 줄어드는지 보시게!' if m_l < s_l else '엔진 시동 걸렸구먼!'}"
            
            if is_divergence: final_adv = "🚨 **[최종 결론]** 지표가 배신했네! 수익 빳빳하게 챙기고 보따리 싸시게!"
            elif w_momentum > 10: final_adv = "🔥 **[최종 결론]** 기세 폭발 중일세! 빳빳하게 보유(홀딩)하시게!"
            elif p <= low_b or rsi_val <= 35: final_adv = "🛡️ **[최종 결론]** 공포의 바닥권일세. 분할 매수 기회네!"
            else: final_adv = "🧐 **[최종 결론]** 냉정하게 성벽 사수 여부 보며 관망하시게."

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # 네 기둥 지수 상세 분석 (로직 보정 완료)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "🏰 **[성벽 사수]** 중앙선 위일세." if p > mid_line else "🏚️ **[성벽 함락]** 중앙선 아래네."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                r_diag = f"● 지수 {rsi_val:.2f}: {'🚨 배신 포착! 온도 급랭 중.' if is_divergence else '정상 온도 흐름일세.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                w_diag = f"● 지수 {will_val:.2f}: {'🔥 기세 폭발!' if w_momentum > 10 else '기세 유지 중일세.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diff = m_l - s_l; m_diff_prev = m_prev_l - s_prev_l
                m_diag = "● 엔진 **정회전**! 홀딩하시게." if m_l > s_l else ("● 엔진 **역회전폭 급감**! 채비 중일세." if m_diff > m_diff_prev else "● 엔진 **역회전 심화**! 자숙하시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
