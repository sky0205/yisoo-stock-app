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

        # --- 이수 할배의 빳빳한 정밀 훈수 (여기서부터 수술일세) ---
        if tnx_val >= 4.5:
            advice = "🚨 **[금리 발작: 비상]** 국채 금리가 4.5%를 넘어섰네! 기술주 성벽 무너질 수 있으니 진격을 멈추시게."
        elif n_chg > 0.5 and tnx_chg < 0:
            advice = "🔥 **[골디락스 진입]** 지수는 오르고 금리는 내리니, 이건 하늘이 준 진격의 기회일세! 기세 타시게."
        elif n_chg < -1.0:
            advice = "💀 **[패닉 셀 감지]** 나스닥 비명 지르며 투매 중이네. 성문 닫고 소나기 피하는 게 상책일세."
        elif tnx_val > 4.2:
            advice = "⚠️ **[금리 압박: 주의]** 금리가 빳빳하게 고개 드니 시장 맷집 시험할 걸세. 무리한 진격은 금물이네."
        else:
            advice = "🧐 **[눈치싸움 중]** 세력들이 다음 재료 기다리며 간 보고 있구먼. 섣부른 판단은 독이네."

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
            # [수정] 국장도 미장처럼 yfinance를 써야 튼튼하게 가져오네!
            now_local = datetime.now(pytz.timezone('Asia/Seoul'))
            currency = "원"; fmt_p = ",.0f"
            ticker_symbol = f"{symbol}.KS" # 삼성전자면 005930.KS로 변환!
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(start=start_date, end=end_date)
          # [74번 줄] 기존 74~86번 줄 싹 지우고 딱 이 6줄만 넣으시게!
            try:
                import FinanceDataReader as fdr
                df_krx = fdr.StockListing('KRX')
                # 종목번호와 똑같은 이름을 찾아서 빳빳하게 가져오네
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except:
                # 한국 서버가 죽었을 때만 미국 서버 이름을 쓰되, 복잡한 건 다 떼버리네
                name = ticker.info.get('shortName', symbol).split(',')[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern'))
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol)
        
        # [87번 줄 추가] 미장은 달러($)를 쓰고, 소수점 2자리(,.2f)까지 보여줘야 하네!
            currency = "$"; fmt_p = ",.2f"
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
        # 93-94: 데이터 세척 (주말에도 종가를 사수하네)
            df = df.ffill().dropna()

        # 95-97: [핵심 수술] 오늘 가격(p)과 전일 가격(prev_p)을 가져오네
            p = float(df['Close'].iloc[-1])
        
        # 주말/휴일에는 오늘과 어제 데이터가 같을 수 있으니, 한 칸 더 뒤를 보네
            prev_p = float(df['Close'].iloc[-2])
            if is_kr and p == prev_p and len(df) > 2:
                prev_p = float(df['Close'].iloc[-3]) # 금요일 vs 목요일 비교!
        
        # 101-104: 전일비 금액과 비율을 빳빳하게 계산하네
            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100

            peak_20 = float(df['Close'].iloc[-21:-1].max())
            defense_line = peak_20 * 0.93
            unit = "원" if is_kr else "$"

            peak_20 = float(df['Close'].iloc[-21:-1].max())
            defense_line = peak_20 * 0.93

        # 98-99: 거래량 데이터
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 else 0

        # 98-99: 거래량 점수 계산 기초 데이터
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 else 0
            # 기술 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val = rsi_series.iloc[-1]   # 오늘의 온도
            rsi_prev = rsi_series.iloc[-2]  # 어제의 온도 (이 녀석이 범인이었네!)
            h14 = df['High'].rolling(14).max(); l14 = df['Low'].rolling(14).min()
            will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
            signal = macd.ewm(span=9).mean()
            m_l = macd.iloc[-1]; s_l = signal.iloc[-1]
            m_p = macd.iloc[-2]; s_p = signal.iloc[-2] # 어제의 엔진 상태
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [수정] 어르신 명하신 대로 제목만 정갈하게 추가
            st.markdown("### 📊 현재주가현황")
           # [수정] 화폐 단위와 전광판 출력 로직 - 131번 줄 근처에 넣으시게!
            unit = "원" if is_kr else "$"
        
            # [최종 수술] 화폐 단위 설정 및 시원시원한 전광판 출력
            unit = "원" if is_kr else "$"
        
            if is_kr:
            # 국장용: 글씨 28px로 키우고 전일비 금액까지 빳빳하게!
                display_price = f"{p:,.0f}{unit} (전일비: {p_diff:+,.0f} / {p_chg:+.2f}%)"
            else:
            # 미장용: $169.37 (전일비: -2.10 / -1.22%)
                display_price = f"{unit}{p:,.2f} (전일비: {p_diff:+.2f} / {p_chg:+.2f}%)"

        # 화면에 큼직하게 뿌려주는 전광판 (배경색까지 넣었네)
            st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                    <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p>
                </div>
            """, unsafe_allow_html=True)
            # [시간 가중치 로직 추가] - 114번 줄 바로 위에 넣으시게!
            now_tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
            now = datetime.now(now_tz)
        
            # 시작 시간 설정 (국장 9:00, 미장 9:30)
            s_h, s_m = (9, 0) if is_kr else (9, 30)
        
            # 123번 줄: 현재 경과 시간을 계산하네
            elapsed = (now.hour - s_h) * 60 + (now.minute - s_m)

        # 124번 줄: [핵심] 주말이거나 장 마감(오후 3:30) 이후면 390분으로 고정!
            if now.weekday() >= 5 or elapsed > 390:
                elapsed = 390
            elif elapsed < 10:
                elapsed = 10
        
            # [핵심] 시간 대비 거래 강도 점수 (150점 이상이면 '급증'으로 보네)
            vol_strength = (v_ratio / (elapsed / 390))
            # 거래량 상세 판독 및 호통 로직 (원본 보존)
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            if v_ratio >= 30 and is_opening:
                if p_chg >= 3: v_status, v_adv = f"🔥 현지 시초 주가 폭등 / 거래폭발 ({v_ratio:.1f}%)", f"🔥 **[세력 진격!]** 거래량이 5일 평균 대비 {v_ratio:.1f}% 터지며 폭등 중일세! 진짜 세력이 미는 거니 빳빳하게 기세 타시게!"
                elif p_chg <= -3: v_status, v_adv = f"💀 현지 시초 주가 폭락 / 거래폭발 ({v_ratio:.1f}%)", f"💀 **[비명 포착!]** 거래량이 {v_ratio:.1f}% 터지며 폭락 중일세! 성벽 함락 중이니 일단 피신하시게!"
                else: v_status, v_adv = f"📈 현지 시초 거래급등 ({v_ratio:.1f}%)", f"✅ 거래량 {v_ratio:.1f}%로 터졌으나 주가가 힘겨루기 중일세. 방향 정해질 때까지 눈을 부라리고 보시게."
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                if p_chg > 3 and v_ratio < 100: v_adv = f"🚨 **[가짜 상승 주의!]** 주가는 {p_chg:.2f}% 올랐는데 거래량은 {v_ratio:.1f}%로 빈 수레일세! 개미 꼬드기는 격이니 속지 마시게."
                elif p_chg > 3 and v_ratio > 150: v_adv = f"🔥 **[진짜 상승!]** 거래량 {v_ratio:.1f}% 실린 빳빳한 진격일세! 성벽을 제대로 뚫었구먼."
                else: v_adv = f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등 신호 (원본 보존)
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"● {'👺 불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= (low_b * 1.005) or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 겁먹지 말고 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 및 최종 결론 (성벽 우선 판정)
            adv1 = f"1. **진격 금지:** RSI가 {rsi_val:.2f}로 아직 60을 향해 고개를 들지 않았네. 섣불리 뛰어들지 마시게." if rsi_val < 60 else "1. **기세 타기:** RSI가 60을 돌파하며 불이 붙었구먼!"
            adv2 = f"2. **성벽 사수 확인:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세. {'함락됐으니 지하실 조심하시게.' if p < defense_line else '사수 중이니 진격의 발판 삼으시게.'}"
            adv3 = f"3. **엔진(MACD) 확인:** 엔진이 아직 **역회전** 중이라네! 절대 속지 마시게!" if m_l < s_l else "3. **엔진 정회전:** 엔진 시동 걸렸구먼!"
            
           # [최종 결론 생성] - 여기서부터 177번 줄까지 빳빳하게 갈아 끼우시게!
            if p >= up_b or rsi_val >= 60:
                final_adv = f"💰 **[최종 결론]** 거래강도({vol_strength:.0f}점). 탐욕의 끝자락일세. **분할 매도**하여 수익을 챙기시게!"
        
            elif m_l < s_l or p < defense_line:
            # 150점이 넘으면 경고등(🚨)을 켜고, 아니면 일반 관망(🧐)으로 표시하네
                if vol_strength > 150:
                    final_adv = f"🚨 **[최종 결론]** 거래량({vol_strength:.0f}점) 실린 폭락세일세! **무조건 관망하고 소나기를 피하시게!**"
                else:
                    final_adv = f"🧐 **[최종 결론]** 거래강도({vol_strength:.0f}점). 엔진 역회전 혹은 성벽 위태롭네. **관망하며 기다리시게!**"

            elif p <= (defense_line * 1.01): # 성벽 근처 바닥권
                if vol_strength > 150:
                    final_adv = f"🔥 **[최종 결론]** 거래량({vol_strength:.0f}점) 실린 진짜 바닥권일세! **강력 분할 매수**하시게!"
                else:
                    final_adv = f"🛡️ **[최종 결론]** 거래강도({vol_strength:.0f}점). 공포의 바닥권이나 기세가 약하네. **천천히 분할 매수**하시게!"
        
            elif rsi_val <= 35:
                final_adv = f"🛡️ **[최종 결론]** 거래강도({vol_strength:.0f}점). 지표 온도가 냉골일세. **분할 매수**로 대응하시게!"
            
            else:
                final_adv = f"📈 **[최종 결론]** 거래강도({vol_strength:.0f}점). 추세 살아있구먼. 성벽 사수 확인하며 **보유(홀딩)**하시게!"
            # --- 필살 전략 박스 출력부 (자네 양식 그대로일세) ---
            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)
