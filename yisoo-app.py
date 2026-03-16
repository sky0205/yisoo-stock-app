import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 할배 캐릭터 스타일 (제목-내용 완전 결합 레이아웃)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    /* [진짜 핵심 수선] 제목 지붕과 내용을 완전히 하나로 가두는 통합 섹션 박스 */
    .unified-box {
        background-color: #FFFFFF;
        border-radius: 15px;
        border: 5px solid #CFD8DC;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 35px;
        overflow: hidden; /* 제목 배경이 박스 테두리에 딱 맞게 절단 */
        padding: 0 !important;
    }
    .unified-header {
        background-color: #1565C0;
        color: #FFFFFF !important;
        padding: 20px 25px;
        font-size: 38px !important;
        border-bottom: 5px solid #0D47A1;
        margin: 0 !important;
        display: block;
    }
    .unified-content {
        padding: 35px 25px;
        margin: 0 !important;
    }
    
    /* 주가 헤더 스타일 */
    .stock-header { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border-left: 15px solid #1E88E5; margin-bottom: 25px; }
    .price-main { font-size: 55px !important; color: #D32F2F !important; line-height: 1.1; }
    
    /* 거래량 상세 훈수 스타일 */
    .vol-main-text { font-size: 42px !important; color: #0D47A1 !important; margin-bottom: 15px; }
    .vol-sub-text { font-size: 30px !important; color: #1565C0 !important; line-height: 1.7; background-color: #F9F9F9; padding: 22px; border-radius: 10px; border-left: 12px solid #1E88E5; }
    
    /* 신호등 및 대응 전략 */
    .signal-box { padding: 45px; border-radius: 25px; text-align: center; margin-bottom: 30px; }
    .signal-text { font-size: 90px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    
    .trend-card { background-color: #FFFFFF; padding: 40px; border-radius: 25px; border: 12px solid #D32F2F; margin: 25px 0; }
    .trend-title { font-size: 45px !important; color: #D32F2F !important; border-bottom: 6px solid #FFEBEE; padding-bottom: 15px; margin-bottom: 30px; }
    .trend-item { font-size: 32px !important; line-height: 1.8; margin-bottom: 20px; }
    
    /* 지수 훈수 박스 상세 스타일 */
    .ind-box { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #90A4AE; min-height: 580px; margin-bottom: 25px; }
    .ind-title { font-size: 38px !important; color: #1976D2 !important; border-bottom: 5px solid #EEEEEE; padding-bottom: 15px; margin-bottom: 25px; }
    .ind-diag { font-size: 32px !important; color: #333333 !important; line-height: 1.8; background-color: #FAFAFA; padding: 25px; border-radius: 12px; border-left: 15px solid #D32F2F; }
    
    /* 대왕 글씨 metric 수치 대폭 강화 */
    [data-testid="stMetricValue"] { font-size: 65px !important; font-weight: 900 !important; color: #212121 !important; }
    [data-testid="stMetricLabel"] { font-size: 32px !important; color: #546E7A !important; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 전황: 제목 지붕 아래 내용을 완벽히 가두었음
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        
        st.markdown(f"""<div class='unified-box'>
            <div class='unified-header'>🌍 글로벌 시장 종합 전황</div>
            <div class='unified-content'>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년", f"{tnx.last_price:.2f}%", f"{(tnx.last_price/tnx.previous_close-1)*100:+.2f}%")
        advice = "✅ **[미장 쾌청: 진격!]**" if n_chg > 0.5 else "🚨 **[긴급 상황: 정박!]**" if n_chg < -1.0 else "🧐 **[안개 정국: 관망]**"
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice} 지표 끝단을 기다리시게.")
        st.markdown("</div></div>", unsafe_allow_html=True)
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "Nvda")

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

            # 기술 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p class='price-main'>{format(p, fmt_p)} {currency} <span style='font-size:38px;'>({p_chg:+.2f}%)</span></p></div>", unsafe_allow_html=True)
            
            # 거래량 분석: 제목 지붕 아래 내용을 완벽히 가두었음
            st.markdown(f"""<div class='unified-box'>
                <div class='unified-header'>📊 실시간 거래량 전황 분석</div>
                <div class='unified-content'>""", unsafe_allow_html=True)
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가"
            if v_ratio >= 30 and is_opening:
                v_status = f"🔥 시초 거래폭발 ({v_ratio:.1f}%)"
                v_adv = f"🔥 **[세력 진격!]** 거래량이 5일 평균 대비 {v_ratio:.1f}% 터지며 폭등 중일세! 진짜 세력이 미는 거니 빳빳하게 기세 타시게!" if p_chg >= 3 else f"💀 **[비명 포착!]** 거래량이 {v_ratio:.1f}% 터지며 폭락 중일세! 성벽 함락 중이니 일단 피신하시게!"
            else:
                v_status = f"{v_label} ({v_ratio:.1f}%)"
                v_adv = f"🚨 **[가짜 상승 주의!]** 주가는 올랐는데 거래량은 {v_ratio:.1f}%로 빈 수레일세! 개미 꼬드기는 격이니 속지 마시게." if p_chg > 3 and v_ratio < 100 else f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-main-text'>{v_status}</div><div class='vol-sub-text'>{v_adv}</div>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"● {'👺 불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 겁먹지 말고 보따리를 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:42px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # 성벽 가격선: 제목 지붕 아래 내용을 완벽히 가두었음
            st.markdown(f"""<div class='unified-box'>
                <div class='unified-header'>🛡️ 매수·매도 핵심 성벽 가격선</div>
                <div class='unified-content'>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("⚖️ 공략 대기선", format(low_b, fmt_p))
            with c2: st.metric("🎯 수확 목표선", format(up_b, fmt_p))
            with c3: st.metric("🛡️ 성벽(방어선)", format(defense_line, fmt_p))
            st.markdown("</div></div>", unsafe_allow_html=True)

            # [복구 완벽] 필살 대응 전략 및 최종 결론
            adv1 = f"1. **진격 금지:** RSI {rsi_val:.1f}로 아직 60 안 뚫었네." if rsi_val < 60 else "1. **기세 타기:** RSI 60 돌파!"
            adv2 = f"2. **성벽 사수:** 성벽({format(defense_line, fmt_p)}) {'함락됐으니 지하실 조심하시게.' if p < defense_line else '사수 중이니 진격의 발판 삼으시게.'}"
            adv3 = f"3. **엔진 확인:** 엔진이 {'정회전 중일세!' if m_l > s_l else '**역회전 중!** 절대 속지 마시게.'}"
            if p >= up_b or rsi_val >= 60: final = "💰 **[최종 결론] 분할 매도하여 수익을 빳빳하게 챙기시게!**"
            elif p <= low_b or rsi_val <= 35: final = "🛡️ **[최종 결론] 분할 매수로 보따리를 푸시게!**"
            elif m_l < s_l or p < defense_line: final = "🧐 **[최종 결론] 엔진 역회전 혹은 성벽 위태롭네. 관망하시게!**"
            else: final = "📈 **[최종 결론] 추세 살아있구먼. 성벽 사수 확인하며 보유하시게!**"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:2px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:42px !important;'>{final}</div></div>""", unsafe_allow_html=True)

            # [복구 완벽] 4대 지수 상세 분석 (비수 꽂는 매서운 훈수)
            st.divider()
            i1, i2 = st.columns(2); i3, i4 = st.columns(2)
            with i1: # Bollinger
                bb_diag = f"● **[비상: 상단 돌파!]** 하늘 찌르는구먼! 탐욕 버리고 익절 준비 하시게." if p >= up_b else f"● **[비상: 하단 돌파!]** 바닥권일세! 지지받고 고개 들면 진짜 진격 기회일세." if p <= low_b else f"● 중앙선 아래일세. 성벽 사수 확인 전까지는 기다리시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                r_diag = f"● 지수 {rsi_val:.2f}로 **👺 불지옥** 문턱일세! 익절가 빳빳하게 잡으시게." if rsi_val >= 60 else f"● 지수 {rsi_val:.2f}로 **🧊 냉골** 상태일세! 냉정하게 바닥을 보시게." if rsi_val <= 35 else f"● 탐욕과 공포 사이 중립 기어일세. 지표 끝단을 기다리시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:65px; color:#E65100;'>{rsi_val:.1f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                w_diag = f"● 지수 {will_val:.2f}로 **🏳️ 개미 항복** 구간! 보따리 푸시게. 여기서 고개 들면 무조건 진격일세!" if will_val < -80 else f"● 지수 {will_val:.2f}로 **🧨 천장 광기** 구간! 매섭게 보시게." if will_val > -20 else f"● 현재 중간지대일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:65px; color:#E65100;'>{will_val:.1f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diag = "● 엔진이 정회전 중일세! 기세 붙었으니 성벽 사수 보시게." if m_l > s_l else f"● 엔진이 **역회전** 중이네! 거꾸로 도는 차에 올라타면 안 되네. 절대 속지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
