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
        
        if tnx_val >= 4.5: adv = "🚨 **[금리 발작: 비상]** 국채 금리가 4.5%를 넘어섰네! 기술주 성벽 무너질 수 있으니 진격을 멈추시게."
        elif n_chg > 0.5 and tnx_chg < 0: adv = "🔥 **[골디락스 진입]** 지수는 오르고 금리는 내리니 기세 타시게."
        else: adv = "🧐 **[눈치싸움 중]** 세력들이 간 보고 있구먼. 섣부른 판단은 독이네."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); is_kr = symbol.isdigit()
        now_tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
        now_local = datetime.now(now_tz)

        if is_kr:
            ticker = yf.Ticker(f"{symbol}.KS")
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            try:
                df_krx = fdr.StockListing('KRX')
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = ticker.info.get('shortName', symbol).split(',')[0]
            currency, fmt_p = "원", ",.0f"
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol)
            currency, fmt_p = "$", ",.2f"

        if not df.empty:
            df = df.ffill().dropna()
            
            # [현주가 및 실시간 거래량 수술]
            df_today = fdr.DataReader(symbol, start=now_local.strftime('%Y-%m-%d')) if is_kr else ticker.history(period='1d')
            if not df_today.empty:
                p = float(df_today['Close'].iloc[-1])
                v_curr = float(df_today['Volume'].iloc[-1])
            else:
                p = float(df['Close'].iloc[-1])
                v_curr = 0

            # 5일 평균 거래량 (분모 격리)
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0

            prev_p = float(df['Close'].iloc[-2])
            if is_kr and p == prev_p and len(df) > 2: prev_p = float(df['Close'].iloc[-3])
            p_diff, p_chg = p - prev_p, (p - prev_p) / prev_p * 100

            # 시간 보정 로직
            s_h, s_m = (9, 0) if is_kr else (9, 30)
            elapsed = (now_local.hour - s_h) * 60 + (now_local.minute - s_m)
            if now_local.weekday() >= 5 or elapsed > 390: elapsed = 390
            elif elapsed < 10: elapsed = 10
            vol_strength = v_ratio / (elapsed / 390)

            # 지표 계산 (엄수)
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

            # 전광판
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"""<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>""", unsafe_allow_html=True)

            is_opening = 9 <= now_local.hour <= 11
            
            # [수정] 시초(is_opening)일 때는 강도 점수(vol_strength)를 기준으로 판독하네
            if is_opening:
                if vol_strength >= 130: v_label, v_status = "🔥 시초 거래폭발", f"🔥 시초 거래폭발"
                elif vol_strength >= 80: v_label, v_status = "📈 시초 거래급등", f"📈 시초 거래급등"
                else: v_label, v_status = "✅ 시초 거래진행", f"✅ 시초 거래진행"
            else:
                v_label = "💤 거래침체" if vol_strength < 70 else "📈 거래증가" if vol_strength < 150 else "🔥 거래폭발"
                v_status = v_label

            v_adv = f"🔥 **[진짜 상승!]** 거래량 실린 빳빳한 진격일세!" if p_chg > 3 and vol_strength > 130 else f"✅ 현재 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            
            # 화면 출력 (v_status와 v_ratio를 함께 보여주네)
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등
            # --- 신호등 및 상황별 조언 로직 (수정본) ---

# 🟢 [매도권/비상] 구간
            if p >= up_b or rsi_val >= 60:
                sig, col = "🟢 매도권 진격", "#388E3C"
    # 어르신의 상황에 따른 쌍방향 조언
                s_adv = (
                    "• 🚀 **[보유]** 수익 극대화! 성벽 위에서 빳빳하게 홀딩하시게.\n"
                    "• 🔥 **[미보유]** 달리는 말일세! 지금이라도 정찰대 투입 적기."
                )

# 🔴 [매수권/바닥] 구간
            elif p <= (low_b * 1.005) or rsi_val <= 35:
                sig, col = "🔴 매수권 진입", "#D32F2F"
    # 어르신의 상황에 따른 쌍방향 조언
                s_adv = (
                    "• 🛡️ **[보유]** 추가 매수 금지! 엔진 돌아설 때까지 자중자애하시게.\n"
                    "• 👀 **[미보유]** 싸다고 덥석 물면 지하실 구경하네. 관망하시게."
                )

# 🟡 [관망/대기] 구간
            else:
                sig, col = "🟡 관망 및 대기", "#FBC02D"
                s_adv = "• 🧐 눈치싸움 중일세. 지표 끝단을 기다리며 칼자루만 쥐고 계시게."

# ---------------------------------------
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 (냉정 복구)
            adv1 = f"1. **진격 금지:** RSI가 {rsi_val:.2f}로 아직 60을 향해 고개를 들지 않았네. 섣불리 뛰어들지 마시게." if rsi_val < 60 else "1. **기세 타기:** RSI가 60을 돌파하며 불이 붙었구먼!"
            adv2 = f"2. **성벽 사수 확인:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세. {'함락됐으니 지하실 조심하시게.' if p < defense_line else '사수 중이니 진격의 발판 삼으시게.'}"
            adv3 = f"3. **엔진(MACD) 확인:** 엔진이 아직 **역회전** 중이라네! 절대 속지 마시게!" if m_l < s_l else "3. **엔진 정회전:** 엔진 시동 걸렸구먼!"
            
            # [최종 수술] 어르신 지침대로 고점 역회전 심화 및 생명선(-3%) 반영하네
            stop_loss_p = p * 0.97 # 진입가 대비 -3% 생명선 계산
            m_diff = m_l - s_l     # 현재 엔진 간격
            m_diff_p = m_p - s_p   # 어제 엔진 간격

            # [최종 수술] 어르신 전용 3X3 필살 대응 로직 (성벽 사수 여부 통합)
            stop_loss_p = p * 0.97 # 진입가 대비 -3% 생명선
            m_diff, m_diff_p = (m_l - s_l), (m_p - s_p) # 엔진 간격(입술)

            # --- [꼭대기 3대 전술: 성벽 위 진격] ---
            if p >= up_b or rsi_val >= 60:
                if m_l < s_l: # [꼭대기 3] 엔진 역회전 + 성벽 위태 (탈출)
                    if p < defense_line or abs(m_diff) > abs(m_diff_p):
                        final_adv = f"🚨 **[최종 결론]** 거래강도({vol_strength:.0f}점). 성벽({format(defense_line, fmt_p)}) 위태롭고 엔진 역회전 심화! **전량 익절**하시게!"
                    else:
                        final_adv = f"⚠️ **[최종 결론]** 거래강도({vol_strength:.0f}점). 성벽 사수 중이나 엔진 역회전 초입일세. **30~50% 부분 익절**하시게."
                elif vol_strength > 150 and p > defense_line: # [꼭대기 1] 성벽 위 비상 (불사조)
                    final_adv = f"🚀 **[최종 결론]** 거래강도({vol_strength:.0f}점). 성벽 딛고 하늘 문이 열렸네! 정회전에 물량 실렸으니 **빳빳하게 홀딩**하시게!"
                else: # [꼭대기 2] 성벽 위 정체 (수확)
                    final_adv = f"💰 **[최종 결론]** 거래강도({vol_strength:.0f}점). 성벽 위나 기세가 약해지네. **야금야금 분할 매도**로 수확하시게."

            # --- [바닥권 3대 전술: 성벽 탈환 시도] ---
            elif p <= (low_b * 1.02):
                if m_l < s_l or p < (defense_line * 0.90): # [바닥 3] 성벽과 너무 멀거나 엔진 역전 (금지)
                    final_adv = f"💀 **[최종 결론]** 거래강도({vol_strength:.0f}점). 성벽에서 너무 멀고 엔진도 역회전이네. **절대 매수 금지**일세."
                elif vol_strength > 130 and p >= (defense_line * 0.95): # [바닥 1] 성벽 탈환 직전 + 물량 (진격)
                    final_adv = f"🔥 **[최종 결론]** 거래강도({vol_strength:.0f}점). 진짜 바닥에 물량 실렸고 성벽 탈환 직전이네! **{format(p, fmt_p)}**서 적극 진격하시게! (손절 -3%)"
                else: # [바닥 2] 바닥 정회전이나 성벽이 멂 (정찰)
                    final_adv = f"🛡️ **[최종 결론]** 거래강도({vol_strength:.0f}점). 엔진은 도는데 성벽이 아직 멀구먼. 소량 **정찰대**만 보내고 성벽 돌파 보시게."

            # --- 미장 거래강도 수치 보정 (203행 바로 위에 추가) ---
            # --- [203행 시작] 미장 판별 및 거래강도 수치 보정 ---
            is_us_market = any(c.isalpha() for c in name) if 'name' in locals() else False
            if is_us_market and vol_strength > 300:
                import math
                vol_strength = 100 + (math.log10(vol_strength / 100) * 100)
                vol_strength = min(vol_strength, 300)

# --- [중간 지지 및 결론 도출] ---
            elif m_l < s_l or p < defense_line:
                diag = "엔진 역회전" if m_l < s_l else "성벽 함락"
                final_adv = f"🧐 **[최종 결론]** 거래강도({vol_strength:.0f}점). {diag} 상태일세. 칼 뽑지 말고 성벽 회복 전까지 **무조건 관망!**"

            else:
                final_adv = f"🚀 **[최종 결론]** 거래강도({vol_strength:.0f}점). 성벽 위 안착 및 기세가 빳빳하네! **정찰대 진격 가능**할세."
            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # 4대 지수 정밀 진단 (원본 문구 완벽 복원)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "⚠️ **[과열 진입]** 성벽 사수 중이나 온도가 높네. 홀딩보다는 수익을 빳빳하게 확정 지으며 다음 성벽을 준비하시게." if p >= up_b or rsi_val >= 60 else ("🏰 **[성벽 사수]** 중앙선 위에서 안정적 진격 중일세. 아직 온도가 적당하니 성벽 무너지기 전까지는 홀딩하시게." if p > mid_line else "🏚️ **[성문 함락]** 성벽 밑일세. 온도가 낮아도 엔진 시동 걸리기 전까지는 절대 칼 뽑지 마시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                is_div = p > prev_p and rsi_val < rsi_prev
                if rsi_val >= 60: r_diag = f"● 지수 {rsi_val:.2f}로 **👺 불지옥** 문턱일세! {'🚨 온도가 식고 있네(배신 포착)! 가짜 상승이니 대피하시게.' if is_div else '천장에 다 왔으니 수익 챙길 채비 하시게.'}"
                elif rsi_val <= 35: r_diag = f"● 지수 {rsi_val:.2f}로 **🧊 냉골** 바닥일세! 남들 무서워할 때 우리는 냉정하게 보따리 푸시게."
                else: r_diag = f"● 지수 {rsi_val:.2f}로 중립일세. {'🚨 주가는 오르나 온도가 식고 있네! 눈 부라리고 보시게.' if is_div else '지표 끝단을 기다리시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                if will_val >= -20: w_diag = f"● 지수 {will_val:.2f}로 **🧨 천장 광기** 구간일세! 개미들 눈 뒤집혔으니 비수 꽂히기 전에 수확(익절)하시게."
                elif will_val >= -35: w_diag = f"● 지수 {will_val:.2f}로 **⚠️ 천장 근접** 구간일세! 고점 징후 포착되었으니 눈 부라리고 주시하시게."
                elif will_val <= -80: w_diag = f"● 지수 {will_val:.2f}로 **🏳️ 개미 항복** 구간일세! 보따리 풀 준비 하시되, 고개 들 때까지 기다리시게."
                elif will_val <= -65: w_diag = f"● 지수 {will_val:.2f}로 **📉 하락 가속** 구간일세! 바닥 확인 전까지는 절대 칼 뽑지 말고 자숙하시게."
                else: w_diag = f"● 지수 {will_val:.2f}로 중간 지대일세. 기세가 어느 쪽으로 튈지 냉정하게 지켜보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diff, m_diff_p = m_l - s_l, m_p - s_p
                if m_l > s_l: m_diag = "● 엔진 **정회전(헛바퀴)** 중일세! 성벽이 무너졌으니 속지 마시게." if p < defense_line else "● 엔진 **정회전** 중일세! 기세 붙었으니 성벽 사수 여부 보며 자신 있게 진격하시게."
                else: m_diag = "● 엔진 **역회전폭 급감**! 시동 걸 채비 중이니 보따리 챙겨두고 진격 신호를 기다리시게." if m_diff > m_diff_p else "● 엔진 **역회전 심화** 중일세! 거꾸로 도는 차에 올라타면 안 되는 법, 냉정하게 자숙하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
