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
           # --- [74~84번 줄 교체] 네이버 전용 실시간 안전 로직 ---
            try:
                # 1. 네이버 서버에서 오늘 실시간 데이터를 가져오네
                df_today = fdr.DataReader(symbol, start=now_local.strftime('%Y-%m-%d')) if is_kr else ticker.history(period='1d')
                
                if not df_today.empty:
                    p = float(df_today['Close'].iloc[-1])
                    v_curr = float(df_today['Volume'].iloc[-1])
                else:
                    # 오늘 장부가 비었으면 마지막 종가와 거래량 0으로 설정하네
                    p = float(df['Close'].iloc[-1])
                    v_curr = 0
            except:
                # 2. 서버 통신 장애 시에도 멈추지 않고 마지막 데이터로 대체하네
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
            # --- [109번 줄 삽입] 청년의 냉철한 기세 및 간극 판단 로직 ---
            m_diff = m_l - s_l      # 현재 엔진 간격 (입술)
            m_diff_p = m_p - s_p    # 전일 엔진 간격
            is_forward = m_l > s_l  # 엔진 정회전(MACD 골든크로스 상태) 여부
            
            # 볼린저 밴드 하단 간극 축소 여부 판별
            current_width = up_b - low_b
            prev_width = (df['Std'].iloc[-2] * 4) # 전일 밴드폭 (상단-하단 간격)
            is_narrowing = current_width < prev_width
            # 전광판
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"""<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>""", unsafe_allow_html=True)

            is_opening = 9 <= now_local.hour <= 11
            
            # [수정] 어르신의 지침: 전황 옆에는 수치만, 아래 분석 내용에 상태 포함
            if v_ratio < 0.50:
                v_status = "기세부족"
                v_msg = "아직은 안개뿐이니, 아군 화력을 더 기다리시게."
            elif v_ratio < 1.00:
                v_status = "매집시작"
                v_msg = "평균치를 향해 아군 화력이 차오르고 있으니 눈여겨보시게."
            elif v_ratio < 1.50:
                v_status = "주의단계"
                v_msg = "평균 화력을 넘어섰구먼! 기세가 충만하니 추세를 타며 소량 대응해 보시게."
            else:
                v_status = "과열폭발"
                v_msg = "화력이 폭발 중일세! 단기 고점의 위험이 있으나, 기세가 범상치 않으니 냉정하게 대응하시게."

    # [1. 화면 출력용] 전황 옆에는 수치(%)만 빳빳하게 보여주네
            st.markdown(f"📊 **거래량 전황**: {v_ratio:.1f}%")

    # [2. 분석 내용] 그 아래에 상태와 지침이 한꺼번에 보이게 하네
            v_adv = f"현재 [{v_status}] 단계로, {v_msg}"
            # 신호등
           # --- [141번 줄부터 끝까지 통째로 교체] ---
            v_score = vol_strength
            if not is_kr and v_score > 300:
                import math
                v_score = 100 + (math.log10(v_score / 100) * 100)
                v_score = min(v_score, 300)

            # 1. 5단계 신호등 로직 (어르신 지정 색상: 매수-빨강 / 관망-노랑 / 매도-파랑)
            if p >= up_b or rsi_val >= 70:
                # [매도] 파란색 계열로 변경
                if is_forward and v_score > 150:
                    sig, col = "💰 매도 권유 (강세)", "#1E88E5"
                    s_adv = "• [보유] 기세 좋으니 홀딩! / [비보유] 첨병 파견 가능 (단, 3% 손절 엄수!)"
                    final_adv = f"💰 **[최종 결론]**. 거래강도({v_score:.0f}점). 정회전 기세 살아있으니 수익을 즐기시게."
                else:
                    sig, col = "💰 매도 권유 (주의)", "#0D47A1"
                    s_adv = "• [보유] 역회전 감지, 강한 매도 권유! / [비보유] 진입 절대 금지!"
                    final_adv = f"💰 **[최종 결론]**. 거래강도({v_score:.0f}점). 성벽 위협받으니 미련 없이 챙겨서 나오시게."

            elif p <= low_b or rsi_val <= 35:
                # [매수] 빨간색 계열로 유지 및 강화
                if is_narrowing:
                    sig, col = "☘️ 매수 신호 (진입)", "#D32F2F"
                    s_adv = "• [지침] 간극 축소 확인! 분할 매수 및 첨병 파견 시작(공격적 대응)!"
                    final_adv = f"☘️ **[최종 결론]**. 거래강도({v_score:.0f}점). 하강 에너지 소멸 중이니 조용히 보따리 푸시게."
                else:
                    sig, col = "☘️ 매수 신호 (대기)", "#C62828"
                    s_adv = "• [지침] 간극 확대 중! 바닥 밑 지하실 위험 있으니 좀 더 인내하며 대기!"
                    final_adv = f"☘️ **[최종 결론]**. 거래강도({v_score:.0f}점). 역회전 심화 중이니 아직 칼 뽑지 마시게."

            elif p < defense_line:
                # [관망-위험] 노란색 계열로 변경
                sig, col = "🧐 관망 (위험)", "#FBC02D"
                s_adv = "• [보유] 비중 축소 및 후퇴 권유 / [비보유] 성벽 아래 무법지대, 진입 절대 금지!"
                final_adv = f"🧐 **[최종 결론]**. 거래강도({v_score:.0f}점). 성벽 함락 상태일세. 냉정하게 관망하시게."

            elif is_forward and p >= defense_line and v_score > 100:
                # [진격] 매수와 같은 빨간색 계열
                sig, col = "🔥 진격 (진행)", "#E53935"
                s_adv = "• [보유] 홀딩 및 관망 / [비보유] 본진 투입(전량 매수)하여 기세 타시게!"
                final_adv = f"🔥 **[최종 결론]**. 거래강도({v_score:.0f}점). 엔진 정회전에 성벽 안착, 승기를 잡았네."

            else:
                # [관망-보통] 노란색 계열
                sig, col = "🧐 관망 (보통)", "#FFEB3B"
                s_adv = "• [보유] 탈출 및 진격 기회 대기 / [비보유] 안개 정국, 섣불리 움직이지 마시게."
                final_adv = f"🧐 **[최종 결론]**. 거래강도({v_score:.0f}점). 지표 혼조세이니 느긋하게 지켜보시게."
            # --- [185번 줄부터 261번 줄까지 이 내용으로 대체] ---
            
            # 1. 미장 거래량 점수 보정 (중복 없이 여기서 한 번만 계산)
            v_score = vol_strength
            if not is_kr and v_score > 300:
                import math
                v_score = 100 + (math.log10(v_score / 100) * 100)
                v_score = min(v_score, 300)

            # 2. 실전 필살 대응 전략 텍스트 생성
            adv1_txt = f"1. [진격 금지] RSI가 {rsi_val:.2f}로 아직 60을 향해 고개를 들지 않았네." if rsi_val < 60 else "1. [기세 타기] RSI가 60을 돌파하며 불이 붙었구먼!"
            adv2_txt = f"2. [성벽 사수 확인] 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세."
            adv3_txt = f"3. [엔진 확인] 엔진이 아직 역회전 중이라네!" if not is_forward else "3. [엔진 정회전] 엔진 시동 걸렸구먼!"

            # 3. 화면 출력: 신호등 전광판
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # 4. 화면 출력: 하단 3대 기둥 가격 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 5. 화면 출력: 실전 대응 전략 카드
            t_html = "<div class='trend-card'>"
            t_html += f"<div class='trend-title'>[필살] {name} 실전 대응 전략</div>"
            t_html += f"<div class='trend-item'>{adv1_txt}</div>"
            t_html += f"<div class='trend-item'>{adv2_txt}</div>"
            t_html += f"<div class='trend-item'>{adv3_txt}</div>"
            t_html += "<hr style='border:1px solid #FFEBEE;'>"
            t_html += f"<div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div>"
            t_html += "</div>"
            
            st.markdown(t_html, unsafe_allow_html=True)
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
