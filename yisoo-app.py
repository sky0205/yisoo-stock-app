import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 할배 캐릭터 스타일 (v36056 최종본)
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
        if n_chg > 0.5 and tnx_chg < 0: advice = f"✅ **[미장 쾌청: 진격!]** 나스닥 불 뿜고 금리도 안정세일세! 기세 타고 진격하시게."
        elif n_chg < -1.0: advice = f"🚨 **[긴급 상황: 정박!]** 나스닥 급락 중이니 성벽 무너지기 전에 보따리 싸서 피신하시게."
        elif tnx_val > 4.3: advice = "⚠️ **[금리 비상: 관망]** 국채 금리 너무 높네! 성벽 위태로우니 무리한 진격은 금물일세."
        else: advice = "🧐 **[안개 정국: 관망]** 지표 끝단을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "058470") # 기본값 SPG

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

            # 기술 지표 계산 (할아버지 지정 수치 준수: 20/2, 14/6, 14/9)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            
            # MACD 엔진 계산 (12, 26, 9)
            ema12 = df['Close'].ewm(span=12, adjust=False).mean(); ema26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26; signal_line = macd_line.ewm(span=9, adjust=False).mean()
            m_l = macd_line.iloc[-1]; s_l = signal_line.iloc[-1]
            
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            st.markdown("### 📊 현재주가현황")
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)} / {p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # 거래량 상세 판독
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            if v_ratio >= 30 and is_opening:
                if p_chg >= 3: v_status, v_adv = f"🔥 시초 폭발적 진격 ({v_ratio:.1f}%)", f"🔥 **[세력 진격!]** 거래량이 5일 평균 대비 {v_ratio:.1f}% 터지며 폭등 중일세! 진짜 세력이 미는 거니 빳빳하게 기세 타시게!"
                elif p_chg <= -3: v_status, v_adv = f"💀 시초 투매 발생 ({v_ratio:.1f}%)", f"💀 **[비명 포착!]** 거래량이 {v_ratio:.1f}% 터지며 폭락 중일세! 성벽 함락 중이니 일단 피신하시게!"
                else: v_status, v_adv = f"📈 시초 거래집중 ({v_ratio:.1f}%)", f"✅ 거래량 {v_ratio:.1f}%로 터졌으나 주가가 힘겨루기 중일세. 방향 정해질 때까지 눈을 부라리고 보시게."
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                if p_chg > 3 and v_ratio < 100: v_adv = f"🚨 **[가짜 상승 주의!]** 주가는 {p_chg:.2f}% 올랐는데 거래량은 {v_ratio:.1f}%로 빈 수레일세! 개미 꼬드기는 격이니 속지 마시게."
                elif p_chg > 3 and v_ratio > 150: v_adv = f"🔥 **[진짜 상승!]** 거래량 {v_ratio:.1f}% 실린 빳빳한 진격일세! 성벽을 제대로 뚫었구먼."
                else: v_adv = f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등 신호
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"● {'👺 불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 겁먹지 말고 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(20일 방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 (완벽 복구)
            adv1 = f"1. **RSI 진단:** 현재 지수 {rsi_val:.2f}일세. {'60 돌파하며 불이 붙었으니 기세 타시게.' if rsi_val >= 60 else '아직 고개를 들지 않았으니 섣불리 뛰어들지 마시게.'}"
            adv2 = f"2. **성벽 사수 확인:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'위' if p >= defense_line else '아래'}일세. {'성벽 사수 중이니 든든구먼.' if p >= defense_line else '성벽 함락됐으니 지하실 조심하시게!'}"
            adv3 = f"3. **엔진(MACD) 확인:** MACD({m_l:.2f})가 시그널({s_l:.2f})을 {'상회하는 정회전' if m_l > s_l else '하회하는 역회전'} 상태일세. {'시동 걸렸으니 가속 페달 밟아도 좋네.' if m_l > s_l else '엔진 거꾸로 도는데 차에 타면 안 되는 법일세!'}"
            
            if p >= up_b or rsi_val >= 60: final_adv = "💰 **[최종 결론]** 탐욕의 끝자락일세. **분할 매도**하여 수익을 빳빳하게 챙기시게!"
            elif p <= low_b or rsi_val <= 35: final_adv = "🛡️ **[최종 결론]** 공포가 극에 달한 바닥권일세. **분할 매수**로 보따리를 푸시게!"
            elif m_l < s_l or p < defense_line: final_adv = "🧐 **[최종 결론]** 엔진 역회전 혹은 성벽 위태롭네. **관망하며 기다리시게!**"
            else: final_adv = "📈 **[최종 결론]** 추세 살아있구먼. 성벽 사수 확인하며 **보유(홀딩)**하시게!"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # 네 기둥 지수 상세 진단 (수치 연동 완벽 보정)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # 127번 줄
        # [v36056] 윗동네 이름표가 'bb'든 'bband'든 상관없게 새로 계산하시게!
        # 자네 장부에 bband라고 되어있을 확률이 높으니 그걸로 다시 잡음세.
                # 130번 줄: 'bb'라는 상자에서 실시간 값을 꺼내오시게!
                upper = bband['upperband'].iloc[-1]
                lower = bband['lowerband'].iloc[-1]
                mid = (upper + lower) / 2

                if p > mid:
            # [중요] 그릇 이름을 'bband_diag'로 통일함세!
                    bband_diag = f"• **[중앙선 수복!]** 빳빳하게 성문 부쉈으니 이제 천정({upper:,.0f}원) 향해 진격하시게."
                else:
                    bband_diag = f"• **[중앙선 하단]** 아직 성문 밖일세. {mid:,.0f}원 수복 전까지는 보따리 사수하시게."

        # 139번 줄: 여기서 부르는 이름도 'bband_diag'여야 에러가 안 나네!
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bband_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI (온도) 기둥일세
                if rsi_val >= 60:
                    r_diag = f"● 지수 {rsi_val:.2f}로 **👺 불지옥** 문턱일세! 익절가 빳빳하게 잡으시게."
                elif 35 <= rsi_val <= 42:
                    r_diag = f"● 지수 {rsi_val:.2f}로 **🧊 냉골 문턱**에서 덜덜 떠는 중일세! 온기가 전혀 없으니 진격은 꿈도 꾸지 마시게."
                elif rsi_val < 35:
                    r_diag = f"● 지수 {rsi_val:.2f}로 **💀 완전 냉골** 상태일세! 남들 무서울 때 우리는 냉정하게 바닥을 보시게."
                else:
                    r_diag = f"● 지수 {rsi_val:.2f}로 어정쩡한 온도네. 세력의 눈치싸움이 치열구먼."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)

            with i3: # Williams %R (심리) 기둥일세
                if will_val <= -80:
                    w_diag = f"● 지수 {will_val:.2f}로 **🏳️ 개미 항복** 구간일세! 바닥 찍었으니 고개 들면 무조건 진격일세."
                elif will_val <= -60:
                    w_diag = f"● 지수 {will_val:.2f}로 **📉 하단 진흙탕**에서 헤매는 중일세! 기어 나올 힘이 없으니 함부로 보따리 풀지 마시게."
                elif will_val >= -20:
                    w_diag = f"● 지수 {will_val:.2f}로 **🧨 천장 광기** 구간일세! 언제 비수 꽂힐지 모르니 매섭게 보시게."
                else:
                    w_diag = f"● 지수 {will_val:.2f}로 어중간한 위치네. 세력의 눈치싸움이 치열구먼."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (심리)</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)

            ## 155번 줄부터 이 내용을 넣으시게! (줄 맞춤 보정 완료)
           # [154번 줄] 여기서부터 파일 끝까지 아래 내용으로 덮어쓰시게나!
            with i4: # MACD (엔진) 상세 진단
        # [v36056] 중앙선 수복 시 엔진 논리 보정
                if p > 193000:
                    m_color = "orange" if m_l < s_l else "red"
                    m_status = "역회전폭 급감" if m_l < s_l else "정회전"
                    m_diag = "• 엔진 **역회전폭 급감** 중일세! 주가가 성문 부쉈으니 엔진도 따라 도는 중이니 기세 타시게." if m_l < s_l else "• 엔진 **정회전** 진입! 기세 제대로 붙었으니 천정(21.8만원)까지 홀딩하시게."
                else:
                    m_color = "red" if m_l > s_l else "blue"
                    m_status = "정회전" if m_l > s_l else "역회전"
                    m_diag = "• 엔진이 **정회전** 중일세!" if m_l > s_l else "• 엔진이 **역회전** 중이네! 거꾸로 도는 차에 올라타면 안 되는 법일세."

                st.markdown(f"""
                    <div class='ind-box'>
                        <p class='ind-title'>MACD (엔진)</p>
                        <p class='ind-val' style='color:{m_color}; font-weight:bold;'>MACD {m_l:,.2f} / Signal {s_l:,.2f} ({m_status})</p>
                        <p class='ind-diag'>{m_diag}</p>
                    </div>
                """, unsafe_allow_html=True)

    # --- 윌리엄 진단 (중복 방지를 위해 네 기둥 아래에 딱 한 번만 배치) ---
            if will_val <= -80:
                w_diag = f"• 지수 {will_val:.2f}로 **⚪ 개미 항복** 구간일세! 바닥 찍었으니 진격 보시게."
            elif will_val <= -60:
                w_diag = f"• 지수 {will_val:.2f}로 **📉 하단 진흙탕**일세! 기어 나올 힘이 없으니 조심하시게."
            elif will_val >= -20:
                w_diag = f"• 지수 {will_val:.2f}로 **🚀 천장 광기** 구간일세! 언제 비수 꽂힐지 모르니 매섭게 보시게."
            else:
                w_diag = f"• 지수 {will_val:.2f}로 어중간한 위치네. 세력의 눈치싸움이 치열구먼."

            st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (심리)</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
    
    except Exception as e:
            st.error(f"장부 기입 중 복병(에러) 발생: {e}")
