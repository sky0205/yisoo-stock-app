import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 (v36056 스타일 및 할배 캐릭터 완벽 유지)
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
    .val-main { font-size: 32px !important; color: #333; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-status { font-size: 32px !important; color: #D32F2F !important; margin-bottom: 10px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지표 실시간 연동 (훈수 로직 강화)
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
        if n_chg > 0.5: advice = "✅ **[진격!]** 미장이 불을 뿜고 있구먼! 이 흐름 타시게."
        elif n_chg < -1.0: advice = "🚨 **[정박!]** 미장이 피를 흘리고 있네! 보따리 싸시게."
        else: advice = "🧐 **[관망]** 시초가 형성 중이니 눈을 부라리고 보시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "goog")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul')); currency = "원"; fmt_p = ",.0f"
            try:
                df = fdr.DataReader(symbol, start_date, end_date); stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            except:
                ticker = yf.Ticker(f"{symbol}.KS"); df = ticker.history(start=start_date, end=end_date); name = ticker.info.get('shortName', symbol)
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"; name = ticker.info.get('shortName', symbol)
        
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # 기술 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)} / {p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # [핵심 복구] 현지 시초장 판독 시에도 거래율(%) 수치 빳빳하게 표시
            v_status_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            
            if v_ratio >= 30 and is_opening: # 현지 시간 시초장 판독
                if p_chg >= 3:
                    v_status = f"🔥 현지 시초 주가폭등 / 거래폭발 ({v_ratio:.1f}%)"
                    v_adv = f"🔥 **[세력 진격!]** 시초 거래량이 5일 평균 대비 {v_ratio:.1f}% 터지며 주가 폭등 중일세! 빳빳하게 기세 타시게!"
                elif p_chg <= -3:
                    v_status = f"💀 현지 시초 주가폭락 / 거래폭발 ({v_ratio:.1f}%)"
                    v_adv = f"💀 **[비명 포착!]** 시초 거래량이 {v_ratio:.1f}% 터지며 폭락 중일세! 성벽 함락 중이니 일단 피신하시게!"
                else:
                    v_status = f"📈 현지 시초 거래급등 ({v_ratio:.1f}%)"
                    v_adv = f"✅ 거래량은 {v_ratio:.1f}%로 터졌는데 주가가 힘겨루기 중일세. 눈을 부라리고 보시게."
            else: # 일반 및 장마감 판독
                v_status = f"{v_status_label} ({v_ratio:.1f}%)"
                if p_chg > 3 and v_ratio < 100:
                    v_adv = f"🚨 **[가짜 상승 주의!]** 주가는 {p_chg:.2f}% 올랐는데 거래량은 {v_ratio:.1f}%로 빈 수레일세! 속지 마시게."
                else:
                    v_adv = f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등 및 성벽
            if p >= up_b or rsi_val >= 60: sig, col, adv = "🟢 매도권 진입", "#388E3C", f"● {'불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= low_b or rsi_val <= 35: sig, col, adv = "🔴 매수권 진입", "#D32F2F", "● 바닥권일세. 보따리 푸시게."
            else: sig, col, adv = "🟡 관망 및 대기", "#FBC02D", "● 대기하시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt_p)}) {'함락!' if p < defense_line else '사수 중.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span style='color:#D32F2F;'>{'수익 챙기시게!' if p >= up_b else '바닥 확인하고 진격하시게!'}</span></div></div>""", unsafe_allow_html=True)

            # 네 기둥 지수 상세 훈수 (완벽 유지)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                if p >= up_b: bb_diag = "● **[상단 돌파!]** 하늘 찌르는구먼! 탐욕 버리고 수확 준비 하시게."
                elif p <= low_b: bb_diag = "● **[하단 돌파!]** 바닥권일세! 지지받고 고개 들면 진격 기회일세."
                else: bb_diag = f"● 중앙선 {'위' if p > mid_line else '아래'}일세. 성벽 사수 확인하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                r_diag = f"● 지수 {rsi_val:.2f}로 **👺 불지옥** 문턱일세! 익절가 잡으시게." if rsi_val >= 60 else f"● 지수 {rsi_val:.2f}로 **🧊 냉골** 상태일세! 바닥 보시게." if rsi_val <= 35 else "● 눈치싸움 중일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                w_diag = "● **🏳️ 개미 항복** 구간! 진격 준비!" if will_val < -80 else "● **🧨 천장 광기** 구간! 매섭게 보시게." if will_val > -20 else "● 중간지대일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diag = "● 엔진 정회전 중!" if m_l > s_l else "● 엔진 **역회전** 중! 거꾸로 도는 차에 타지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
