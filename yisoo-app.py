import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup

# --- [보급로 최적화 캐싱 장치] ---
@st.cache_data(ttl=3600)
def load_krx_listing():
    try: return fdr.StockListing('KRX')
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_global_market():
    nasdaq = yf.Ticker("^IXIC").fast_info
    sp500 = yf.Ticker("^GSPC").fast_info
    tnx = yf.Ticker("^TNX").fast_info
    return {
        "n_last": nasdaq.last_price, "n_prev": nasdaq.previous_close,
        "s_last": sp500.last_price, "s_prev": sp500.previous_close,
        "t_last": tnx.last_price, "t_prev": tnx.previous_close
    }

# 1. 스타일 설정 (기존 유지)
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

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); is_kr = symbol.isdigit()
        now_tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
        now_local = datetime.now(now_tz)

        if is_kr:
            ticker = yf.Ticker(f"{symbol}.KS")
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            df_krx = load_krx_listing()
            name = df_krx[df_krx['Code'] == symbol]['Name'].values[0] if not df_krx.empty else symbol
            currency, fmt_p = "원", ",.0f"
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
            v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            prev_p = float(df['Close'].iloc[-1])
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol); currency, fmt_p = "$", ",.2f"
            df_today = ticker.history(period='1d')
            p = float(df_today['Close'].iloc[-1]); v_curr = float(df_today['Volume'].iloc[-1]); prev_p = float(df['Close'].iloc[-1])

        if not df.empty:
            df = df.ffill().dropna()
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            p_diff, p_chg = p - prev_p, (p - prev_p) / prev_p * 100

            # 시간 보정 로직
            s_h, s_m = (9, 0) if is_kr else (9, 30)
            m_start = now_local.replace(hour=s_h, minute=s_m, second=0, microsecond=0)
            if now_local < m_start: vol_strength = v_ratio 
            else:
                elapsed = min(390, max(10, (now_local - m_start).seconds / 60))
                if now_local.weekday() >= 5: elapsed = 390
                vol_strength = min(1000, v_ratio / (elapsed / 390))

            # 지표 계산
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
            defense_line = float(df['High'].iloc[-21:-1].max()) * 0.93

            # 전광판 출력
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

            # 거래량 박스
            if vol_strength >= 150: v_status, v_adv = "과열폭발", f"🔥 **[화력폭발]** 현재 강도 {vol_strength:.1f}점! 본진 진격 중이오."
            elif vol_strength >= 100: v_status, v_adv = "매집시작", f"🚀 **[매집시작]** 현재 강도 {vol_strength:.1f}점! 화력이 차오르네."
            elif vol_strength >= 80: v_status, v_adv = "정상화력", f"⚔️ **[정상화력]** 현재 강도 {vol_strength:.1f}점! 기세가 빳빳하구먼."
            else: v_status, v_adv = "기세부족", f"🧊 **[거래절벽]** 현재 강도 {vol_strength:.1f}점! 속지 마시게."
            
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status} ({v_ratio:.1f}% / 5일평균대비)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"● {'👺 불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 60 else '과열권일세! 수익 챙기시게.'}"
            elif p <= (low_b * 1.005) or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 겁먹지 말고 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # 가격 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 (냉정 로직)
            if p >= up_b or rsi_val >= 60:
                if m_l < s_l: final_adv = f"🚨 **[최종 결론]** 강도({vol_strength:.1f}점). 성벽 함락 및 엔진 역회전! **무조건 퇴각 및 현금 확보!**"
                else: final_adv = f"🚀 **[최종 결론]** 강도({vol_strength:.1f}점). 성벽 사수 중이나 과열권일세. **분할 매도 준비!**"
            elif p <= (low_b * 1.02):
                if m_l < s_l: final_adv = f"💀 **[최종 결론]** 강도({vol_strength:.1f}점). 엔진 역회전 중이니 **절대 매수 금지! 지하실 조심!**"
                else: final_adv = f"🔥 **[최종 결론]** 강도({vol_strength:.1f}점). 바닥에 물량 실리고 엔진 정회전! **매수 검토하시게.**"
            else: final_adv = f"🧐 **[최종 결론]** 강도({vol_strength:.1f}점). 중립 지대일세. **관망하며 지표 끝단을 기다리시게.**"

            st.markdown(f"<div class='trend-card'><div class='trend-title'>⚔️ 실전 필살 대응 전략</div><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>", unsafe_allow_html=True)

            # --- [수선: 4대 지표 정밀 진단 복원] ---
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                if p >= up_b: bb_diag = "👺 **[천장 돌파]** 울타리 밖으로 기세 폭발! 탐욕의 끝단이니 익절하시게."
                elif p <= low_b: bb_diag = "🧊 **[바닥 돌파]** 지하실까지 밀렸구먼. 엔진 시동을 기다리시게."
                elif p >= mid_line: bb_diag = "⚠️ **[과열 진입]** 중앙선 위에서 기세 유지 중이나 온도가 높네."
                else: bb_diag = "🏠 **[기세 둔화]** 중앙선 밑일세. 온도가 낮아도 절대 칼 뽑지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                is_div = p > prev_p and rsi_val < rsi_prev
                if rsi_val >= 60: r_diag = f"● 지수 {rsi_val:.2f}로 **👺 불지옥** 문턱! {'🚨 가짜 상승이니 대피하시게.' if is_div else '수익 챙길 채비 하시게.'}"
                elif rsi_val <= 35: r_diag = f"● 지수 {rsi_val:.2f}로 **🧊 냉골** 바닥! 냉정하게 보따리 푸시게."
                else: r_diag = f"● 지수 {rsi_val:.2f}로 중립일세. {'🚨 가짜 기세니 눈 부라리고 보시게.' if is_div else '끝단을 기다리시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                if will_val >= -20: w_diag = f"● 지수 {will_val:.2f}로 **🧨 천장 광기**! 비수 꽂히기 전에 수확하시게."
                elif will_val >= -35: w_diag = f"● 지수 {will_val:.2f}로 **⚠️ 천장 근접**! 고점 징후니 주시하시게."
                elif will_val <= -80: w_diag = f"● 지수 {will_val:.2f}로 **🏳️ 개미 항복**! 보따리 풀 준비 하시게."
                elif will_val <= -65: w_diag = f"● 지수 {will_val:.2f}로 **📉 하락 가속**! 절대 칼 뽑지 마시게."
                else: w_diag = f"● 지수 {will_val:.2f}로 중간 지대일세. 기세를 냉정하게 지켜보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
                if m_l > s_l: m_diag = "● 엔진 **정회전(헛바퀴)**! 성벽 무너졌으니 속지 마시게." if p < defense_line else "● 엔진 **정회전**! 성벽 사수하며 자신 있게 진격하시게."
                else: m_diag = "● 엔진 **역회전폭 급감**! 시동 걸 채비 중이니 진격 신호를 기다리시게." if m_diff_curr > m_diff_prev else "● 엔진 **역회전 심화**! 거꾸로 도는 차니 냉정하게 자숙하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
