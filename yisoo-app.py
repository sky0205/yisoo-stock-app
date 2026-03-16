import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (모바일 최적화 및 신고가 대응 로직 보강)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .header-container { background-color: #0D47A1; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #1565C0; }
    .main-title { font-size: 24px !important; color: #FFFFFF !important; margin: 0; }
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2px solid #455A64; margin-bottom: 20px; }
    .global-header { font-size: 20px !important; color: #81D4FA !important; border-bottom: 1px solid #546E7A; padding-bottom: 8px; margin-bottom: 12px; }
    .global-item-text { font-size: 15px !important; margin-bottom: 5px; }
    .global-item-label { color: #B0BEC5 !important; }
    .volume-box-unified { background-color: #E3F2FD; padding: 20px; border-radius: 12px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .unified-strategy-box { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 4px solid #D32F2F; margin: 15px 0; }
    .strategy-title { font-size: 20px !important; color: #D32F2F !important; border-bottom: 2px solid #FFEBEE; padding-bottom: 8px; margin-bottom: 12px; }
    .diagnosis-content { font-size: 16px !important; color: #B71C1C !important; line-height: 1.6; background-color: #FFF8F1; padding: 15px; border-radius: 8px; border-left: 8px solid #D32F2F; margin-bottom: 12px; }
    .price-wall-container { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 3px solid #1E88E5; margin-bottom: 20px; }
    .price-card { background-color: #F8F9FA; padding: 12px; border-radius: 10px; border: 1.5px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 10px; }
    .ind-title { font-size: 18px !important; color: #1976D2 !important; border-bottom: 1px solid #EEEEEE; padding-bottom: 8px; margin-bottom: 10px; }
    .ind-value { font-size: 38px !important; color: #B71C1C !important; text-align: center; display: block; margin: 8px 0; }
    .ind-diag { font-size: 14px !important; color: #333333 !important; line-height: 1.7; background-color: #FDFDFD; padding: 12px; border-radius: 5px; border-left: 6px solid #D32F2F; }
    .stock-header { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 8px solid #1E88E5; margin-bottom: 15px; }
    .val-main { font-size: 24px !important; color: #D32F2F !important; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-container'><p class='main-title'>👴 이수할아버지 냉정 진단기 v36056</p></div>", unsafe_allow_html=True)

# 0. 글로벌 전황 보고
def get_global_data(ticker):
    try:
        g_df = yf.download(ticker, period="5d", progress=False)
        if not g_df.empty:
            curr, prev = g_df['Close'].iloc[-1].item(), g_df['Close'].iloc[-2].item()
            return f"{curr:,.2f}", ((curr - prev) / prev) * 100
        return "장부 지연", 0
    except: return "통신 오류", 0

n_v, n_p = get_global_data("^IXIC"); s_v, s_p = get_global_data("^GSPC"); t_v, t_p = get_global_data("^TNX")

st.markdown(f"""
    <div class='global-unified-box'>
        <div class='global-header'>🌎 0. 글로벌 전황 통합 보고</div>
        <div class='global-item-container'>
            <div class='global-item'><span class='global-item-label'>나스닥(NASDAQ)</span><span class='global-item-val' style='color:{"#EF5350" if n_p > 0 else "#42A5F5"};'>{n_v} ({n_p:+.2f}%)</span></div>
            <div class='global-item'><span class='global-item-label'>S&P 500</span><span class='global-item-val' style='color:{"#EF5350" if s_p > 0 else "#42A5F5"};'>{s_v} ({s_p:+.2f}%)</span></div>
            <div class='global-item'><span class='global-item-label'>미국채 10년 금리</span><span class='global-item-val' style='color:{"#EF5350" if t_p > 0 else "#42A5F5"};'>{t_v} ({t_p:+.2f}%)</span></div>
        </div>
        <hr style='border:1px dashed #546E7A; margin: 15px 0;'>
        <div style='font-size:16px; color:#CFD8DC; line-height:1.6;'>
            <b>👴 냉정 평가:</b> 미장 지수는 거품 위 줄타기 중이고 국채 금리는 언제든 비수가 될 수 있네. 국장은 사지가 마비된 형국이니 섣부른 낙관은 금물이야.
        </div>
    </div>
    """, unsafe_allow_html=True)

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "006660") # 하이닉스 기본 예시

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365)
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency, fmt, diff_fmt = "원", ",.0f", "+,.0f" 
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol); currency, fmt, diff_fmt = "$", ",.2f", "+,.2f"
        
        if not df.empty:
            p, prev_p = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2]); diff = p - prev_p; pct_chg = (diff/prev_p)*100
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line, up_b, low_b = df['MA20'].iloc[-1], df['MA20'].iloc[-1] + (df['Std'].iloc[-1] * 2), df['MA20'].iloc[-1] - (df['Std'].iloc[-1] * 2)
            
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
            h14, l14 = df['High'].rolling(window=14).max().iloc[-1], df['Low'].rolling(window=14).min().iloc[-1]
            will_val = (h14 - p) / (h14 - l14) * -100 if (h14 - l14) != 0 else 0
            m_l = df['Close'].ewm(span=12, adjust=False).mean().iloc[-1] - df['Close'].ewm(span=26, adjust=False).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()).ewm(span=9, adjust=False).mean().iloc[-1]
            peak_p = float(df['Close'].iloc[-60:].max()); defense_line = peak_p * 0.93

            st.markdown(f"<div class='stock-header'><p style='font-size:20px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:26px; color:{'#D32F2F' if diff > 0 else '#1976D2'}; margin:0;'>{format(p, fmt)} {currency} <span style='font-size:16px;'>({format(diff, diff_fmt)}, {pct_chg:+.2f}%)</span></p></div>", unsafe_allow_html=True)

            buy_score = sum([p <= low_b * 1.03, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b * 0.97, rsi_val >= 65, will_val >= -25])
            sig, color = ("🔴 매수권 진입", "#D32F2F") if buy_score >= 2 else ("🟢 매도권 진입", "#388E3C") if sell_score >= 2 else ("🟡 관망 및 대기", "#FBC02D")
            st.markdown(f"<div style='padding:15px; border-radius:10px; text-align:center; background-color:{color}; margin-bottom:15px;'><span style='font-size:28px; color:white;'>{sig}</span></div>", unsafe_allow_html=True)

            # 1. 거래량 전황
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            if p > prev_p: v_advice = f"📈 <b>주포 진격:</b> {pct_chg:.1f}% 급등에 거래량까지 실렸네. 기세가 하늘을 찌르는구먼." if v_ratio > 150 else "🚨 <b>가짜 축제:</b> 거래량 없이 올린 함정일세."
            else: v_advice = "⚠️ <b>도살장 입구:</b> 거래량 실린 하락이야." if v_ratio > 150 else "📉 계단식 하락 중."
            st.markdown(f"<div class='volume-box-unified'><div style='font-size:20px; color:#0D47A1; margin-bottom:8px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:15px; line-height:1.6;'>{v_advice}</div></div>", unsafe_allow_html=True)

            # 2. 필살 전략 + 냉정 진단 (급등 및 신고가 대응 로직 강화)
            is_surge = pct_chg >= 5.0
            is_new_high = p >= peak_p * 0.98
            if is_new_high:
                diag_txt = f"축하하네! 주가가 성벽 상단을 부수고 {pct_chg:.1f}% 폭등하며 신고가 영역에 진입했구먼."
                strategy_txt = "<b>수익 극대화:</b> 상단선을 무시하고 기세를 즐기셔. 전일 고점을 생명선 삼아 수익을 끝까지 끌고 가되, 새로 타는 건 독약을 마시는 것이네."
            elif is_surge:
                diag_txt = f"오늘 {pct_chg:.1f}% 급등하며 하락 추세를 단번에 돌파했네. 장부가 오랜만에 기침을 멈췄구먼."
                strategy_txt = "<b>추세 전환 확인:</b> 거래량이 실린 급등이니 눌림목에서 공략을 준비하셔. 섣부른 추격보다는 성벽 안착을 먼저 확인하게나."
            else:
                diag_txt = f"현재 주가는 {format(p, fmt)}원에서 방향을 못 잡고 미지적대고 있구먼."
                strategy_txt = "<b>함정 수사 대기:</b> 가짜 반등에 속지 마셔. 지표가 완전히 식을 때까지 째려만 보게나."

            st.markdown(f"""
                <div class='unified-strategy-box'>
                    <div class='strategy-title'>⚔️ 2. 필살 대응 전략 및 냉정 진단</div>
                    <div class='diagnosis-content'><b>⚠️ [냉정 진단]:</b> {diag_txt} RSI <b>{rsi_val:.1f}</b>는 시장 열기를 말해주네.</div>
                    <div style='font-size:16px; color:#333; padding-left:10px;'>● <b>필살 대응 전략:</b> {strategy_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            # 3. 매수매도 성벽
            st.markdown("<div class='price-wall-container'><div style='font-size:18px; color:#1E88E5; margin-bottom:12px;'>🛡️ 3. 매수 매도 성벽 (Price Wall)</div>", unsafe_allow_html=True)
            cw1, cw2, cw3 = st.columns(3)
            target_high = "확장 중 (신고가)" if is_new_high else format(up_b, fmt)
            with cw1: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>⚖️ 공략(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with cw2: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🎯 수확(상단)</p><span class='val-main' style='color:#D32F2F;'>{target_high}</span></div>", unsafe_allow_html=True)
            with cw3: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🛡️ 성벽(93%)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 4. 네 기둥 지수 상세 진단 (종목 수치 맞춤형 강화)
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_msg = f"🚀 상단 성벽({format(up_b, fmt)})을 뚫었네. 광기가 끝날 때를 대비해 칼자루를 꽉 쥐셔." if p >= up_b * 0.98 else f"⚠️ 하단 성벽 근처일세." if p <= low_b * 1.02 else "⚖️ 성벽 사이 눈치싸움 중일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger (기세)</p><span style='font-size:13px; color:#546E7A;'>[중앙선 가격]</span><span class='ind-value'>{format(mid_line, fmt)}</span><div class='ind-diag'>● <b>종목 진단:</b> {bb_msg}<br><br><b>👴 훈수:</b> 볼린저는 기세의 너비일세. 하이닉스 같은 놈이 밴드를 뚫으면 그건 주포가 작정했다는 소리지.</div></div>", unsafe_allow_html=True)
            with i2: # RSI
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (온도)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{rsi_val:.1f}</span><div class='ind-diag'>● <b>종목 진단:</b> {'🔥 탐욕이 뜨겁네.' if rsi_val > 65 else '🧊 공포가 가득해.' if rsi_val < 35 else '🌡️ 미지근하네.'}<br><br><b>👴 훈수:</b> RSI 70 위는 과열이지만, 신고가 영역에선 이 숫자가 90까지도 버티니 익절선만 올리셔.</div></div>", unsafe_allow_html=True)
            with i3: # Williams
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams (심리)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{will_val:.1f}</span><div class='ind-diag'>● <b>종목 진단:</b> {'🧨 광기 폭발일세.' if will_val > -20 else '🏳️ 항복 지점이야.' if will_val < -80 else '⏳ 중간 지대일세.'}<br><br><b>👴 훈수:</b> 윌리엄이 상단에 붙어있다면 지금은 주포의 세상이지. 개미들은 그저 구경만 해야 할 때야.</div></div>", unsafe_allow_html=True)
            with i4: # MACD
                if m_l > 0 and m_l > s_l: m_msg = f"🚀 엔진 {m_l:.2f}, 수면 위 가속 중."
                elif m_l > 0 and m_l <= s_l: m_msg = f"⚠️ 엔진 {m_l:.2f}, 꺾였어 조심해."
                else: m_msg = f"💣 엔진 {m_l:.2f}, 역회전 혹은 침몰 중."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (추세)</p><span style='font-size:13px; color:#546E7A;'>[MACD 수치]</span><span class='ind-value' style='font-size:30px !important;'>{m_l:.2f}</span><div class='ind-diag'>● <b>종목 진단:</b> {m_msg}<br><br><b>👴 훈수:</b> {name}의 엔진이 드디어 힘을 내는구먼. 0 위에서 엔진이 고개를 들면 그때가 진짜 진격의 시간일세.</div></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부 오류: {e}")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 급등 대응 강화본")
