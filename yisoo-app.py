import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (어르신 맞춤형 최종 UI 고정)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .header-container { background-color: #0D47A1; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #1565C0; }
    .main-title { font-size: 24px !important; color: #FFFFFF !important; margin: 0; }
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2px solid #455A64; margin-bottom: 20px; }
    .global-header { font-size: 20px !important; color: #81D4FA !important; border-bottom: 1px solid #546E7A; padding-bottom: 8px; margin-bottom: 12px; }
    .global-item-container { display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; }
    .global-item-label { font-size: 14px !important; color: #B0BEC5 !important; display: block; margin-bottom: 5px; }
    .global-item-val { font-size: 17px !important; }
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
            <b>👴 냉정 평가:</b> 미장 지수는 거품 위 줄타기 중이고 국채 금리는 언제든 비수가 될 수 있네. 국장은 사지가 마비된 형국일세. 섣부른 낙관은 금물이야.
        </div>
    </div>
    """, unsafe_allow_html=True)

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "006660")

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
            if p > prev_p: v_advice = f"📈 <b>주포 진격:</b> {pct_chg:.1f}% 급등에 거래량까지 실렸네." if v_ratio > 100 else "🚨 <b>가짜 축제:</b> 거래량 없이 올린 함정일세. 모래성 위의 성벽이야."
            else: v_advice = "⚠️ <b>도살장 입구:</b> 거래량 터진 하락이야." if v_ratio > 150 else "📉 계단식 하락 중."
            st.markdown(f"<div class='volume-box-unified'><div style='font-size:20px; color:#0D47A1; margin-bottom:8px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:15px; line-height:1.6;'>{v_advice}</div></div>", unsafe_allow_html=True)

            # 2. 필살 전략 + 냉정 진단 (거래량-가격 정밀 판독 보완)
            is_surge = pct_chg >= 5.0; is_new_high = p >= peak_p * 0.98
            if is_new_high:
                if v_ratio > 100:
                    diag_txt = f"성벽 상단을 부수고 {pct_chg:.1f}% 폭등하며 신고가 영역일세. 주포가 작정하고 문을 연 것이야."
                    strategy_txt = "<b>수익 극대화:</b> 상단선 무시하고 기세를 즐기셔. 전일 고점을 생명선 삼고 끝까지 끌고 가셔."
                else:
                    diag_txt = f"신고가 근처까지 {pct_chg:.1f}% 올랐으나 거래량이 {v_ratio:.1f}%로 너무 빈약하구먼. 주포들이 개미들 꼬시려고 성문만 열어둔 격일세."
                    strategy_txt = "<b>가짜 돌파 경계:</b> 속지 마시게. 거래량이 뒷받침 안 되는 신고가는 언제든 무너질 함정이니 섣불리 진격하지 마셔."
            elif is_surge:
                if v_ratio > 100:
                    diag_txt = f"오늘 {pct_chg:.1f}% 급등하며 하락 추세를 돌파했네. 거래량까지 실려 장부가 생기를 되찾았구먼."
                    strategy_txt = "<b>추세 전환 확인:</b> 거래량 실린 급등이니 눌림목 공략을 준비하셔. 성벽 안착을 먼저 보게나."
                else:
                    diag_txt = f"가격은 {pct_chg:.1f}%나 올랐으나 거래량이 {v_ratio:.1f}%로 형편없구먼. 이건 빈 수레가 요란한 격일세."
                    strategy_txt = "<b>함정 수사 대기:</b> 거래량 없는 급등은 데드 캣 바운스일 뿐이야. 속지 말고 수급이 붙을 때까지 독하게 기다리셔."
            elif p <= low_b * 1.03:
                diag_txt = f"현재 주가는 하단 성벽({format(low_b, fmt)})에 바짝 붙어 투매 비명이 들리는 판국일세."
                strategy_txt = "<b>하단 성벽 사수:</b> 개미 투항까지 독하게 기다리시게. 심해를 뚫을 때가 기회일세."
            else:
                diag_txt = f"성벽 사이에서 방향을 못 잡고 미지적대고 있구먼. RSI {rsi_val:.1f}는 시장의 눈치싸움을 말해주네."
                strategy_txt = "<b>관망 유지:</b> 지표가 완전히 식을 때까지 째려만 보게나."

            st.markdown(f"""
                <div class='unified-strategy-box'>
                    <div class='strategy-title'>⚔️ 2. 필살 대응 전략 및 냉정 진단</div>
                    <div class='diagnosis-content'><b>⚠️ [냉정 진단]:</b> {diag_txt}</div>
                    <div style='font-size:16px; color:#333; padding-left:10px;'>● <b>필살 대응 전략:</b> {strategy_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            # 3. 매수매도 성벽
            st.markdown("<div class='price-wall-container'><div style='font-size:18px; color:#1E88E5; margin-bottom:12px;'>🛡️ 3. 매수 매도 성벽 (Price Wall)</div>", unsafe_allow_html=True)
            cw1, cw2, cw3 = st.columns(3)
            target_high = "확장 중 (신고가)" if is_new_high and v_ratio > 100 else format(up_b, fmt)
            with cw1: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>⚖️ 공략(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with cw2: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🎯 수확(상단)</p><span class='val-main' style='color:#D32F2F;'>{target_high}</span></div>", unsafe_allow_html=True)
            with cw3: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🛡️ 성벽(93%)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 4. 네 기둥 지수 상세 진단 (로직 고정)
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_msg = f"🚀 상단 성벽({format(up_b, fmt)}) 돌파 중." if p >= up_b * 0.98 else f"⚠️ 하단 성벽 근처일세." if p <= low_b * 1.02 else "⚖️ 성벽 사이 눈치싸움 중."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger (기세)</p><span style='font-size:13px; color:#546E7A;'>[중앙선 가격]</span><span class='ind-value'>{format(mid_line, fmt)}</span><div class='ind-diag'>● <b>종목 진단:</b> {bb_msg}<br><br><b>👴 훈수:</b> 밴드를 뚫으면 주포가 작정했다는 소리네. 성벽 사수를 독하게 보셔.</div></div>", unsafe_allow_html=True)
            with i2: # RSI
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (온도)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{rsi_val:.1f}</span><div class='ind-diag'>● <b>종목 진단:</b> {'🔥 탐욕이 뜨겁네.' if rsi_val > 65 else '🧊 공포가 가득해.' if rsi_val < 35 else '🌡️ 미지근하네.'}<br><br><b>👴 훈수:</b> 70 위는 과열이지만 기세가 등등할 땐 함부로 내리지 마셔. 30까지 독하게 참으셔.</div></div>", unsafe_allow_html=True)
            with i3: # Williams
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams (심리)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{will_val:.1f}</span><div class='ind-diag'>● <b>종목 진단:</b> {'🧨 광기 폭발일세.' if will_val > -20 else '🏳️ 항복 지점이야.' if will_val < -80 else '⏳ 중간 지대일세.'}<br><br><b>👴 훈수:</b> 윌리엄은 바닥 귀신일세. -80 아래 심해 잠수 때가 진짜 기회라는 걸 잊지 마셔.</div></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_msg = f"🚀 엔진 {m_l:.2f}, 가속 중." if m_l > s_l else f"💣 엔진 {m_l:.2f}, 역회전 중."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (추세)</p><span style='font-size:13px; color:#546E7A;'>[MACD 수치]</span><span class='ind-value' style='font-size:30px !important;'>{m_l:.2f}</span><div class='ind-diag'>● <b>종목 진단:</b> {m_msg}<br><br><b>👴 훈수:</b> 0 위에서 엔진이 고개를 들면 그때가 진짜 진격의 시간이구먼. {name}의 엔진 상태를 믿으셔.</div></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부 오류: {e}")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 확정본 (Locked)")
