import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

@st.cache_data(ttl=60)
def fetch_global_market():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info
        return {
            "n_last": nasdaq.last_price, "n_prev": nasdaq.previous_close,
            "s_last": sp500.last_price, "s_prev": sp500.previous_close,
            "t_last": tnx.last_price, "t_prev": tnx.previous_close
        }
    except:
        return {
            "n_last": 25520.24, "n_prev": 25880.0,
            "s_last": 7457.69, "s_prev": 7533.0,
            "t_last": 4.541, "t_prev": 4.569
        }

st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
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
        data = fetch_global_market()
        n_chg = (data["n_last"] / data["n_prev"] - 1) * 100
        tnx_val, tnx_chg = data["t_last"], (data["t_last"] / data["t_prev"] - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{data['n_last']:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{data['s_last']:,.2f}", f"{(data['s_last']/data['s_prev']-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        if tnx_val >= 4.5: adv = "🚨 **[금리 발작: 비상]** 국채 금리 4.5% 돌파! 기술주 성벽 주의하시게."
        elif n_chg > 0.5 and tnx_chg < 0: adv = "🔥 **[골디락스 진입]** 지수 상승과 금리 하락, 기세 타시게."
        else: adv = "🧐 **[눈치싸움 중]** 세력들이 간 보고 있구먼."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930").strip()

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500)
        is_kr = symbol.isdigit()
        now_tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
        now_local = datetime.now(now_tz)

        core_vault = {
            "005930": "삼성전자", "000660": "SK하이닉스", 
            "033100": "제룡전기", "257720": "실리콘투", 
            "058610": "에스피지", "010140": "삼성중공업",
            "035900": "JYP Ent.", "050890": "쏜다텍",
            "086520": "E코프로머티", "042700": "한미반도체", 
            "196170": "알테오젠", "000100": "유한양행"
        }

        df = pd.DataFrame()
        p, prev_p, v_curr, final_display_name = 0.0, 0.0, 0.0, ""

        if is_kr:
            currency, fmt_p = "원", ",.0f"
            code_str = symbol.zfill(6)
            final_display_name = core_vault.get(code_str, f"국내종목 ({code_str})")

            # yfinance 단일 안정선으로 국장 데이터 수집 (차단 및 멈춤 원천 방지)
            try:
                tk = yf.Ticker(f"{code_str}.KS")
                df = tk.history(start=start_date)
                if df.empty:
                    tk = yf.Ticker(f"{code_str}.KQ")
                    df = tk.history(start=start_date)
            except:
                pass
        else:
            currency, fmt_p = "$", ",.2f"
            tk_us = symbol.upper()
            us_vault = {
                "TSLA": "테슬라 (Tesla)", "NVDA": "엔비디아 (NVIDIA)", 
                "AAPL": "애플 (Apple)", "MSFT": "마이크로소프트", 
                "AMZN": "아마존", "GOOGL": "알파벳A", "META": "메타",
                "CPNG": "쿠팡 (CooPang)", "IONQ": "아이온큐 (IonQ)", "NFLX": "넷플릭스 (Netflix)"
            }
            final_display_name = us_vault.get(tk_us, tk_us)

            try:
                ticker = yf.Ticker(tk_us)
                df = ticker.history(start=start_date)
            except:
                pass

        # 백지 멈춤 방어 더미 트랩
        if df.empty:
            dates = pd.date_range(end=datetime.now(), periods=100)
            df = pd.DataFrame({
                'Open': [10000.0] * 100, 'High': [10000.0] * 100,
                'Low': [10000.0] * 100, 'Close': [10000.0] * 100,
                'Volume': [1000.0] * 100
            }, index=dates)

        p = float(df['Close'].iloc[-1])
        v_curr = float(df['Volume'].iloc[-1])
        prev_p = float(df['Close'].iloc[-2]) if len(df) > 1 else p

        # ========================================================
        # 강제 전광판 및 신호등 출력부
        # ========================================================
        df.loc[df.index[-1], 'Close'] = p
        df = df.ffill().dropna()
        
        v_avg5 = float(df['Volume'].iloc[-6:-1].mean()) if len(df) >= 6 else 1.0
        v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 100.0
        
        p_diff = p - prev_p
        p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0.0
        
        s_h, s_m = (9, 0) if is_kr else (9, 30)
        m_start = now_local.replace(hour=s_h, minute=s_m, second=0, microsecond=0)
        
        if now_local < m_start: 
            vol_strength = v_ratio 
        else:
            elapsed = min(390, max(10, (now_local - m_start).seconds / 60))
            if now_local.weekday() >= 5: elapsed = 390
            vol_strength = min(1000, v_ratio / (elapsed / 390))
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        rsi_val, rsi_prev = float(rsi_series.iloc[-1]), float(rsi_series.iloc[-2])
        
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        will_series = (h14 - df['Close']) / (h14 - l14 + 1e-10) * -100
        will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
        will_prev = float(will_series.iloc[-2])
        
        macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        sig_line = macd.ewm(span=9).mean()
        m_l, s_l, m_p, s_p = float(macd.iloc[-1]), float(sig_line.iloc[-1]), float(macd.iloc[-2]), float(sig_line.iloc[-2])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['Std'] = df['Close'].rolling(20).std()
        mid_line = float(df['MA20'].iloc[-1])
        up_b = mid_line + (float(df['Std'].iloc[-1]) * 2)
        low_b = mid_line - (float(df['Std'].iloc[-1]) * 2)
        defense_line = float(df['High'].iloc[-21:-1].max()) * 0.93

        # 전광판 출력
        st.markdown("### 📊 현재주가현황")
        display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
        st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name} ({symbol.upper()})</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

        if vol_strength >= 150: v_status, v_adv = "과열폭발", f"🔥 **[화력폭발]** 현재 강도 {vol_strength:.1f}점! 본진 진격 중이오."
        elif vol_strength >= 100: v_status, v_adv = "매집시작", f"🚀 **[매집시작]** 현재 강도 {vol_strength:.1f}점! 화력이 차오르네."
        elif vol_strength >= 80: v_status, v_adv = "정상화력", f"⚔️ **[정상화력]** 현재 강도 {vol_strength:.1f}점! 기세가 빳빳하구먼."
        else: v_status, v_adv = "기세부족", f"🧊 **[거래절벽]** 현재 강도 {vol_strength:.1f}점! 속지 마시게."
        
        st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status} ({v_ratio:.1f}% / 5일평균대비)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

        bb_bottom       = 1 if p <= (low_b * 1.005) else 0
        rsi_bottom      = 1 if rsi_val <= 35 else 0
        williams_bottom = 1 if will_val <= -80 else 0
        bottom_score    = bb_bottom + rsi_bottom + williams_bottom

        bb_top       = 1 if p >= (up_b * 0.995) else 0
        rsi_top      = 1 if rsi_val >= 60 else 0
        williams_top = 1 if will_val >= -20 else 0 
        top_score    = bb_top + rsi_top + williams_top

        m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
        is_engine_reverse = (m_l < s_l)
        is_reverse_shrinking = is_engine_reverse and (abs(m_diff_curr) < abs(m_diff_prev))

        is_bb_attack = (rsi_val < 30 and will_val <= -80 and abs(m_l - s_l) < abs(m_diff_prev))
        is_macd_turning = (m_l < s_l and m_diff_curr > m_diff_prev)

        if top_score >= 2:
            sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"• {'👿 불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 70 else '• 다중 과열 지표 포착! 기세가 완연한 수확기일세.'} (매도 지표 일치도: {top_score}/3)"
        elif bottom_score >= 2:
            if is_reverse_shrinking or is_macd_turning:
                sig, col, s_adv = "🔴 [명장의 선취매 타점]", "#D32F2F", f"• 🎯 **[필살 변곡점]** 다중 바닥({bottom_score}/3) 상태에서 엔진 역회전 폭이 줄어들기 시작했소! 명장의 날카로운 선취매 타이밍이오!"
            elif is_engine_reverse:
                sig, col, s_adv = "🟡 관망 및 대기 (역회전 심화)", "#FBC02D", f"• ⚠️ 다중 바닥 지표({bottom_score}/3)이나 엔진 역회전이 깊어지는 중일세. 칼 뽑지 말고 폭이 줄어들 때까지 대기하시게."
            else:
                sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", f"• 🧊 다중 바닥 및 엔진 정회전 확정 포착! 자신 있게 진격할 타이밍이오. (매수 지표 일치도: {bottom_score}/3)"
        else:
            sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", f"• 눈치싸움 중일세. 지표 끝단을 기다리시게. (바닥동조: {bottom_score}/3 | 과열동조: {top_score}/3)"
        
        st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

        adv1 = f"1. **진격 금지:** RSI가 {rsi_val:.2f}로 아직 60을 향해 고개를 들지 않았네. 섣불리 뛰어들지 마시게." if rsi_val < 60 else "1. **기세 타기:** RSI가 60을 돌파하며 불이 붙었구먼!"
        adv2 = f"2. **성벽 사수 확인:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세. {'함락됐으니 지하실 조심하시게.' if p < defense_line else '사수 중이니 진격의 발판 삼으시게.'}"
        
        if bottom_score >= 2 and (is_reverse_shrinking or is_macd_turning or m_l >= s_l):
            adv3 = "3. **엔진(MACD) 확인:** 다중 바닥 권역에 엔진 시동 중이네! 소량 분할 매수 기회를 노리시게."
            final_adv = f"🏹 **[최종 결론]** 강도({vol_strength:.1f}점). 다중 바닥 권역 확인 및 엔진 시동 완료! 소량 **[분할 매수]** 타이밍을 노리시게!"
        else:
            if m_l < s_l:
                if is_macd_turning:
                    adv3 = "3. **엔진(MACD) 확인:** 엔진 **역회전폭 급감** 중이라네! 시동 걸 채비 중이니 진격 신호를 기다리시게."
                    final_adv = f"🧐 **[최종 결론]** 강도({vol_strength:.1f}점). 중간 지대에서 엔진 역회전폭 급감 중이네. 기세가 완전히 잡힐 때까지 **무조건 관망 및 대기!**"
                else:
                    adv3 = "3. **엔진(MACD) 확인:** 엔진 **역회전 심화** 중이라네! 거꾸로 도는 차니 절대 속지 마시게!"
                    final_adv = f"🧐 **[최종 결론]** 강도({vol_strength:.1f}점). 중간 지대에서 엔진 역회전 심화 중이네. 기세가 잡힐 때까지 **무조건 관망 및 대기!**"
            else:
                adv3 = "3. **엔진(MACD) 확인:** 엔진 정회전 완료! 본대 진격의 신호탄이 터졌네."
                if p >= up_b or rsi_val >= 60:
                    final_adv = f"🚀 **[최종 결론]** 강도({vol_strength:.1f}점). 성벽 딛고 하늘 문이 열렸네! **비중 유지 및 홀딩!**" if vol_strength >= 150 and p > defense_line else f"💰 **[최종 결론]** 강도({vol_strength:.1f}점). 성벽 위나 기세가 약해지네. **야금야금 분할 매도 시작!**"
                elif p <= (low_b * 1.02):
                    final_adv = f"🧐 **[최종 결론]** 강도({vol_strength:.1f}점). 엔진은 정회전(헛바퀴)이나 성벽 아래일세. 속지 말고 **추가 진격 금지 및 관망!**" if p < defense_line else f"🔮 **[최종 결론]** 강도({vol_strength:.1f}점). 바닥권에서 엔진 정회전 시동 걸렸고 성벽 사수 중이네! **강력 매수 검토!**"
                else:
                    final_adv = f"🧐 **[최종 결론]** 강도({vol_strength:.1f}점). 엔진 정회전이나 추세 탐색 중일세. 중앙선 방향 보며 **무조건 관망 및 대기!**"

        st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
            <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
            <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

        # 지표 상세 진단
        st.divider()
        i1, i2, i3, i4 = st.columns(4)
        
        with i1:
            if p >= up_b: bb_diag = "👺 **[천장 돌파]** 울타리 밖으로 기세 폭발! 탐욕의 끝단이니 익절하시게."
            elif p <= low_b: bb_diag = "🧊 **[바닥 돌파]** 지하실까지 밀렸구먼. 엔진 시동을 기다리시게."
            elif p >= mid_line: bb_diag = "⚠️ **[과열 진입]** 중앙선 위에서 기세 유지 중이나 온도가 높네."
            else:
                if rsi_val < 30 and will_val <= -80 and abs(m_l - s_l) < abs(m_diff_prev):
                    bb_diag = "🏹 **[낙폭과대 진격]** 기세는 중앙선 밑이나, 단기 골짜기 바닥에 엔진 시동 중일세. 소량 분할 매수 시작!"
                else:
                    if m_l < s_l:
                        if abs(m_l - s_l) >= abs(m_diff_prev):
                            bb_diag = "🏠 **[기세 둔화]** 중앙선 밑일세. 엔진 역회전 심화 중이니 절대 칼을 뽑지 마시게."
                        else:
                            bb_diag = "🏠 **[기세 둔화]** 중앙선 밑일세. 엔진 역회전폭 급감 중이나 지표 미달이니 진격 신호를 기다리시게."
                    else:
                        bb_diag = "🏠 **[기세 둔화]** 중앙선 밑일세. 엔진 정회전이나 기세가 약하니 절대 칼을 뽑지 마시게."
            st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
        
        with i2:
            rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
            is_div = p > prev_p and rsi_val < rsi_prev
            
            if rsi_val >= 60: 
                msg_type = '🚨 가짜 상승이니 대피하시게.' if is_div else '수익 챙길 채비 하시게.'
                r_status = f"**👿 불지옥** 문턱! {msg_type}"
            elif rsi_val <= 35: 
                if rsi_val > rsi_prev:
                    r_status = "**🧊 냉골 바닥**이나, 어제보다 온도가 올라오며 **[지수 개선]** 중일세. 추이를 주시하시게."
                else:
                    r_status = "**🧊 냉골 바닥**일세. 온도가 계속 떨어지며 **[지속 하락]** 중이니 냉정하게 보따리 푸시게."
            else: 
                msg_type = '🚨 가짜 기세니 눈 부라리고 보시게.' if is_div else '끝단을 기다리시게.'
                r_status = f"중립일세. {msg_type}"
            
            st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f} <span style='font-size:25px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>● {r_status}</p></div>", unsafe_allow_html=True)
        
        with i3:
            will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
            
            if will_val >= -20: 
                w_status = "**🚩 천장 광기**! 비수 꽂히기 전에 수확하시게."
            elif will_val >= -35: 
                w_status = "**⚠️ 천장 근접**! 고점 징후니 주시하시게."
            elif will_val <= -80: 
                if will_val > will_prev:
                    w_status = "**🏳️ 개미 항복 구역**이나, 기운이 고개를 들며 **[지수 개선]** 중일세. 진격 준비를 고려하시게."
                else:
                    w_status = "**🏳️ 개미 항복 구역**일세. 여전히 밑바닥으로 **[지속 하락]** 중이니 보따리 풀 준비만 하시게."
            elif will_val <= -65: 
                if will_val > will_prev:
                    w_status = "**📉 낙폭 과대** 구역이나, 어제보다 기세가 올라오며 **[하락 브레이크]**가 잡히고 있소."
                else:
                    w_status = "**📉 하락 가속**! 어제보다 기세가 더 꺾였으니 절대 칼 뽑지 마시게."
            else: 
                w_status = "중간 지대일세. 기세를 냉정하게 지켜보시게."
            
            st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f} <span style='font-size:25px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>● {w_status}</p></div>", unsafe_allow_html=True)
        
        with i4:
            if m_l > s_l: m_diag = "● 엔진 **정회전(헛바퀴)**! 성벽 무너졌으니 속지 마시게." if p < defense_line else "● 엔진 **정회전**! 성벽 사수하며 자신 있게 진격하시게."
            else: m_diag = "● 엔진 **역회전폭 급감**! 시동 걸 채비 중이니 진격 신호를 기다리시게." if m_diff_curr > m_diff_prev else "● 엔진 **역회전 심화**! 거꾸로 도는 차니 냉정하게 자숙하시게."
            st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")